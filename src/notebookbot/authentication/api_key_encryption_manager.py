from cryptography.fernet import Fernet
import os
import base64
import hashlib
from dotenv import load_dotenv

class APIKeyEncryptionManager:
    """
    A class to securely manage API keys using encryption.
    This class handles encrypting, storing, and retrieving API keys from a .env file.
    The encryption key is derived from a user password and a stored salt.
    """
    def __init__(self, password: str, env_file_path: str):
        self.password = password
        self.env_file_path = env_file_path
        self.salt = self._get_or_generate_salt()
        self.fernet = Fernet(self._derive_key(password, self.salt))
        load_dotenv(self.env_file_path)

    def _get_or_generate_salt(self) -> bytes:
        """Retrieves the salt from the .env file or generates a new one if not present."""
        try:
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    if line.startswith('SALT='):
                        # Add padding back before decoding
                        salt_b64 = line.split('=')[1].strip()
                        padding = '=' * ((4 - len(salt_b64) % 4) % 4)
                        salt_b64 += padding
                        return base64.urlsafe_b64decode(salt_b64)
        except FileNotFoundError:
            pass

        # Generate new salt
        salt = os.urandom(16)
        salt_b64 = base64.urlsafe_b64encode(salt).decode().rstrip('=')
        with open(self.env_file_path, 'a') as f:
            f.write(f"SALT={salt_b64}\n")
        return salt

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

    def encrypt_and_store_key(self, key_name: str, api_key: str):
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
        # Reload environment variables after writing
        load_dotenv(self.env_file_path, override=True)

    def decrypt_key(self, key_name: str) -> str:
        """
        Decrypts and returns the API key for the given key name.
        Args:
            key_name (str): The name of the API key variable (e.g., OPENAI_API_KEY).
        Returns:
            str: The decrypted API key.
        """
        # Reload environment variables before reading
        load_dotenv(self.env_file_path, override=True)
        encrypted_key = os.getenv(f"{key_name}_ENCRYPTED")
        if not encrypted_key:
            raise ValueError(f"Encrypted key for {key_name} not found.")
        try:
            return self.fernet.decrypt(encrypted_key.encode()).decode()
        except Exception:
            print("Decryption failed. Incorrect password or corrupted data.")
            return None

    def list_keys(self) -> set:
        """List all available encrypted API keys."""
        keys = set()
        try:
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    if '_ENCRYPTED=' in line:
                        # Extract just the key name without the _ENCRYPTED suffix
                        key_name = line.split('_ENCRYPTED=')[0].strip()
                        keys.add(key_name)
        except FileNotFoundError:
            return set()
        
        return keys
