import os
import getpass
from dotenv import load_dotenv
from typing import Union

from .api_key_encryption_manager import APIKeyEncryptionManager
from .api_key_interface import APIKeyInterface

class AuthenticationManager:
    """
    A manager class to handle initial password setup, authentication, and interface creation.
    """
    def __init__(self, env_file_path: str, min_length: int = 16, required_symbols: str = "!@#$%^&*()_+-="):
        self.env_file_path = env_file_path
        self.min_length = min_length
        self.required_symbols = required_symbols
        self.is_authenticated = False
        self.api_interface = None

    def setup_or_authenticate(self):
        """
        Handles password setup if no password exists or authenticates if a password is present.
        """
        password = self._get_password()
        if self._validate_password(password):
            encryption_manager = APIKeyEncryptionManager(password, self.env_file_path)
            self.api_interface = APIKeyInterface(encryption_manager)
            self.is_authenticated = True
            print("Authentication successful.")
        else:
            print("Authentication failed.")

    def _get_password(self):
        return getpass.getpass("Enter your password: ")

    def _validate_password(self, password: str) -> bool:
        # Implement your password validation logic here
        return len(password) >= self.min_length and any(char in self.required_symbols for char in password)

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
                api_key = getpass.getpass(f"Enter {key_name}: ")
            self.api_interface.add_api_key(key_name, api_key)
        else:
            print("You need to authenticate first to add new API keys.")
            self.setup_or_authenticate()

    def get_api_key(self, key_name: str) -> str:
        """
        Retrieves an API key from the interface.
        Args:
            key_name (str): The name of the API key variable (e.g., OPENAI_API_KEY).
        Returns:
            str: The actual API key.
        """
        if self.is_authenticated:
            return self.api_interface.get_api_key(key_name)
        else:
            print("You need to authenticate first to retrieve API keys.")
            self.setup_or_authenticate()
            return self.get_api_key(key_name)
