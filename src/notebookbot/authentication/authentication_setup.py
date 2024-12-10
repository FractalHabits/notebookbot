import os
import sys
import getpass
from dataclasses import dataclass
from typing import Optional
import base64

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from notebookbot.authentication.authentication_manager import AuthenticationManager


@dataclass
class APIKeys:
    """Container for API keys."""
    openai: str
    anthropic: str

class AuthenticationSetup:
    _instance = None
    _api_keys = None  # Class variable to store API keys
    _is_authenticated = False  # Add static authentication state

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, env_file_path: str = '.env'):
        if not getattr(self, '_initialized', False):
            self.env_file_path = env_file_path
            self.auth_manager = None
            self._setup_env_file()
            self._initialized = True
        
    def _setup_env_file(self):
        """Ensure .env file exists and has required structure."""
        try:
            with open(self.env_file_path, 'a+') as f:
                f.seek(0)
                content = f.read()
                if 'SALT=' not in content:
                    # Generate 16 bytes of random data and ensure proper base64 padding
                    salt = base64.urlsafe_b64encode(os.urandom(16)).decode().rstrip('=')
                    f.write(f"SALT={salt}\n")
        except Exception as e:
            raise ValueError(f"Could not access {self.env_file_path}: {e}")

    def authenticate(self) -> bool:
        """Set up password or authenticate with existing one."""
        from notebookbot.authentication.authentication_manager import AuthenticationManager
        
        # If already authenticated, return True immediately
        if AuthenticationSetup._is_authenticated:
            return True

        # Check if keys already exist
        if self._keys_exist():
            print("Keys already exist. Skipping password setup.")
            self.auth_manager = AuthenticationManager(self.env_file_path)
            if self._try_authenticate(self.auth_manager):
                self._show_available_keys()
                AuthenticationSetup._is_authenticated = True  # Set authenticated state
                return True
            return False

        max_attempts = 3
        for attempt in range(max_attempts):
            password = getpass.getpass("Enter your password: ")
            confirm_password = getpass.getpass("Confirm your password: ")
            
            if password != confirm_password:
                remaining = max_attempts - (attempt + 1)
                if remaining > 0:
                    print(f"Passwords do not match! {remaining} attempts remaining.")
                    continue
                print("Maximum password attempts exceeded.")
                return False
                
            self.auth_manager = AuthenticationManager(self.env_file_path)
            if self._try_authenticate(self.auth_manager):
                self._show_available_keys()
                self._setup_keys()  # Add this line to set up keys if none exist
                AuthenticationSetup._is_authenticated = True  # Set authenticated state
                return True
        
        return False

    def _show_available_keys(self):
        """Display available API keys."""
        encryption_manager = self.auth_manager.api_interface.encryption_manager
        existing_keys = encryption_manager.list_keys()
        print("\nAvailable API keys:")
        if existing_keys:
            for key in sorted(existing_keys):
                print(f"- {key}")
        else:
            print("No API keys stored.")

    def get_api_keys(self) -> APIKeys:
        """Get decrypted API keys."""
        if not self.auth_manager or not self.auth_manager.is_authenticated:
            raise ValueError("Must authenticate first")
            
        encryption_manager = self.auth_manager.api_interface.encryption_manager
        
        # Get both API keys
        openai_key = encryption_manager.decrypt_key("OPENAI_API_KEY")
        anthropic_key = encryption_manager.decrypt_key("ANTHROPIC_API_KEY")
        
        if not openai_key or not anthropic_key:
            raise ValueError("Failed to decrypt API keys")
            
        return APIKeys(openai=openai_key, anthropic=anthropic_key)

    def _setup_keys(self):
        """Set up API keys interactively."""
        if not self.auth_manager or not self.auth_manager.is_authenticated:
            raise ValueError("Must authenticate first")
        
        if not hasattr(self.auth_manager, 'api_interface') or \
           not hasattr(self.auth_manager.api_interface, 'encryption_manager'):
            raise ValueError("Authentication manager not properly initialized")

        encryption_manager = self.auth_manager.api_interface.encryption_manager
        existing_keys = encryption_manager.list_keys()

        if not existing_keys:
            print("\nLet's set up your API keys.")
        else:
            print("\nYou already have the following API keys stored:")
            for key in sorted(existing_keys):
                print(f"- {key}")

        keys_to_setup = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        keys_to_setup = [key for key in keys_to_setup if key not in existing_keys]

        if keys_to_setup:
            print("\nLet's set up the remaining API keys.")
            for key_name in keys_to_setup:
                while True:
                    choice = input(f"Do you want to enter your {key_name}? (yes/no): ").strip().lower()
                    if choice in ('yes', 'y'):
                        api_key = getpass.getpass(f"Enter your {key_name}: ")
                        encryption_manager.encrypt_and_store_key(key_name, api_key)
                        print(f"{key_name} added successfully.")
                        break
                    if choice in ('no', 'n'):
                        break
                    print("Please enter 'yes' or 'no")
        else:
            print("\nAll API keys are already set up.")

        # Show final status
        print("\nSetup complete!")
        print("Available API keys:")
        existing_keys = encryption_manager.list_keys()
        if existing_keys:
            for key in sorted(existing_keys):
                print(f"- {key}")
        else:
            print("No API keys stored.")

    def _keys_exist(self) -> bool:
        """Check if API keys are already stored."""
        try:
            with open(self.env_file_path, 'r') as f:
                content = f.read()
                return 'OPENAI_API_KEY_ENCRYPTED=' in content and 'ANTHROPIC_API_KEY_ENCRYPTED=' in content
        except FileNotFoundError:
            return False

    def _try_authenticate(self, auth_manager, max_attempts=3):
        """Try to authenticate with multiple attempts."""
        attempts = 0
        while attempts < max_attempts:
            auth_manager.setup_or_authenticate()
            if auth_manager.is_authenticated:
                return True
            
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                print(f"Incorrect password. You have {remaining} {'attempts' if remaining > 1 else 'attempt'} remaining.")
    
        print("Maximum password attempts exceeded. Please try again later.")
        return False

