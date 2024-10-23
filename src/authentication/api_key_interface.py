import os
import getpass
from dotenv import load_dotenv
from .decrypted_api_key import DecryptedAPIKey
from .api_key_retriever import APIKeyRetriever
from .secure_api_key_manager import SecureAPIKeyManager

class APIKeyInterface:
    """
    A high-level interface to manage and retrieve API keys.
    Handles user authentication, manages session state, and provides DecryptedAPIKey objects.
    """
    def __init__(self, password: str, env_file_path: str):
        self.env_file_path = env_file_path
        self.retriever = APIKeyRetriever(password, env_file_path)
        self.is_authenticated = False
        self.api_keys = {}
        self.authenticate(password)

    def authenticate(self, password: str):
        """
        Authenticates the user and sets up decrypted API key instances.
        """
        self.is_authenticated = True
        self._load_api_keys()

    def _load_api_keys(self):
        """
        Loads all encrypted API keys from the .env file and creates DecryptedAPIKey instances.
        """
        load_dotenv(self.env_file_path)
        for key, value in os.environ.items():
            if key.endswith('_ENCRYPTED'):
                key_name = key.replace('_ENCRYPTED', '')
                self.api_keys[key_name] = DecryptedAPIKey(key_name, self.retriever)

    def add_api_key(self, key_name: str, api_key: str):
        """
        Adds and encrypts a new API key using SecureAPIKeyManager.
        Args:
            key_name (str): The name of the API key variable (e.g., OPENAI_API_KEY).
            api_key (str): The actual API key to store.
        """
        if self.is_authenticated:
            manager = SecureAPIKeyManager(password=getpass.getpass("Enter your password for encryption: "), env_file_path=self.env_file_path)
            manager.add_api_key(key_name, api_key)
            self.api_keys[key_name] = DecryptedAPIKey(key_name, self.retriever)
        else:
            print("You need to authenticate first to add new API keys.")