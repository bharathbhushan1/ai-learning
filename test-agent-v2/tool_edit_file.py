"""The edit_file tool."""

import os
from typing import Any

from tool import ToolDefinition


def _create_new_file(path: str, content: str) -> str:
    directory = os.path.dirname(path)
    if directory and directory != ".":
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully created file {path}"


def edit_file(args: dict[str, Any]) -> str:
    path = args.get("path", "")
    old_str = args.get("old_str", "")
    new_str = args.get("new_str", "")

    if path == "" or old_str == new_str:
        raise ValueError("invalid input parameters")

    if not os.path.exists(path):
        if old_str == "":
            return _create_new_file(path, new_str)
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8") as f:
        old_content = f.read()

    new_content = old_content.replace(old_str, new_str)

    if old_content == new_content and old_str != "":
        raise ValueError("old_str not found in file")

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return "OK"


EditFileTool = ToolDefinition(
    name="edit_file",
    description=(
        "Make edits to a text file.\n\n"
        "Replaces 'old_str' with 'new_str' in the given file. 'old_str' and "
        "'new_str' MUST be different from each other.\n\n"
        "If the file specified with path doesn't exist, it will be created."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file",
            },
            "old_str": {
                "type": "string",
                "description": "Text to search for - must match exactly and must only have one match exactly",
            },
            "new_str": {
                "type": "string",
                "description": "Text to replace old_str with",
            },
        },
        "required": ["path", "new_str"],
    },
    function=edit_file,
)
