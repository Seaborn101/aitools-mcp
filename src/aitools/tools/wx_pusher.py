"""WxPusher push tool - send messages to WeChat via WxPusher."""
import os
import requests
from fastmcp import Tool

WX_PUSHER_URL = "https://wxpusher.zjiecode.com/api/send/message/simple-push"
DEFAULT_SPT = os.environ.get("WXPUSHER_SPT", "")


def get_tool() -> Tool:
    return Tool(
        name="send_message",
        description="Push a message to WeChat via WxPusher. contentType: markdown(3) if use_html=False, html(2) if use_html=True.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Message content (markdown or HTML)",
                },
                "summary": {
                    "type": "string",
                    "description": "Message summary (max 100 chars, defaults to first 50 chars of content)",
                },
                "use_html": {
                    "type": "boolean",
                    "description": "False=markdown(3), True=html(2). Default False.",
                },
                "spt": {
                    "type": "string",
                    "description": "WxPusher SPT token. Defaults to the configured default token.",
                },
            },
            "required": ["content"],
        },
    )


def run_tool(
    content: str,
    summary: str | None = None,
    use_html: bool = False,
    spt: str | None = None,
) -> str:
    """Send a message via WxPusher."""
    token = spt or DEFAULT_SPT
    if not token:
        return "✗ Error: SPT token not provided. Set spt arg or WXPUSHER_SPT env var."

    payload = {
        "content": content,
        "contentType": 2 if use_html else 3,
        "spt": token,
    }
    if summary:
        payload["summary"] = summary[:100]

    try:
        resp = requests.post(WX_PUSHER_URL, json=payload, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 1000:
            return f"✓ Message sent successfully. msgId: {result.get('msgId')}"
        return f"✗ Failed: {result}"
    except Exception as e:
        return f"✗ Error: {e}"
