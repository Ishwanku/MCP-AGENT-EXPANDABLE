"""
CLI entry point for the MCP Document Merge Agent.

This script allows a user to enter document processing commands (such as merging and summarizing documents from Azure Blob Storage) via the command line. It sends the command to the FastAPI backend's /plan_and_execute endpoint, receives the result, and prints it for the user. The backend orchestrates the workflow using LLM-based planning and tool execution.
"""
import requests
from mcp.core.config import settings

def main():
    api_url = f"{settings.API_BASE_URL}/plan_and_execute"

    print("Ask anything related to document processing. Example:")
    print("   merge all documents from Azure Blob and generate a Word document.\n")

    while True:
        command = input("You: ")
        if command.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        try:
            response = requests.post(api_url, json={"command": command})
            response.raise_for_status()
            result = response.json()

            print("Agent response:")
            print(result)
        except Exception as e:
            print("Failed to contact MCP agent:", str(e))

if __name__ == "__main__":
    main()
