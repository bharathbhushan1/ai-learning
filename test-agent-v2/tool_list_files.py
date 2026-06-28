"""The list_files tool."""

import json
import os
from typing import Any

from tool import ToolDefinition


def list_files(args: dict[str, Any]) -> str:
    dir_path = args.get("path") or "."

    files: list[str] = []
    for root, dirnames, filenames in os.walk(dir_path):
        for name in dirnames:
            rel = os.path.relpath(os.path.join(root, name), dir_path)
            files.append(rel + "/")
        for name in filenames:
            rel = os.path.relpath(os.path.join(root, name), dir_path)
            files.append(rel)

    return json.dumps(files)


ListFilesTool = ToolDefinition(
    name="list_files",
    description=(
        "List files and directories at a given path. If no path is provided, "
        "lists files in the current directory."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "Optional relative path to list files from. Defaults to "
                    "current directory if not provided."
                ),
            },
        },
    },
    function=list_files,
)
