import os
import getpass
from dotenv import load_dotenv
from .api_key_encryption_manager import APIKeyEncryptionManager
from .decrypted_api_key import DecryptedAPIKey

class APIKeyInterface:
    """
    A high-level interface to manage and retrieve API keys.
    Handles user authentication, manages session state, and provides DecryptedAPIKey objects.
    """
    def __init__(self, encryption_manager: APIKeyEncryptionManager):
        self.encryption_manager = encryption_manager
        self.api_keys = {}
        self._load_api_keys()

    def _load_api_keys(self):
        # This method might need to be updated depending on how you want to handle existing keys
        pass

    def add_api_key(self, key_name: str, api_key: str):
        self.encryption_manager.encrypt_and_store_key(key_name, api_key)
        self.api_keys[key_name] = DecryptedAPIKey(key_name, self.encryption_manager)

    def get_api_key(self, key_name: str) -> str:
        if key_name not in self.api_keys:
            raise ValueError(f"API key '{key_name}' not found.")
        return self.api_keys[key_name]()
