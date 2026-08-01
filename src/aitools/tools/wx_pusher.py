"""WxPusher push tool - send messages to WeChat via WxPusher."""
import os
import requests

from aitools.server import tool

WX_PUSHER_URL = "https://wxpusher.zjiecode.com/api/send/message/simple-push"


@tool(name="send_message", description="Push a message to WeChat via WxPusher.")
def send_message(
    content: str,
    summary: str | None = None,
    use_html: bool = False,
    spt: str | None = None,
) -> str:
    """Send a message via WxPusher.

    Args:
        content: Message content (markdown or HTML).
        summary: Brief summary (max 100 chars).
        use_html: False=markdown(3), True=html(2).
        spt: WxPusher SPT token (or set WXPUSHER_SPT env var).
    """
    token = spt or os.environ.get("WXPUSHER_SPT", "")
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
            return f"✓ Message sent. msgId: {result.get('msgId')}"
        return f"✗ Failed: {result}"
    except Exception as e:
        return f"✗ Error: {e}"
