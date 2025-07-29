# MCP Agent Tool & Workflow Extension Guide

This document explains how to extend the MCP Agent with new tools (API endpoints), workflows, and static/LLM-driven plans. Use this as a reference for adding new document processing capabilities or automations.

---

## 1. Adding a New Tool (API Endpoint)

### A. Create the Tool Logic

- Add a new file in `src/mcp/tools/` (or add to an existing one).
- Implement a FastAPI router endpoint for your tool.
- Define request/response models in `models.py` if needed.

**Example:**

```python
# src/mcp/tools/my_new_tool.py
from fastapi import APIRouter
from .models import MyNewToolRequest, MyNewToolResponse

router = APIRouter()

@router.post("/my_new_tool", response_model=MyNewToolResponse)
async def my_new_tool_endpoint(request: MyNewToolRequest):
    # Your logic here
    return MyNewToolResponse(...)
```

### B. Register the Tool

- In `src/mcp/tools/a_tool_register.py`, import and include your new router:

```python
from .my_new_tool import router as my_new_tool_router
app.include_router(my_new_tool_router)
```

---

## 2. Update Models (If Needed)

- Add new Pydantic models to `src/mcp/tools/models.py` for your tool’s request/response.

---

## 3. Add Tool to the Tool Registry

- In `src/mcp/core/llm_planner.py`, add your tool to `TOOL_REGISTRY`:

```python
TOOL_REGISTRY = {
    # ...existing...
    "my_new_tool": {
        "description": "Describe what your tool does.",
        "input": {"param1": "type", "param2": "type"}
    },
}
```

---

## 4. Add Static Plans for New Workflows

- In `STATIC_PLANS` in `llm_planner.py`, add new user command variants and the sequence of tool calls:

```python
STATIC_PLANS = {
    # ...existing...
    "run my new workflow": [
        {"tool": "fetch_documents", "input": {"source": "blob_storage"}},
        {"tool": "my_new_tool", "input": {"param1": "use_previous_result"}},
        {"tool": "merge_document", "input": "use_previous_result"},
    ],
}
```

- Add as many variants as you want for fuzzy matching.

---

## 5. Update `replace_use_previous` (If Needed)

- If your new tool needs to transform the previous result, add a special case in `src/mcp/agents/utils.py`:

```python
if tool == "my_new_tool":
    # Transform result as needed
    return ...
```

---

## 6. (Optional) Update LLM Prompt

- If you want the LLM to be able to plan with your new tool, update the prompt in `llm_planner.py` to include a clear description and example usage.

---

## 7. Test Your New Workflow

- Use the CLI or API to send a command that matches your new static plan or triggers the LLM to use your new tool.

---

## Best Practices

- **Keep static plans up to date** for all common workflows.
- **Add fuzzy-matching variants** for user-friendly experience.
- **Document new tools and workflows** in your README and this extension guide.
- **Validate LLM-generated plans** before execution if possible.

---

## Example: Adding a PDF-to-Text Extraction Tool

1. **Create `tools/pdf_extract.py`** with a FastAPI endpoint.
2. **Add models** for request/response in `models.py`.
3. **Register the router** in `a_tool_register.py`.
4. **Add to `TOOL_REGISTRY`**:

   ```python
   "pdf_extract": {
       "description": "Extracts text from PDF files.",
       "input": {"pdf_url": "str"}
   }
   ```

5. **Add static plan**:

   ```python
   "extract text from pdf and summarize": [
       {"tool": "pdf_extract", "input": {"pdf_url": "some_url"}},
       {"tool": "batch_summarize", "input": {"documents": "use_previous_result"}},
   ]
   ```

6. **Handle result passing** in `replace_use_previous` if needed.

---

## Troubleshooting

- If a tool fails with a 422 error, check the input schema and ensure all required fields are present.
- If the LLM does not generate the correct plan, add a static plan and/or improve fuzzy matching.
- Use logging and debug prints during development, but remove them for production.

---

**Keep this file updated as you add new tools and workflows!**
