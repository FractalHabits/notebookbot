from .api_key_encryption_manager import APIKeyEncryptionManager

class DecryptedAPIKey:
    """
    A class representing a decrypted API key, with lazy evaluation.
    Decrypts the key only when called.
    """
    def __init__(self, key_name: str, encryption_manager: APIKeyEncryptionManager):
        self.key_name = key_name
        self.encryption_manager = encryption_manager

    def __call__(self):
        """
        Decrypts and returns the API key.
        Returns:
            str: The decrypted API key.
        """
        return self.encryption_manager.decrypt_key(self.key_name)
