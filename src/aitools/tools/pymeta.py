"""Python 元数据工具 - 解析文件头部 docstring，生成代码库结构视图。"""
import json
import os
import re
from pathlib import Path

from aitools.server import tool


@tool(name="parse_header", description="解析 Python 文件开头的多行 docstring，提取结构化元数据")
def parse_header(path: str) -> str:
    """解析 Python 文件头部的 docstring 元数据。

    头部格式示例:
        qqq
        摘要: 文件功能的简要描述
        依赖: dep_a.py, dep_b.py
        被依赖: caller_x.py
        约束:
        - 约束项 1
        - 约束项 2
        qqq

    Args:
        path: Python 文件路径（绝对路径或相对于当前目录）

    Returns:
        JSON 字符串：
        {
            "path": "xxx.py",
            "metadata": {"摘要": "...", "依赖": "...", ...},
            "raw_header": "<原始头部（不含 triple-quote）>"
        }
    """
    try:
        file_path = Path(path).resolve()
        if not file_path.exists():
            return json.dumps({"error": f"文件不存在: {path}"}, ensure_ascii=False)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取文件开头的 docstring
        match = re.match(r'^(\s*)(["\']{3})(.*?)(\2)', content, re.DOTALL)
        if not match:
            return json.dumps({
                "path": str(file_path),
                "metadata": {},
                "raw_header": "",
                "error": "未找到 docstring header"
            }, ensure_ascii=False)

        header_text = match.group(3).strip()

        # 解析键值对
        metadata = {}
        current_key = None
        current_lines = []

        for line in header_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            key_match = re.match(r'^([^\s:：]+)[:：]\s*(.*)$', line)
            if key_match:
                if current_key:
                    metadata[current_key] = '\n'.join(current_lines).strip()
                current_key = key_match.group(1).strip()
                rest = key_match.group(2).strip()
                current_lines = [rest[1:].strip()] if rest.startswith('-') else ([rest] if rest else [])
            elif line.startswith('-'):
                current_lines.append(line[1:].strip())
            else:
                current_lines.append(line)

        if current_key:
            metadata[current_key] = '\n'.join(current_lines).strip()

        result = {
            "path": str(file_path),
            "metadata": metadata,
            "raw_header": header_text,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool(name="view_codebase", description="生成 Python 代码库的结构树，包含文件头部摘要信息")
def view_codebase(root: str = ".") -> str:
    """遍历目录，生成 Python 代码库的结构树。

    每个 .py 文件会读取其头部 docstring，提取 "摘要:" 或 "summary:" 字段
    作为简短描述，接在文件路径下方显示。

    Args:
        root: 代码库根目录路径（默认当前目录）

    Returns:
        树形结构字符串，例如：
        aitools/
        ├── server.py
        │   summary: MCP 服务器，自动发现并注册工具
        └── tools/
            ├── __init__.py
            └── wx_pusher.py
                summary: 微信推送工具
    """
    try:
        root_path = Path(root).resolve()
        if not root_path.exists():
            return f"错误: 目录不存在: {root}"

        lines = [f"{root_path.name}/"]
        py_files = sorted(root_path.rglob("*.py"))

        for i, py_file in enumerate(py_files):
            rel_path = py_file.relative_to(root_path)
            is_last = (i == len(py_files) - 1)
            prefix = "└── " if is_last else "├── "

            summary = _extract_summary(py_file)

            if summary:
                lines.append(f"{prefix}{rel_path}")
                # Continuation indent: match tree depth with spaces
                indent = " " * (len(prefix) + 4)
                lines.append(f"{indent}summary: {summary}")
            else:
                lines.append(f"{prefix}{rel_path}")

        return '\n'.join(lines)

    except Exception as e:
        return f"错误: {str(e)}"


def _extract_summary(py_file: Path) -> str:
    """提取文件头部的摘要字段（支持中英文标签）。"""
    try:
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.match(r'^(\s*)(["\']{3})(.*?)(\2)', content, re.DOTALL)
        if not match:
            return ""

        header = match.group(3)

        for pattern in [r'摘要[:：]\s*(.+?)(?:\n|$)', r'summary[:：]\s*(.+?)(?:\n|$)']:
            m = re.search(pattern, header, re.IGNORECASE)
            if m:
                return m.group(1).strip()

        return ""

    except Exception:
        return ""
