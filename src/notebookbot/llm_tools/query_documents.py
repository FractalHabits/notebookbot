from langchain_core.tools import tool
from notebookbot.chromadb.chromadb_manager import ChromaDBManager
from typing import Literal, Optional

@tool
def query_documents(
    query: str, 
    n_results: int = 5,
    return_fields: Optional[Literal["title", "authors", "summary", "metadata", "content", "all"]] = "all"
) -> str:
    """
    Search through previously saved documents using semantic search.
    Args:
        query: The search query
        n_results: Number of results to return (default: 5)
        return_fields: What information to return from the documents. Options:
            - "title": Return only the titles
            - "authors": Return titles and authors
            - "summary": Return titles and summaries
            - "metadata": Return all metadata (published date, authors, title, source)
            - "content": Return title and full content
            - "all": Return all available information (default)
    """
    db_manager = ChromaDBManager()
    results = db_manager.query_documents(query, n_results)
    
    # Format results based on requested fields
    formatted_results = []
    for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
        if return_fields == "title":
            formatted_results.append(
                f"Title: {metadata.get('Title', 'Unknown')}"
            )
        elif return_fields == "authors":
            formatted_results.append(
                f"Title: {metadata.get('Title', 'Unknown')}\n"
                f"Authors: {metadata.get('Authors', 'Unknown authors')}"
            )
        elif return_fields == "summary":
            formatted_results.append(
                f"Title: {metadata.get('Title', 'Unknown')}\n"
                f"Summary: {metadata.get('Summary', 'No summary available')}"
            )
        elif return_fields == "metadata":
            formatted_results.append(
                f"Title: {metadata.get('Title', 'Unknown')}\n"
                f"Authors: {metadata.get('Authors', 'Unknown authors')}\n"
                f"Published: {metadata.get('Published', 'Unknown date')}\n"
                f"Source: {metadata.get('source', 'Unknown source')}"
            )
        elif return_fields == "content":
            formatted_results.append(
                f"Title: {metadata.get('Title', 'Unknown')}\n"
                f"Content: {doc[:500]}..."  # First 500 chars of content
            )
        else:  # "all"
            formatted_results.append(
                f"Title: {metadata.get('Title', 'Unknown')}\n"
                f"Authors: {metadata.get('Authors', 'Unknown authors')}\n"
                f"Published: {metadata.get('Published', 'Unknown date')}\n"
                f"Source: {metadata.get('source', 'Unknown source')}\n"
                f"Summary: {metadata.get('Summary', 'No summary available')}\n"
                f"Content: {doc[:500]}..."  # First 500 chars of content
            )
    
    return "\n\n".join(formatted_results) 