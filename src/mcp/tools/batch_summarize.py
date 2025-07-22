"""
Tool endpoint for batch summarization of documents using LLMs.

This FastAPI route receives a list of documents, summarizes them in parallel using an LLM (via LangGraph), and returns summaries and folder-wise groupings for downstream merging.
"""
from fastapi import APIRouter
from .models import (
    DocumentState,
    BatchSummarizeRequest,
    BatchSummarizeResponse,
    BatchState,
)
from .utils import (
    summarize_node,
    fan_out_documents,
    aggregate_results,
)
from langgraph.graph import StateGraph, START, END
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/batch_summarize", response_model=BatchSummarizeResponse)
async def batch_summarize_tool(request: BatchSummarizeRequest):
    # Log the number of documents received for summarization
    logger.info(
        f"Received batch summarize request with {len(request.documents)} documents"
    )

    # Create a LangGraph state graph for parallel summarization
    builder = StateGraph(BatchState)

    # Identity node: passes state through unchanged
    async def identity_node(state: BatchState):
        logger.info(f"Identity node: {len(state.documents)} documents in state")
        return state

    # Wrapper node to summarize a single document
    async def summarize_node_wrapper(state: BatchState):
        doc_dict = state["documents"][0]
        doc = DocumentState(**doc_dict) if isinstance(doc_dict, dict) else doc_dict

        # Call the summarization logic for this document
        result = await summarize_node(
            {"documents": [doc]}, request.max_tokens, request.temperature
        )
        return result

    # Add nodes to the graph
    builder.add_node("fan_out_documents", identity_node)
    builder.add_node("summarize_node", summarize_node_wrapper)
    builder.add_node("aggregate_results", aggregate_results)

    # Define edges for the graph (workflow steps)
    builder.add_edge(START, "fan_out_documents")
    builder.add_conditional_edges(
        "fan_out_documents", fan_out_documents, ["summarize_node"]
    )
    builder.add_edge("summarize_node", "aggregate_results")
    builder.add_edge("aggregate_results", END)

    # Compile the graph for execution
    graph = builder.compile()

    # Convert input documents to DocumentState objects if needed
    newDocuments = [
        DocumentState(**doc) if isinstance(doc, dict) else doc
        for doc in request.documents
    ]

    # Set up the initial state for the graph
    initial_state = BatchState(
        documents=newDocuments,
        folder_updates=[],
        summaries=[],
        summarize_node=[],
    )
    logger.info(f"Initial state: {len(initial_state.documents)} documents")

    # Run the graph asynchronously to process all documents in parallel
    result = await graph.ainvoke(initial_state)
    return result