# Keep existing functions for CLI usage
def try_authenticate(auth_manager, max_attempts=3):
    """Try to authenticate with multiple attempts."""
    attempts = 0
    while attempts < max_attempts:
        auth_manager.setup_or_authenticate()
        if auth_manager.is_authenticated:
            return True
            
        attempts += 1
        remaining = max_attempts - attempts
        if remaining > 0:
            print(f"Incorrect password. You have {remaining} {'attempts' if remaining > 1 else 'attempt'} remaining.")
    
    print("Maximum password attempts exceeded. Please try again later.")
    return False

def format_key_name(encrypted_key_name):
    """Convert encrypted filename back to original key name."""
    return encrypted_key_name.replace('.encrypted', '')


def get_api_key_choice(remaining_keys):
    """Present API key choices to user."""
    choices = {
        "1": "OPENAI_API_KEY",
        "2": "ANTHROPIC_API_KEY"
    }
    
    # Filter out keys that have already been entered
    available_choices = {k: v for k, v in choices.items() if v in remaining_keys}
    
    if not available_choices:
        return None
        
    prompt = "Do you want to enter "
    if len(available_choices) > 1:
        prompt += f"your {' or '.join(f'{v} ({k})' for k, v in available_choices.items())}? "
    else:
        k, v = next(iter(available_choices.items()))
        prompt += f"your {v} ({k})? (yes/no) "
    
    while True:
        choice = input(prompt).strip().lower()
        if choice in available_choices:
            return available_choices[choice]
        elif choice in ["openai", "open"]:
            return "OPENAI_API_KEY"
        elif choice in ["anthropic", "claude"]:
            return "ANTHROPIC_API_KEY"
        elif choice.lower() == "no":
            return None
        print("Invalid choice. Please try again.")


def get_existing_keys(auth_manager):
    """Get list of existing API keys."""
    try:
        return auth_manager.api_interface.encryption_manager.list_keys()
    except AttributeError:
        return set()


'''def main():
    setup = AuthenticationSetup()
    if setup.authenticate():
        setup._setup_keys()  # Call the _setup_keys method here

if __name__ == "__main__":
    main()
'''