from fastapi import APIRouter

# Import routers for each tool endpoint
from .fetch_documents import router as fetch_documents_router
from .batch_summarize import router as batch_summarize_router
from .merge_document import router as merge_document_router

# Create a FastAPI APIRouter to aggregate all tool endpoints
app = APIRouter()

# Register the fetch_documents tool endpoint
app.include_router(fetch_documents_router)
# Register the batch_summarize tool endpoint
app.include_router(batch_summarize_router)
# Register the merge_document tool endpoint
app.include_router(merge_document_router)
