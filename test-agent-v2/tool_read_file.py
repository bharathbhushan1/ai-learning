"""The read_file tool."""

from typing import Any

from tool import ToolDefinition


def read_file(args: dict[str, Any]) -> str:
    path = args["path"]
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


ReadFileTool = ToolDefinition(
    name="read_file",
    description=(
        "Read the contents of a given relative file path. Use this when you "
        "want to see what's inside a file. Do not use this with directory names."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The relative path of a file in the working directory.",
            },
        },
        "required": ["path"],
    },
    function=read_file,
)
