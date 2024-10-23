from cryptography.fernet import Fernet
import os
import base64
import hashlib
from dotenv import load_dotenv

class SecureAPIKeyManager:
    """
    A class to securely manage API keys using encryption.
    This class handles encrypting and storing API keys in a .env file.
    The encryption key is derived from a user password and a stored salt.
    """
    def __init__(self, password: str, env_file_path: str):
        self.env_file_path = env_file_path
        self.salt = self._get_or_generate_salt()
        self.fernet = Fernet(self._derive_key(password, self.salt))

    def _get_or_generate_salt(self) -> bytes:
        """
        Retrieves the salt from the .env file or generates a new one if not present.
        Returns:
            bytes: The salt used for key derivation.
        """
        load_dotenv(self.env_file_path)
        salt = os.getenv('SALT')
        if not salt:
            salt = base64.urlsafe_b64encode(os.urandom(16)).decode()
            with open(self.env_file_path, 'a') as f:
                f.write(f"SALT={salt}\n")
        return base64.urlsafe_b64decode(salt)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derives an encryption key from the user's password and salt using PBKDF2.
        Args:
            password (str): The user's password.
            salt (bytes): The salt value for key derivation.
        Returns:
            bytes: The derived encryption key.
        """
        key = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm
            password.encode(),  # Convert the password to bytes
            salt,  # Provide the salt
            100000  # Iterations of the hash function
        )
        return base64.urlsafe_b64encode(key)

    def add_api_key(self, key_name: str, api_key: str):
        """
        Encrypts and stores the given API key in the .env file.
        Args:
            key_name (str): The name of the API key variable (e.g., OPENAI_API_KEY).
            api_key (str): The actual API key to store.
        """
        encrypted_key = self.fernet.encrypt(api_key.encode()).decode()
        with open(self.env_file_path, 'a') as f:
            f.write(f"{key_name}_ENCRYPTED={encrypted_key}\n")
        print(f"API key for {key_name} encrypted and stored successfully.")