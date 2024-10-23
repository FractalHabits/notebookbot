import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from src.authentication.authentication_manager import AuthenticationManager


def main():
    # Step 1: Set up or authenticate with existing credentials to access stored API keys
    env_file_path = '.env'  # This should be relative to the project root
    auth_manager = AuthenticationManager(env_file_path=env_file_path)

    #auth_manager.add_api_key()
    #auth_manager.add_api_key()

    if auth_manager.is_authenticated:
        # Retrieve and use existing API keys
        try:
            print(auth_manager.api_interface.api_keys.items())
            OPENAI_API_KEY = auth_manager.api_interface.api_keys['OPENAI_API_KEY']
            ANTHROPIC_API_KEY = auth_manager.api_interface.api_keys['ANTHROPIC_API_KEY']
        except ValueError as e:
            print(str(e))

        # Display available API keys
        print("Available API keys:")
        for key_name in auth_manager.api_interface.api_keys:
            print(key_name)

if __name__ == "__main__":
    main()
