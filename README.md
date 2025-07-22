# MCP Document Merge Agent

This project is a FastAPI-based backend that orchestrates the fetching, summarization, and merging of documents from Azure Blob Storage using LLMs and LangGraph for parallel processing. The final output is a merged Word document containing summaries of all documents.

## Features

- **Fetch documents** from Azure Blob Storage and Azure Cognitive Search
- **Summarize documents in parallel** using an LLM (Azure OpenAI)
- **Merge summaries** into a single Word document
- **Orchestrate workflows** using a CLI or HTTP API

## Project Structure

``
MCP-AGENT_workings/
  src/mcp/
    agents/           # FastAPI app, agent logic, plan execution
    core/             # Config, LLM client, planner
    tools/            # Tool endpoints (fetch, summarize, merge), models, utils
    mcp_client.py     # HTTP client for tool endpoints
    orchestrator_llm_merge_to_output.py  # CLI orchestrator
  README.md
  pyproject.toml
``

## Prerequisites

- Python 3.9+
- Azure account with Blob Storage, Cognitive Search, and OpenAI resources
- Required Python packages (see below)

## Installation

1. Clone the repository.
2. Install dependencies:

   ```bash
   pip install -r src/mcp_agent.egg-info/requires.txt
   ```

3. Set up your `.env` file or environment variables for Azure credentials and API keys (see `src/mcp/core/config.py` for required variables).

## Configuration

Create a `.env` file in the project root with the following (example):

``
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
AZURE_STORAGE_ACCOUNT=your-storage-account
AZURE_STORAGE_CONTAINER=your-container
AZURE_SEARCH_ENDPOINT=https://your-search-endpoint.search.windows.net
AZURE_SEARCH_INDEX_NAME=your-index
``

## Running the FastAPI Server

From the project root, run:

```bash
uvicorn src.mcp.agents.agent:agent --reload --port 9100
```

## Using the Orchestrator CLI

Run the CLI tool to interact with the agent:

```bash
python src/mcp/orchestrator_llm_merge_to_output.py
```

You will be prompted to enter a command, e.g.:

``
merge all documents from Azure Blob and generate a Word document.
``

The agent will fetch, summarize, and merge documents, then return the path to the generated Word file.

## API Endpoints

- `/plan_and_execute` (POST): Accepts a command and executes the workflow.
- `/tools/fetch_documents` (POST): Fetches documents from Azure.
- `/tools/batch_summarize` (POST): Summarizes documents in parallel.
- `/tools/merge_document` (POST): Merges summaries into a Word document.

## Workflow Overview

1. **User command** (via CLI or HTTP) triggers the workflow.
2. **LLMPlanner** generates a plan (sequence of tool calls).
3. **Agent** executes each tool in order:
   - Fetches documents
   - Summarizes them in parallel (LangGraph)
   - Merges summaries into a Word document
4. **Result** (output file path) is returned to the user.

## Extending or Debugging

- Add new tools in `src/mcp/tools/` and register them in `a_tool_register.py`.
- Update the planner logic in `src/mcp/core/llm_planner.py` for new workflows.
- Use logging in `src/mcp/tools/utils.py` for debugging parallel summarization and merging.
