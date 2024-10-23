import os
import getpass
from dotenv import load_dotenv
from typing import Union

from .api_key_interface import APIKeyInterface
from .secure_api_key_manager import SecureAPIKeyManager

class AuthenticationManager:
    """
    A manager class to handle initial password setup, authentication, and interface creation.
    """
    def __init__(self, env_file_path: str, min_length: int = 16, required_symbols: str = "!@#$%^&*()_+-="):
        self.env_file_path = env_file_path
        self.min_length = min_length
        self.max_length = 255
        self.required_symbols = required_symbols
        self.is_authenticated = False
        self.api_interface = None
        self.setup_or_authenticate()

    def setup_or_authenticate(self):
        """
        Handles password setup if no password exists or authenticates if a password is present.
        """
        load_dotenv(self.env_file_path)
        if os.getenv('SALT') is None:
            print("No password found. Setting up a new password.")
            self.setup_password()
        else:
            password = getpass.getpass("Enter your password to access the encrypted keys: ")
            self.api_interface = APIKeyInterface(password=password, env_file_path=self.env_file_path)
            self.is_authenticated = self.api_interface.is_authenticated

    def setup_password(self):
        """
        Prompts the user to set up a new password with defined security standards.
        """
        while True:
            password = getpass.getpass("Create a password: ")
            if self.validate_password(password):
                confirm_password = getpass.getpass("Confirm your password: ")
                if password == confirm_password:
                    print("Password setup successful.")
                    SecureAPIKeyManager(password=password, env_file_path=self.env_file_path)
                    break
                else:
                    print("Passwords do not match. Please try again.")
            else:
                print(f"Password must be at least {self.min_length} characters long and contain at least one of the required symbols: {self.required_symbols}")

    def validate_password(self, password: str) -> bool:
        """
        Validates the password based on the defined length and required symbols.
        Args:
            password (str): The password to validate.
        Returns:
            bool: True if the password meets all criteria, False otherwise.
        """
        if len(password) < self.min_length or len(password) > self.max_length:
            return False
        if not any(char in self.required_symbols for char in password):
            return False
        return True

    """
    A manager class to handle initial password setup, authentication, and interface creation.
    """
    def __init__(self, env_file_path: str, min_length: int = 16, required_symbols: str = "!@#$%^&*()_+-="):
        self.env_file_path = env_file_path
        self.min_length = min_length
        self.max_length = 255
        self.required_symbols = required_symbols
        self.is_authenticated = False
        self.api_interface = None
        self.setup_or_authenticate()

    def setup_or_authenticate(self):
        """
        Handles password setup if no password exists or authenticates if a password is present.
        """
        load_dotenv(self.env_file_path)
        if os.getenv('SALT') is None:
            print("No password found. Setting up a new password.")
            self.setup_password()
        else:
            password = getpass.getpass("Enter your password to access the encrypted keys: ")
            self.api_interface = APIKeyInterface(password=password, env_file_path=self.env_file_path)
            self.is_authenticated = self.api_interface.is_authenticated

    def add_api_key(self, key_name: Union[str, None]=None, api_key: Union[str, None]=None):
        """
        Adds a new API key to the interface.
        Args:
            key_name (str): The name of the API key variable (e.g., OPENAI_API_KEY).
            api_key (str): The actual API key to store.
        """
        if self.is_authenticated:
            if key_name is None:
              key_name = input("Enter a name for the API key: ")
            if api_key is None:
                self.api_interface.add_api_key(key_name, getpass.getpass(f"Enter {key_name}:"))
            else:
                self.api_interface.add_api_key(key_name, api_key)
        else:
            print("You need to authenticate first to add new API keys.")
            self.setup_or_authenticate()

    def setup_password(self):
        """
        Prompts the user to set up a new password with defined security standards.
        """
        while True:
            password = getpass.getpass("Create a password: ")
            if self.validate_password(password):
                confirm_password = getpass.getpass("Confirm your password: ")
                if password == confirm_password:
                    print("Password setup successful.")
                    SecureAPIKeyManager(password=password, env_file_path=self.env_file_path)
                    break
                else:
                    print("Passwords do not match. Please try again.")
            else:
                print(f"Password must be at least {self.min_length} characters long and contain at least one of the required symbols: {self.required_symbols}")

    def validate_password(self, password: str) -> bool:
        """
        Validates the password based on the defined length and required symbols.
        Args:
            password (str): The password to validate.
        Returns:
            bool: True if the password meets all criteria, False otherwise.
        """
        if len(password) < self.min_length and len(password) > self.max_length:
            return False
        if not any(char in self.required_symbols for char in password):
            return False
        return True