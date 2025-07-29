import logging
from typing import Dict, List
from mcp.core.config_loader import Settings
from mcp.core.config_validator import SettingsValidator
from mcp.core.llm_client import LLMClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
from ..tools.models import DocumentState, SummarizeNodeResult, FolderUpdate

settings = Settings()
SettingsValidator(settings).validate()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This function helps to get folder and file structure from Azure Blob Storage to organize the generated summaries in folder(Section) wise structure
def get_blob_structure(storage_account, container_name):
    account_url = f"https://{storage_account}.blob.core.windows.net"
    blob_service_client = BlobServiceClient(
        account_url=account_url, credential=DefaultAzureCredential()
    )
    container_client: ContainerClient = blob_service_client.get_container_client(
        container_name
    )
    folder_map: Dict[str, List[str]] = {}
    blobs = container_client.list_blobs()
    for blob in blobs:
        blob_path = blob.name
        parts = blob_path.split("/")
        if len(parts) == 1:
            folder = "root"
            file_name = parts[0]
        else:
            folder = "/".join(parts[:-1])
            file_name = parts[-1]
        folder_map.setdefault(folder, []).append(file_name)
    return folder_map


# This function summarizes each document using the LLM client
async def summarize_node(state: dict, max_tokens: int, temperature: float):
    logger.info(f"Summarize node called with state: {state}")
    doc = state["documents"][0]
    if isinstance(doc, dict):
        doc = DocumentState(**doc)
    logger.info(f"Summarizing document: {doc.file_name}")
    llm_client = LLMClient(settings)
    prompt = f"""
    Document: {doc.content}
    Please analyze the document and provide a concise summary.
    """
    try:
        analysis = await llm_client.generate_content(
            prompt=prompt, max_tokens=max_tokens, temperature=temperature
        )
        logger.info(f"LLM response for {doc.file_name}: {analysis}")
        if not analysis or analysis == "No response generated":
            analysis = "Summary generation failed."
            logger.warning(f"Summary generation failed for {doc.file_name}")
    except Exception as e:
        analysis = f"Summary generation failed: {str(e)}"
        logger.error(f"Error summarizing {doc.file_name}: {str(e)}")

    result = SummarizeNodeResult(
        folder_update=FolderUpdate(
            folder=doc.folder_name,
            documents=[
                {
                    "blob_path": doc.blob_path,
                    "document_name": doc.file_name,
                    "status": (
                        "summarized"
                        if analysis != "Summary generation failed."
                        else "failed"
                    ),
                    "analysis": analysis,
                }
            ],
        ),
        summary_text=f"Summary for {doc.file_name}:\n{analysis}",
    )
    logger.info(f"Summarize node result for {doc.file_name}: {result}")
    return {"summarize_node": result}
