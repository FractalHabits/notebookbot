import os
from typing import List
from langchain.docstore.document import Document

def save_documents_to_txt(documents: List[Document], directory: str = "data/raw/txt"):
    """
    Save a list of LangChain documents as individual text files in the specified directory.
    Metadata is included at the top of each file.
    """
    os.makedirs(directory, exist_ok=True)

    for doc in documents:
        doc_id = doc.metadata.get("id", doc.metadata.get("source", doc.metadata.get("file_path")))
        doc_title = doc.metadata.get("Title", doc.metadata.get("source", doc.metadata.get("file_path")))
        if not doc_id:
            raise ValueError("Document must have an 'id', 'source', or 'file_path' field in its metadata.")

        file_path = os.path.join(directory, f"{doc_title}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            # Write metadata
            f.write("Metadata:\n")
            for key, value in doc.metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("\nContent:\n")
            # Write content
            f.write(doc.page_content)
