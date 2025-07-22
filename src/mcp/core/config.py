"""
Configuration management for the MCP Document Merge Agent.

This module defines the Settings class, which loads environment variables and provides configuration for Azure, LLM, and server settings used throughout the application.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator


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
        # Returns the full URL for the tools API endpoints
        return f"{self.API_BASE_URL}/tools"

    @field_validator("AZURE_OPENAI_ENDPOINT")
    def validate_endpoint(cls, v):
        # Ensure the endpoint is a valid HTTPS URL
        if v and not v.startswith("https://"):
            raise ValueError("AZURE_OPENAI_ENDPOINT must be a valid HTTPS URL")
        return v

    @field_validator("AZURE_OPENAI_API_KEY")
    def validate_api_key(cls, v):
        # Ensure the API key is provided
        if not v:
            raise ValueError("AZURE_OPENAI_API_KEY is required")
        return v

    @field_validator("AZURE_OPENAI_DEPLOYMENT_NAME")
    def validate_deployment_name(cls, v):
        # Ensure the deployment name is provided
        if not v:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME is required")
        return v

    @field_validator("AZURE_STORAGE_ACCOUNT")
    def validate_storage_account(cls, v):
        # Ensure the storage account is provided
        if not v:
            raise ValueError("AZURE_STORAGE_ACCOUNT is required")
        return v

    @field_validator("AZURE_STORAGE_CONTAINER")
    def validate_storage_container(cls, v):
        # Ensure the storage container is provided
        if not v:
            raise ValueError("AZURE_STORAGE_CONTAINER is required")
        return v

    class Config:
        # Configuration for loading environment variables
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


# Instantiate the settings object to be used throughout the application
settings = Settings()
