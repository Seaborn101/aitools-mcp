"""WxPusher 推送工具 - 发送桌面弹窗 + 手机通知。

摘要: 通过 WxPusher 发送桌面弹窗和手机推送通知
依赖: requests
约束:
- 需要设置 WXPUSHER_SPT 环境变量
- content 建议不超过 1024 字符
"""

import os
import requests

from aitools.server import tool


@tool(name="send_message", description="Push a notification to desktop (popup) and mobile")
def send_message(
    title: str,
    content: str,
    use_html: bool = False
) -> str:
    """Send a push notification via WxPusher.

    Args:
        title: Notification title (shown in mobile notification banner).
        content: Message body (markdown or HTML).
        use_html: False=markdown, True=html.
    """
    token = os.environ.get("WXPUSHER_SPT")
    if not token:
        return "✗ Error: SPT token not provided. Set spt arg or WXPUSHER_SPT env var."

    payload = {
        "summary": title,
        "content": content,
        "contentType": 2 if use_html else 3,
        "spt": token,
    }

    try:
        url = "https://wxpusher.zjiecode.com/api/send/message/simple-push"
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 1000:
            return f"✓ Message sent. msgId: {result.get('msgId')}"
        return f"✗ Failed: {result}"
    except Exception as e:
        return f"✗ Error: {e}"
