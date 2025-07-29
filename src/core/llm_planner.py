"""
LLM-based workflow planner for document processing.

This module defines the LLMPlanner class, which analyzes user commands and generates a sequence of tool calls (plan) to fulfill document processing workflows. It uses static plans for known commands or queries an LLM for dynamic planning.
"""
import json
import difflib
from openai import AsyncAzureOpenAI
from .config_loader import Settings

# Tool registry with descriptions & input schema
TOOL_REGISTRY = {
    "fetch_documents": {
        "description": "Fetches documents from Azure Blob storage and Azure Cognitive Search.",
        "input": {"source": "blob_storage"},
    },
    "batch_summarize": {
        "description": "Summarizes documents.",
        "input": {"documents": "..."},
    },
    "merge_document": {
        "description": "Merges summarized documents into a Word document.",
        "input": {"folder_updates": "...", "output_filename": "merged.docx"},
    },
    "create_directory": {
        "description": "Creates output folders.",
        "input": {"directory_name": "folder_name"},
    },
}

# Static predefined flows for known commands
STATIC_PLANS = {
    # If the user command matches any of these, use the static plan
    "merge all documents from azure blob and generate a word document.": [
        {"tool": "fetch_documents", "input": {"source": "blob_storage"}},
        {"tool": "batch_summarize", "input": {"documents": "use_previous_result"}},
        {"tool": "merge_document", "input": "use_previous_result"},
    ],
    "merge all the documents": [
        {"tool": "fetch_documents", "input": {"source": "blob_storage"}},
        {"tool": "batch_summarize", "input": {"documents": "use_previous_result"}},
        {"tool": "merge_document", "input": "use_previous_result"},
    ],
    "merge all documents and give output as a word document.": [
        {"tool": "fetch_documents", "input": {"source": "blob_storage"}},
        {"tool": "batch_summarize", "input": {"documents": "use_previous_result"}},
        {"tool": "merge_document", "input": "use_previous_result"},
    ],
    "merge all documents and generate a word document.": [
        {"tool": "fetch_documents", "input": {"source": "blob_storage"}},
        {"tool": "batch_summarize", "input": {"documents": "use_previous_result"}},
        {"tool": "merge_document", "input": "use_previous_result"},
    ],
}


class LLMPlanner:
    def __init__(self, settings: Settings, tools=None):
        # Store settings and initialize the LLM client
        self.settings = settings
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME

        # Use tool registry keys as default tool list
        self.tools = tools if tools is not None else list(TOOL_REGISTRY.keys())

    async def plan(self, user_command, context=None):
        normalized_cmd = user_command.strip().lower()
        # Try exact match first for static plans
        if normalized_cmd in STATIC_PLANS:
            return STATIC_PLANS[normalized_cmd]
        # Try fuzzy match if no exact match
        close_matches = difflib.get_close_matches(
            normalized_cmd, STATIC_PLANS.keys(), n=1, cutoff=0.7
        )
        if close_matches:
            return STATIC_PLANS[close_matches[0]]

        # Build a string describing available tools for the LLM prompt
        tools_str = "\n".join(
            f"- {name}: {info['description']} Input: {info['input']}"
            for name, info in TOOL_REGISTRY.items()
            if name in self.tools
        )

        # Compose the prompt for the LLM to generate a plan
        prompt = f"""
You are an intelligent document workflow orchestrator.

Your job is to analyze the user's request and plan the sequence of tool invocations needed to complete it.

---

Available tools:
{tools_str}

---

 Behavior:
- If the user's request requires multiple steps, respond with a JSON list of tool calls like:
  [
    {{"tool": "fetch_documents", "input": {{"source": "blob_storage"}}}},
    {{"tool": "batch_summarize", "input": {{"documents": "use_previous_result"}}}},
    {{"tool": "merge_document", "input": {{"folder_updates": "use_previous_result", "output_filename": "merged.docx"}}}}
  ]

- If no tools are needed and the user is asking something general (e.g. "What tools do you have?"), respond with a plain string.

- Do NOT explain anything. Only return either:
  - A plain string
  - OR a valid JSON array of tool calls

---

User command: {user_command}
Context: {context or 'None'}
"""

        # Call the LLM to generate a plan based on the prompt
        response = await self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=self.settings.LLM_DEFAULT_MAX_TOKENS,
        )

        # Extract the content from the LLM response
        content = response.choices[0].message.content.strip()

        try:
            # Try to parse the plan as JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # If parsing fails, return an error tool step
            return [
                {
                    "tool": "error",
                    "input": {"message": f"Failed to parse plan: {content}"},
                }
            ]
