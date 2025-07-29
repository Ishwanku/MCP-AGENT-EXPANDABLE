from pathlib import Path
from datetime import datetime
from mcp.core.config_loader import Settings
from mcp.core.config_validator import SettingsValidator

settings = Settings()
SettingsValidator(settings).validate()

# Create output directory
def get_or_create_output_dir(output_folder: str = None) -> Path:
    base_name = output_folder or getattr(settings, "OUTPUT_DIR", "output_folder")
    timestamp = datetime.now().strftime("on_%Y-%m-%d_at_%I_%M_%p")
    full_name = f"{base_name}_{timestamp}"
    output_dir = Path(full_name).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir