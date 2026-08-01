"""HTTP POST tool - placeholder for fetching webpage content."""
import requests
from fastmcp import Tool


def get_tool() -> Tool:
    return Tool(
        name="http_post",
        description="Send a POST request to a URL and return the response",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to send POST request to"},
                "data": {"type": "object", "description": "JSON data to send in request body"},
            },
            "required": ["url"],
        },
    )


def run_tool(url: str, data: dict | None = None) -> str:
    try:
        resp = requests.post(url, json=data, timeout=10)
        resp.raise_for_status()
        return f"Status: {resp.status_code}\n\n{resp.text[:1000]}"
    except Exception as e:
        return f"Error: {e}"
