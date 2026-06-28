"""Shared tool abstraction.

A ToolDefinition bundles the metadata Sarvam needs to advertise a tool
(name, description, JSON-schema parameters) together with the Python callable
that actually runs it. The callable takes the already-parsed arguments dict and
returns a string result (or raises on failure).
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    function: Callable[[dict[str, Any]], str]
