import base64
import logging
from langgraph.pregel import Send
from collections import defaultdict
from tools.models import FolderUpdate, BatchState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Define a safe base64 decode function to handle potential padding issues
def safe_base64_decodedcode(s):
    missing_padding = len(s) % 4
    if missing_padding:
        s += "=" * (4 - missing_padding)
    return base64.b64decode(s).decode("utf-8")


# This function is used to fan out documents for processing in parallel
async def fan_out_documents(state: BatchState):
    logger.info(f"Fan-out: Processing {len(state.documents)} documents")
    return [Send("summarize_node", {"documents": [doc]}) for doc in state.documents]




# This function aggregates results from the summarize_node and prepares the final output
def aggregate_results(state: BatchState):
    logger.info(f"Aggregating results from state: {state}")

    folder_updates_dict = defaultdict(list)
    summaries = []

    # Collect results from summarize_node
    for result in state.summarize_node:
        if hasattr(result, "folder_update"):
            folder = result.folder_update.folder
            folder_updates_dict[folder].extend(result.folder_update.documents)
            logger.info(f"Added documents to folder {folder}")
        if hasattr(result, "summary_text"):
            summaries.append(result.summary_text)
            logger.info(f"Added summary: {result.summary_text}")

    folder_updates = [
        FolderUpdate(folder=folder, documents=docs)
        for folder, docs in folder_updates_dict.items()
    ]

    logger.info(f"Aggregated folder updates: {len(folder_updates)} folders")

    result = {
        "folder_updates": folder_updates,
        "summaries": summaries,
        "documents": [],  # Clear to prevent further processing
        "summarize_node": state.summarize_node,  # Keep for inspection if needed
    }

    logger.info(f"Aggregation result: {result}")
    return result
