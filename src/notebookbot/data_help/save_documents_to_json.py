import json
import os
from typing import List
from langchain.docstore.document import Document

def save_documents_to_json(documents: List[Document], directory: str = "../data/raw/json"):
    """
    Save a list of LangChain documents as individual JSON files in the specified directory.
    """
    os.makedirs(directory, exist_ok=True)

    for doc in documents:
        doc_id = doc.metadata.get("id", doc.metadata.get("source", doc.metadata.get("file_path")))
        doc_title = doc.metadata.get("Title", doc.metadata.get("source", doc.metadata.get("file_path")))
        if not doc_id:
            raise ValueError("Document must have an 'id', 'source', or 'file_path' field in its metadata.")

        file_path = os.path.join(directory, f"{doc_title}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(doc.model_dump(), f, ensure_ascii=False, indent=2)
