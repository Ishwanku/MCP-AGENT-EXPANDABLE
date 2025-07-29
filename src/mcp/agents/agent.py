"""
This file defines the main API endpoints, including /plan_and_execute, which receives user commands, 
generates a workflow plan using an LLM, and executes a sequence of document processing tools (fetch, summarize, merge) to fulfill the request.
"""
from fastapi import FastAPI, Request
from mcp.tools.a_tool_register import app as tools_app
from mcp.core.llm_planner import LLMPlanner
from mcp.mcp_client import MCPClient
from mcp.core.config_loader import Settings
from mcp.core.config_validator import SettingsValidator
from mcp.utils.agentUtils import replace_use_previous
import json

# Initialize config
settings = Settings()
SettingsValidator(settings).validate()

# Create the FastAPI application for the Document Merge MCP Agent
agent = FastAPI(title="Document Merge MCP Agent")
agent.mount("/tools", tools_app)

# Define the root endpoint
@agent.get("/")
async def root():
    return {
        "message": "Welcome to the Document Merge MCP Agent.",
        "tools": [
            "/tools/fetch_documents",
            "/tools/batch_summarize",
            "/tools/merge_document",
        ],
    }

# Define the /plan_and_execute endpoint
@agent.post("/plan_and_execute")
async def plan_and_execute(request: Request):
    # Parse the incoming JSON body
    body = await request.json()
    command = body.get("command")

    # Return error if no command is provided
    if not command:
        return {"error": "No command provided."}

    # Create a planner instance to generate execution steps
    planner = LLMPlanner(settings=settings)
    plan_response = await planner.plan(command)

    # Parse the planner's response into a list of steps
    if isinstance(plan_response, str):
        try:
            plan = json.loads(plan_response)
        except Exception:
            return {"message": plan_response}
    elif isinstance(plan_response, list):
        plan = plan_response
    else:
        return {"error": "Planner returned unexpected response type."}

    # Initialize the MCP client to call tools
    client = MCPClient(api_url=settings.API_TOOLS_URL)
    result = None  # Store result of each step

    # Loop through each planned step
    for step in plan:
        tool = step.get("tool")
        if not tool:
            return {"error": "Step missing tool name."}

        input_data = step.get("input", {})

        try:
            # Replace __use_previous__ references with actual data
            input_data = replace_use_previous(input_data, result, tool, step)
            # Call the tool with input and store the result
            result = await client.call_tool(tool, **input_data)
        except Exception as e:
            # Return error if any tool fails
            print(f"Tool '{tool}' failed with error: {e}")
            return {"error": f"Tool '{tool}' failed: {str(e)}"}

    # Return the final result after executing all steps
    return {"message": "Execution complete", "result": result}
