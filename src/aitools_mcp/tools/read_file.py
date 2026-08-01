"""Read file tool - placeholder for reading first 5 lines of a file."""
from fastmcp import Tool


def get_tool() -> Tool:
    return Tool(
        name="read_file",
        description="Read the first 5 lines of a file",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to read"},
            },
            "required": ["path"],
        },
    )


def run_tool(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(5)]
            lines = [l for l in lines if l]
        return "".join(lines) if lines else "(empty file)"
    except Exception as e:
        return f"Error: {e}"
