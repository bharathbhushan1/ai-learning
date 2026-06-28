"""A minimal CLI agent that talks to the Sarvam API.

This is a Python port of the Go `test-agent`. Functionally it is the same:
a stdin-driven conversation loop that lets the model call file tools
(`read_file`, `list_files`, `edit_file`) and feeds the results back.

The one difference is the backend. Where the Go agent targets Google's
Gemini `generateContent` API, this one targets Sarvam, whose
`/v1/chat/completions` endpoint is OpenAI-compatible. That means the wire
shape is the standard OpenAI chat format: a flat list of `messages` with
`system`/`user`/`assistant`/`tool` roles, `tools` advertised as
`{"type": "function", "function": {...}}`, and tool calls returned on the
assistant message as `tool_calls` (with a `tool` message carrying each
result back, keyed by `tool_call_id`).
"""

import json
import os
import sys
from typing import Any

import httpx

from tool import ToolDefinition
from tool_edit_file import EditFileTool
from tool_list_files import ListFilesTool
from tool_read_file import ReadFileTool

# Sarvam's OpenAI-compatible chat model.
MODEL = "sarvam-30b"

API_URL = "https://api.sarvam.ai/v1/chat/completions"


class Agent:
    def __init__(self, api_key: str, get_user_message, tools: list[ToolDefinition]):
        self.api_key = api_key
        self.get_user_message = get_user_message
        self.tools = tools
        self.client = httpx.Client(timeout=120.0)

    def run(self) -> None:
        conversation: list[dict[str, Any]] = []
        read_user_input = True

        print("Agent: Sudarshana ☸️ :> ")
        while True:
            if read_user_input:
                user_input, ok = self.get_user_message()
                if not ok:
                    break
                conversation.append({"role": "user", "content": user_input})

            message = self.infer(conversation)
            conversation.append(message)

            if message.get("content"):
                print(f"\U0001f9e0 \033[93m{MODEL}\033[0m: {message['content']}\n")

            tool_calls = message.get("tool_calls") or []
            if not tool_calls:
                read_user_input = True
                continue

            read_user_input = False
            for tool_call in tool_calls:
                conversation.append(self.execute_tool(tool_call))

    def execute_tool(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        call_id = tool_call.get("id", "")
        name = tool_call["function"]["name"]
        args_str = tool_call["function"].get("arguments") or "{}"

        tool = next((t for t in self.tools if t.name == name), None)
        if tool is None:
            return self._tool_result(call_id, {"error": f"tool not found: {name}"})

        print(f"➡ \033[92m{name}\033[0m: {args_str}\n")
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            args = {}

        try:
            output = tool.function(args)
        except Exception as e:  # noqa: BLE001 - surface any tool failure to the model
            return self._tool_result(call_id, {"error": str(e)})

        return {"role": "tool", "tool_call_id": call_id, "content": output}

    @staticmethod
    def _tool_result(call_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"role": "tool", "tool_call_id": call_id, "content": json.dumps(payload)}

    def infer(self, conversation: list[dict[str, Any]]) -> dict[str, Any]:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema,
                },
            }
            for t in self.tools
        ]

        body = {
            "model": MODEL,
            "messages": conversation,
            "tools": tools,
        }

        resp = self.client.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=body,
        )

        try:
            data = resp.json()
        except ValueError:
            raise RuntimeError(f"sarvam returned {resp.status_code}: {resp.text}")

        if isinstance(data.get("error"), dict):
            err = data["error"]
            raise RuntimeError(
                f"sarvam error: {err.get('message', err)}"
            )
        if resp.status_code != 200:
            raise RuntimeError(f"sarvam returned {resp.status_code}: {resp.text}")

        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"no choices returned: {resp.text}")

        message = choices[0]["message"]
        message.setdefault("role", "assistant")
        return message


def main() -> None:
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        print("Set SARVAM_API_KEY")
        return

    def get_user_message() -> tuple[str, bool]:
        sys.stdout.write("\033[94mYou\033[0m: ")
        sys.stdout.flush()
        line = sys.stdin.readline()
        if line == "":  # EOF
            return "", False
        return line.rstrip("\n"), True

    tools = [ReadFileTool, ListFilesTool, EditFileTool]
    agent = Agent(api_key, get_user_message, tools)
    try:
        agent.run()
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
