# aitools

A customizable MCP server with auto-registered tools.

## Install

```bash
pip install -e .
# or: pip install git+https://github.com/Seaborn101/aitools-mcp.git
```

Required environment variable:

```bash
export WXPUSHER_SPT=your_spt_token  # for send_message tool
```

## Usage

### 1. As MCP Server

```bash
aitools
# or: python -m aitools.server
```

Then configure in your MCP client (Claude Code, etc.):

```json
{
  "mcpServers": {
    "aitools": {
      "command": "aitools"
    }
  }
}
```

### 2. As Python Package (direct function calls)

```python
from aitools.tools.wx_pusher import send_message

# Markdown mode (default)
send_message(content="# Hello\nThis is a **test** message")

# HTML mode
send_message(
    content="<h1>Hello</h1><p style='color:red;'>Red text</p>",
    use_html=True
)

# With summary
send_message(content="...", summary="Brief summary")
```

### Available Tools

| Tool | Description |
|------|-------------|
| `send_message` | Push notification to desktop popup + mobile via WxPusher |

## Adding New Tools

Create a new file in `src/aitools/tools/` (e.g., `my_tool.py`):

```python
"""My custom tool."""
from aitools.server import tool

@tool(name="my_tool", description="Does something useful.")
def my_tool(arg1: str, arg2: int = 10) -> str:
    """Do something.

    Args:
        arg1: First argument.
        arg2: Second argument (default 10).
    """
    return f"Result: {arg1}, {arg2}"
```

Tools auto-register on server start. No manual registration needed.

## Framework

- **Auto-discovery**: Tools in `src/aitools/tools/` are auto-loaded via `pkgutil`
- **Decorator-based**: Use `@tool` decorator to register
- **Type hints**: Schema auto-generated from function signatures
- **No hardcoded tokens**: Use env vars for secrets
