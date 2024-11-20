import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional
from langchain.docstore.document import Document
import os
from pathlib import Path

class ChromaDBManager:
    _instance = None
    _api_keys = None  # Class variable to store API keys

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def set_api_keys(cls, api_keys):
        """Set API keys for the ChromaDBManager"""
        cls._api_keys = api_keys

    def __init__(self, db_path="./chroma_db"):
        if not self._initialized:
            if self._api_keys is None:
                raise ValueError("API keys not set. Call ChromaDBManager.set_api_keys() first.")
            
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Use OpenAI embeddings with the decrypted key
            openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=self._api_keys.openai,
                model_name="text-embedding-ada-002"
            )
            
            self.collection = self.client.get_or_create_collection(
                name="user_collection",
                embedding_function=openai_ef,
                metadata={"description": "User collection of documents"}
            )
            self._initialized = True

    def load_txt_documents(self, txt_dir: str = "data/txt") -> List[Document]:
        """Load all .txt files from the specified directory"""
        documents = []
        txt_path = Path(txt_dir)
        
        if not txt_path.exists():
            raise ValueError(f"Directory not found: {txt_dir}")
        
        # Print all txt files found
        txt_files = list(txt_path.glob("*.txt"))
        print(f"Found {len(txt_files)} .txt files in {txt_dir}")
        
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
                    print(f"Successfully loaded: {txt_file.name}")
            except Exception as e:
                print(f"Error loading {txt_file}: {e}")
        
        print(f"Loaded {len(documents)} documents from {txt_dir}")
        return documents

    def add_documents(self, documents: List[Document]):
        """Add new documents to ChromaDB"""
        print(f"Attempting to add {len(documents)} documents to ChromaDB")
        for i, doc in enumerate(documents):
            self.collection.add(
                documents=[doc.page_content],
                metadatas=[doc.metadata],
                ids=[doc.metadata.get("id", f"doc_{i}")]
            )
            print(f"Added document {i+1} with ID: {doc.metadata.get('id', f'doc_{i}')}")
        print(f"Added {len(documents)} documents to ChromaDB")

    def load_and_embed_txt_documents(self, txt_dir: str = "data/txt"):
        """Load and embed all .txt documents from the specified directory"""
        documents = self.load_txt_documents(txt_dir)
        if documents:
            self.add_documents(documents)
            return True
        return False

    def query_documents(self, query: str, n_results: int = 5):
        """Query the vector database"""
        # Get total count of documents in collection
        total_docs = self.collection.count()
        print(f"Total documents in collection: {total_docs}")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        print(f"Query returned {len(results['documents'][0])} results")
        return results 