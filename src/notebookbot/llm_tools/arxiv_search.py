from typing import Literal
import uuid

from langchain_community.document_loaders import ArxivLoader
from langchain_community.utilities import ArxivAPIWrapper
from langchain_core.tools import tool
from notebookbot.data_help.save_documents_to_json import save_documents_to_json

@tool
def arxiv_search(query: str,
                        max_results: int = 10,
                        load_max_refs: int = 10,
                        categories: list[str] = [],
                        sort_by: Literal["relevance",
                                          "lastUpdatedDate",
                                          "submittedDate"] = "relevance",
                        sort_order: Literal["ascending", "descending"] = "descending"
                        ) -> list:
            """
            Call to search arxiv and return a list of documents.
            arxiv_search(query: str,
                        max_results: int = 10,
                        load_max_refs: int = 10,
                        categories: list[str] = [],
                        sort_by: Literal["relevance",
                                          "lastUpdatedDate",
                                          "submittedDate"] = "relevance",
                        sort_order: Literal["ascending", "descending"] = "descending"
                        ) -> list:
            """
            arxiv = ArxivAPIWrapper(query=query, 
                                    max_results=max_results, 
                                    load_max_refs=load_max_refs,
                                    categories=categories,
                                    sort_order=sort_order,
                                    sort_by=sort_by)
            docs = arxiv.load(query)
            for i, doc in enumerate(docs):
                doc.metadata["id"] = str(uuid.uuid4())
                doc.metadata["source"] = "arXiv"
            save_documents_to_json(docs)
            return docs