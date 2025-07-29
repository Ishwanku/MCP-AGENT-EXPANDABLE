"""
Async client for interacting with Azure OpenAI LLM.

This module provides the LLMClient class, which handles robust, retried calls to the LLM for generating document summaries and workflow plans.
"""
import logging
from typing import Callable, Any
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import AsyncAzureOpenAI
from .config_loader import Settings
from .config_validator import SettingsValidator

settings = Settings()
SettingsValidator(settings).validate()

# Set up logger
logger = logging.getLogger(__name__)


# Retry decorator for robustness in LLM calls
def retry_llm_call(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 10.0,
    exceptions: tuple = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=initial_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
        )
        async def wrapper(*args, **kwargs) -> Any:
            # Retry the wrapped async function on failure
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class LLMClient:
    def __init__(self, settings: Settings): 
        # Store settings and deployment name
        self.settings = settings
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self._init_client()

    def _init_client(self):
        # Validate required Azure OpenAI settings
        if not self.settings.AZURE_OPENAI_API_KEY:
            raise ValueError("AZURE_OPENAI_API_KEY is required")
        if not self.settings.AZURE_OPENAI_ENDPOINT:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required")
        if not self.settings.AZURE_OPENAI_DEPLOYMENT_NAME:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME is required")

        # Initialize the async OpenAI client
        self.client = AsyncAzureOpenAI(
            api_key=self.settings.AZURE_OPENAI_API_KEY,
            api_version=self.settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
        )

    def is_available(self) -> bool:
        # Check if the client is initialized
        return hasattr(self, "client") and self.client is not None

    @retry_llm_call(
        max_attempts=3, initial_wait=1.0, max_wait=10.0, exceptions=(Exception,)
    )
    async def generate_content(
        self, prompt: str, max_tokens: int = None, temperature: float = None
    ) -> str:
        # Ensure the client is available
        if not self.is_available():
            raise RuntimeError("LLM client is not initialized")

        # Use default values if not provided
        if max_tokens is None:
            max_tokens = self.settings.LLM_DEFAULT_MAX_TOKENS
        if temperature is None:
            temperature = self.settings.LLM_DEFAULT_TEMPERATURE

        try:
            # Send a chat completion request to the LLM
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes documents and provides concise summaries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Check if any choices were returned
            if not response.choices:
                logger.warning("No choices returned from OpenAI")
                return "No response generated"

            # Extract and return the content from the first choice
            content = response.choices[0].message.content.strip()
            return content

        except Exception as e:
            # Log and raise errors from the LLM call
            logger.exception("Error while generating content from LLM")
            raise RuntimeError(f"LLM call failed: {e}")
