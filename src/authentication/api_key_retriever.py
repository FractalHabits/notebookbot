from cryptography.fernet import Fernet
import os
import base64
import hashlib
from dotenv import load_dotenv

class APIKeyRetriever:
    """
    A class to retrieve and decrypt API keys after successful authentication.
    The encryption key is derived from a user password and a stored salt.
    """
    def __init__(self, password: str, env_file_path: str):
        self.env_file_path = env_file_path
        try:
            self.salt = self._get_salt()
            self.fernet = Fernet(self._derive_key(password, self.salt))
        except ValueError:
            print("Incorrect password or salt retrieval failed. Please try again.")
        load_dotenv(self.env_file_path)

    def _get_salt(self) -> bytes:
        """
        Retrieves the salt from the .env file.
        Returns:
            bytes: The salt used for key derivation.
        """
        load_dotenv(self.env_file_path)
        salt = os.getenv('SALT')
        if not salt:
            raise ValueError("Salt not found in the .env file.")
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

    def authenticate_and_get_key(self, key_name: str) -> str:
        """
        Returns the decrypted API key after authentication.
        Args:
            key_name (str): The name of the API key variable (e.g., OPENAI_API_KEY).
        Returns:
            str: The decrypted API key.
        """
        encrypted_key = os.getenv(f"{key_name}_ENCRYPTED")
        if not encrypted_key:
            raise ValueError(f"Encrypted key for {key_name} not found.")
        try:
            return self.fernet.decrypt(encrypted_key.encode()).decode()
        except Exception:
            print("Decryption failed. Incorrect password or corrupted data.")
            return None