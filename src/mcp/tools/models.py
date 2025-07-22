"""
Pydantic data models for document processing tools.

Defines the schemas for documents, summaries, batch states, and API request/response payloads used throughout the workflow.
"""
from pydantic import BaseModel
from typing import List, Dict, Optional
from typing import Annotated
from langgraph.channels import Topic


class DocumentState(BaseModel):
    # Represents a single document's content and metadata
    content: str
    summary: Optional[str] = None
    blob_path: str
    file_name: str
    folder_name: str


class FolderUpdate(BaseModel):
    # Represents a folder and its associated documents (for merging)
    folder: str
    documents: List[Dict[str, str]]


class SummarizeNodeResult(BaseModel):
    # Result of summarizing a document, including folder update and summary text
    folder_update: FolderUpdate
    summary_text: str


class BatchState(BaseModel):
    # State for batch summarization, including all documents and results
    documents: List[DocumentState]
    folder_updates: List[FolderUpdate]
    summaries: List[str]
    summarize_node: Annotated[List[SummarizeNodeResult], Topic("summarize_node")] = []


class BatchSummarizeRequest(BaseModel):
    # Request payload for batch summarization
    documents: List[DocumentState]
    max_tokens: int = 1000
    temperature: float = 0.7


class BatchSummarizeResponse(BaseModel):
    # Response payload for batch summarization
    summaries: List[str]
    folder_updates: List[FolderUpdate]


class MergeDocumentRequest(BaseModel):
    # Request payload for merging documents into a Word file
    documents: List[DocumentState]
    output_filename: str
    output_folder: str


class MergeDocumentResponse(BaseModel):
    # Response payload for merged Word document
    output_file_path: str


class FetchDocumentsResponse(BaseModel):
    # Response payload for fetched documents and folder structure
    documents: List[DocumentState]
    folder_map: Dict[str, List[str]]
