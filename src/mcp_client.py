import aiohttp

class MCPClient:
    """
    Client for communicating with the MCP Agent's tool endpoints via HTTP.
    Handles sending requests to tool APIs and returning their responses.
    """
    def __init__(self, api_url: str, api_key: str | None = None):
        # Store the base API URL, ensuring no trailing slash
        self.api_url = api_url.rstrip('/')
        # Store the API key if provided
        self.api_key = api_key
        # Prepare headers for authentication if API key is present
        self.headers = {"api-key": self.api_key} if self.api_key else {}

    async def call_tool(self, tool_name: str, **kwargs):
        # Build the full URL for the tool endpoint
        url = f"{self.api_url}/{tool_name}"
        # Create an asynchronous HTTP session with the appropriate headers
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Send a POST request to the tool endpoint with the provided JSON payload
            async with session.post(url, json=kwargs) as response:
                # Raise an error if the response status is not 2xx
                response.raise_for_status()
                # Parse and return the JSON response from the tool
                json_response = await response.json()
                return json_response
