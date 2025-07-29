from core.config_loader import Settings


class SettingsValidator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def validate(self):
        self._validate_https_endpoint(self.settings.AZURE_OPENAI_ENDPOINT)
        self._validate_required(
            "AZURE_OPENAI_API_KEY", self.settings.AZURE_OPENAI_API_KEY
        )
        self._validate_required(
            "AZURE_OPENAI_DEPLOYMENT_NAME", self.settings.AZURE_OPENAI_DEPLOYMENT_NAME
        )
        self._validate_required(
            "AZURE_STORAGE_ACCOUNT", self.settings.AZURE_STORAGE_ACCOUNT
        )
        self._validate_required(
            "AZURE_STORAGE_CONTAINER", self.settings.AZURE_STORAGE_CONTAINER
        )

    def _validate_https_endpoint(self, endpoint: str):
        if endpoint and not endpoint.startswith("https://"):
            raise ValueError("AZURE_OPENAI_ENDPOINT must be a valid HTTPS URL")

    def _validate_required(self, name: str, value):
        if not value:
            raise ValueError(f"{name} is required")
