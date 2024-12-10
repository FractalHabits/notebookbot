import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional
from langchain.docstore.document import Document
import os
from pathlib import Path
from notebookbot.authentication.authentication_setup import AuthenticationSetup
import logging

class ChromaDBManager:
    _instance = None
    _api_keys = None
    _auth = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path="./chroma_db", reset_db: bool = False):
        # Setup logging
        log_dir = Path(db_path)
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "chromadb.log"
        
        # Configure logging format and file handler
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                #logging.StreamHandler()  # This will also print to console
            ]
        )

        # getattr(object: Any, name: str, default: Any = None) -> Any
        # Safely gets an attribute from an object, returning default if not found
        if not getattr(self, '_initialized', False):
            logging.info(f"Initializing ChromaDBManager with path: {db_path}")
            if reset_db and os.path.exists(db_path):
                import shutil
                shutil.rmtree(db_path)
                logging.info(f"Deleted existing database at {db_path}")
        if not getattr(self, '_initialized', False):
            # Initialize auth only if not already initialized
            if ChromaDBManager._auth is None:
                ChromaDBManager._auth = AuthenticationSetup()
                if not ChromaDBManager._auth.authenticate():
                    raise ValueError("Authentication failed. Please check your API keys.")
            
            # Get API keys only if not already set
            if ChromaDBManager._api_keys is None:
                try:
                    ChromaDBManager._api_keys = ChromaDBManager._auth.get_api_keys()
                except ValueError:
                    raise ValueError("Failed to get API keys. Please ensure you're authenticated.")
            
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Use OpenAI embeddings with the decrypted key
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=ChromaDBManager._api_keys.openai,
                model_name="text-embedding-ada-002"
            )
            
            self.collection = self.client.get_or_create_collection(
                name="user_collection",
                embedding_function=openai_ef,
                metadata={"description": "User collection of documents"}
            )
            self._initialized = True

    def reset_collection(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection("user_collection")
            logging.info("Deleted existing collection")
            
            # Recreate the collection
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=ChromaDBManager._api_keys.openai,
                model_name="text-embedding-ada-002"
            )
            
            self.collection = self.client.create_collection(
                name="user_collection",
                embedding_function=openai_ef,
                metadata={"description": "User collection of documents"}
            )
            logging.info("Created new empty collection")
        except Exception as e:
            logging.error(f"Error resetting collection: {e}")
    def load_txt_documents(self, txt_dir: str = "data/txt") -> List[Document]:
        """Load all .txt files from the specified directory"""
        documents = []
        txt_path = Path(txt_dir)
        
        if not txt_path.exists():
            raise ValueError(f"Directory not found: {txt_dir}")
        
        # Print all txt files found
        txt_files = list(txt_path.glob("*.txt"))
        logging.info(f"Found {len(txt_files)} .txt files in {txt_dir}")
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(txt_file),
                            "filename": txt_file.name,
                            "id": f"txt_{txt_file.stem}"
                        }
                    )
                    documents.append(doc)
                    logging.info(f"Successfully loaded: {txt_file.name}")
            except Exception as e:
                logging.error(f"Error loading {txt_file}: {e}")
        
        logging.info(f"Loaded {len(documents)} documents from {txt_dir}")
        return documents

    def add_documents(self, documents: List[Document]):
        """Add new documents to ChromaDB"""
        logging.info(f"Attempting to add {len(documents)} documents to ChromaDB")
        for i, doc in enumerate(documents):
            self.collection.add(
                documents=[doc.page_content],
                metadatas=[doc.metadata],
                ids=[doc.metadata.get("id", f"doc_{i}")]
            )
            logging.info(f"Added document {i+1} with ID: {doc.metadata.get('id', f'doc_{i}')}")
        logging.info(f"Added {len(documents)} documents to ChromaDB")

    def load_and_embed_txt_documents(self, txt_dir: str = "../data/raw/txt")-> bool:
        """Load and embed all .txt documents from the specified directory"""
        documents = self.load_txt_documents(txt_dir)
        if documents:
            self.add_documents(documents)
            return True
        return False

    def query_documents(self, query: str, n_results: int = 5):
        """Query the vector database"""
        if not hasattr(self, 'collection') or self.collection is None:
            logging.error("Collection not initialized")
            raise ValueError("Collection not initialized. Ensure ChromaDBManager is properly initialized.")
        
        try:
            total_docs = self.collection.count()
            logging.info(f"Total documents in collection: {total_docs}")
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, total_docs)  # Ensure we don't request more than available
            )
            logging.info(f"Query returned {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logging.error(f"Error during query: {str(e)}")
            raise 