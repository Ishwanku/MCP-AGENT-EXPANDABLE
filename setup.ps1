# 1. Move to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# 2. Ensure pyproject.toml exists
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "ERROR: pyproject.toml not found. Are you in the project root?"
    exit 1
}

# 3. Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# 4. Use venv's Python directly
$venvPython = ".venv\Scripts\python.exe"

# 5. Install dependencies
Write-Host "Installing dependencies from pyproject.toml..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e .

# 6. Start the FastAPI server
Write-Host "Starting FastAPI server with reload..."
& $venvPython -m uvicorn src.mcp.agents.agent:agent --host 0.0.0.0 --port 9100 --reload
