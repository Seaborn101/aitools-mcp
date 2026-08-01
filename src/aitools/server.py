"""
MCP Server with auto-tool registration.

Framework design:
- Add new .py files to src/aitools/tools/
- Each file exports: get_tool() -> Tool and run_tool(**kwargs) -> str
- Tools auto-register on server start
"""
import importlib
import pkgutil
from pathlib import Path

from fastmcp import FastMCP

TOOLS_DIR = Path(__file__).parent / "tools"


def create_server() -> FastMCP:
    mcp = FastMCP("aitools")

    # Iterate all modules in tools package
    for _importer, modname, ispkg in pkgutil.iter_modules([str(TOOLS_DIR)]):
        if modname.startswith("_"):
            continue

        full_name = f"aitools.tools.{modname}"
        module = importlib.import_module(full_name)

        # Look for get_tool() export
        if hasattr(module, "get_tool") and hasattr(module, "run_tool"):
            tool = module.get_tool()
            run_fn = module.run_tool

            @mcp.tool(name=tool.name, description=tool.description)
            def tool_wrapper(kwargs, _run=run_fn, _schema=tool.inputSchema):
                return _run(**kwargs)

            print(f"✓ Registered: {tool.name}")

    return mcp


mcp = create_server()


if __name__ == "__main__":
    # Run: python -m aitools.server
    mcp.run()
