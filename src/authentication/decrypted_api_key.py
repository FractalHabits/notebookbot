from .api_key_retriever import APIKeyRetriever

class DecryptedAPIKey:
    """
    A class representing a decrypted API key, with lazy evaluation.
    Decrypts the key only when called.
    """
    def __init__(self, key_name: str, retriever: APIKeyRetriever):
        self.key_name = key_name
        self.retriever = retriever

    def __call__(self):
        """
        Decrypts and returns the API key.
        Returns:
            str: The decrypted API key.
        """
        return self.retriever.authenticate_and_get_key(self.key_name)