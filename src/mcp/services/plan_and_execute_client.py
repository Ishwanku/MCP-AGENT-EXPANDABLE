import requests
from mcp.core.config_loader import Settings
from mcp.core.config_validator import SettingsValidator

class PlanAndExecuteClient:
    def __init__(self):
        self.settings = Settings()
        SettingsValidator(self.settings).validate()
        self.api_url = f"{self.settings.API_BASE_URL}/plan_and_execute"

    def send_command(self, command: str) -> dict:
        try:
            response = requests.post(self.api_url, json={"command": command})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Failed to contact MCP agent: {str(e)}") from e
