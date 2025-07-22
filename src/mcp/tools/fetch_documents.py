"""
Tool endpoint for fetching documents from Azure Blob Storage and Azure Cognitive Search.

This FastAPI route retrieves documents and their folder structure from Azure, returning them in a structured format for further processing in the workflow.
"""
from fastapi import APIRouter
from .models import (
    DocumentState,
    FetchDocumentsResponse,
)
from .utils import (
    get_blob_structure,
    safe_base64_decode,
)
from mcp.core.config import settings
from azure.search.documents import SearchClient
from azure.identity import DefaultAzureCredential

router = APIRouter()


@router.post("/fetch_documents", response_model=FetchDocumentsResponse)
async def fetch_documents_tool():
    # Validate Azure configuration
    storage_account = settings.AZURE_STORAGE_ACCOUNT
    container = settings.AZURE_STORAGE_CONTAINER
    index = settings.AZURE_SEARCH_INDEX_NAME
    search_endpoint = settings.AZURE_SEARCH_ENDPOINT
    if not all([storage_account, container, index, search_endpoint]):
        raise ValueError(
            "Missing required Azure config: storage_account, container, index, or search_endpoint"
        )
    print(
        f"Using storage_account: {storage_account}, container: {container}, index: {index}, search_endpoint: {search_endpoint}"
    )

    # Get folder → [file] mapping from Azure Blob Storage
    folder_map = get_blob_structure(storage_account, container)
    # Create a search client for Azure Cognitive Search
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=index,
        credential=DefaultAzureCredential(),
    )
    # Search for all documents in the index
    query = "*"
    results = search_client.search(search_text=query)
    # Parse results into DocumentState objects
    documents = []
    for result in results:
        content = result.get("content", "")
        file_name = result.get("metadata_storage_name", "unknown.docx")
        blob_path_encoded = result.get("metadata_storage_path", "")
        blob_path = safe_base64_decode(blob_path_encoded)

        # Find which folder this file belongs to
        folder_name = next(
            (f for f, files in folder_map.items() if file_name in files), "Unknown"
        )
        if content:
            # Constructs a list of DocumentState objects
            documents.append(
                DocumentState(
                    content=content,
                    summary=None,
                    blob_path=blob_path,
                    file_name=file_name,
                    folder_name=folder_name,
                )
            )
    print(f"Fetched {len(documents)} documents from Azure Search index '{index}'")
    # Return the documents and folder map in the response
    return FetchDocumentsResponse(documents=documents, folder_map=folder_map)
