"""
MCP Server with auto-tool registration.

Framework design:
- Add new .py files to src/aitools/tools/
- Each tool function uses @tool decorator (from this module)
- Tools auto-register on server start
"""
import importlib
import pkgutil
import warnings
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic.json_schema import PydanticJsonSchemaWarning

# Suppress pydantic non-serializable default warning (cosmetic,不影响功能)
warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)

# Load .env from project root (where pyproject.toml lives)
load_dotenv(Path(__file__).parent.parent.parent / ".env")

TOOLS_DIR = Path(__file__).parent / "tools"

# Global registry for tools: {(module_name, func_name): func}
_tool_registry: dict = {}


def tool(name: str | None = None, description: str | None = None):
    """Decorator to register a function as an MCP tool."""
    def decorator(fn):
        key = (fn.__module__.split(".")[-1], fn.__name__)
        _tool_registry[key] = {
            "fn": fn,
            "name": name or fn.__name__,
            "description": description or fn.__doc__ or "",
        }
        return fn
    return decorator


def create_server() -> FastMCP:
    mcp = FastMCP("aitools")

    # Load all tool modules
    for _importer, modname, ispkg in pkgutil.iter_modules([str(TOOLS_DIR)]):
        if modname.startswith("_"):
            continue
        full_name = f"aitools.tools.{modname}"
        importlib.import_module(full_name)

    # Register discovered tools
    for (modname, funcname), info in _tool_registry.items():
        fn = info["fn"]

        @mcp.tool(name=info["name"], description=info["description"])
        def wrapper(kwargs, _fn=fn):
            return _fn(**kwargs)

        print(f"[+] Registered: {info['name']} ({modname}.{funcname})")

    return mcp


mcp = create_server()


if __name__ == "__main__":
    mcp.run()
