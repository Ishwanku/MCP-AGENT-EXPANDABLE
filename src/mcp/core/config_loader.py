# src/mcp/core/config_loader.py

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Server settings
    DOCUMENT_AGENT_API_KEY: Optional[str] = None
    OUTPUT_DIR: str = "output"
    API_BASE_URL: Optional[str] = "http://127.0.0.1:9100"

    # Azure Cognitive Search
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_INDEX_NAME: Optional[str] = None

    # Azure Blob Storage
    AZURE_STORAGE_ACCOUNT: Optional[str] = None
    AZURE_STORAGE_CONTAINER: Optional[str] = None

    # Azure OpenAI settings (exclusive provider)
    LLM_PROVIDER: str = "azure"
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None
    AZURE_OPENAI_API_VERSION: Optional[str] = "2024-02-15-preview"

    # LLM Settings
    LLM_DEFAULT_MAX_TOKENS: int = 1000
    LLM_DEFAULT_TEMPERATURE: float = 0.7

    # Document Set Default Settings
    DEFAULT_SUMMARY_TYPE: str = "detailed"
    DEFAULT_INCLUDE_SECTIONS: List[str] = ["executive_summary", "important_information"]

    @property
    def API_TOOLS_URL(self) -> str:
        return f"{self.API_BASE_URL}/tools"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
