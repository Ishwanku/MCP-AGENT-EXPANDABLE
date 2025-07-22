"""
This module provides utility functions for the MCP Agent, including helpers for replacing placeholders in tool input with results from previous tool executions.
"""

def replace_use_previous(obj, result, tool, step):
    # If input is a placeholder to use the previous tool's result
    if obj == "use_previous_result":
        if result is None:
            # Raise an error if there is no previous result to use
            raise ValueError("No previous result available")

        # Special handling for batch_summarize tool
        if tool == "batch_summarize":
            documents_raw = result.get("documents", [])  # Get documents from previous result
            documents = []
            for doc in documents_raw:
                # Build a new document structure for summarization
                documents.append(
                    {
                        "content": doc.get("content", doc.get("analysis", "")),
                        "summary": doc.get("summary"),
                        "blob_path": doc.get("blob_path"),
                        "file_name": doc.get("file_name") or doc.get("document_name", ""),
                        "folder_name": doc.get("folder_name", "Default"),
                    }
                )
            return documents

        # Special handling for merge_document tool
        if tool == "merge_document":
            documents = []
            folder_updates = result.get("folder_updates", [])  # Get folder updates from previous result
            for folder in folder_updates:
                folder_name = folder.get("folder", "Default")
                docs = folder.get("documents", [])
                for doc in docs:
                    # Build a new document structure for merging
                    documents.append(
                        {
                            "content": "",  # No content at this stage
                            "summary": doc.get("analysis", ""),
                            "blob_path": doc.get("blob_path", ""),
                            "file_name": doc.get("document_name", ""),
                            "folder_name": folder_name,
                        }
                    )
            output_folder = "output"
            output_filename = "merged.docx"
            input_obj = step.get("input", {})
            if isinstance(input_obj, dict):
                # Use output_filename from input if provided
                output_filename = input_obj.get("output_filename", "merged.docx")

            return {
                "documents": documents,
                "output_folder": output_folder,
                "output_filename": output_filename,
            }

        # Default case: return the previous result as-is
        return result

    # Recursively handle nested dictionaries
    elif isinstance(obj, dict):
        return {k: replace_use_previous(v, result, tool, step) for k, v in obj.items()}

    # Recursively handle lists
    elif isinstance(obj, list):
        return [replace_use_previous(i, result, tool, step) for i in obj]

    # Return value unchanged if not a special case
    else:
        return obj
