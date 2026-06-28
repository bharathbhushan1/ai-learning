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
from tool_translate import TranslateTool

# Sarvam's OpenAI-compatible chat model.
MODEL = "sarvam-30b"

API_URL = "https://api.sarvam.ai/v1/chat/completions"

SYSTEM_PROMPT = "You are Sudarshana, a helpful assistant."

# The dedicated translate tool costs ~₹20/10K chars vs ~₹10/1M output tokens for
# inline chat translation — a ~100x premium that's only worth it for low-resource
# languages or when its controls (mode/script/gender) are needed. So it's off by
# default; set ENABLE_TRANSLATE_TOOL=1 to advertise it to the model. When it's
# enabled we steer the model toward it; otherwise the chat model translates inline.
TRANSLATE_TOOL_PROMPT = (
    " When the user asks for a translation, use the `translate` tool and report "
    "the `translated_text` it returns verbatim, rather than translating in your "
    "own words."
)


class Agent:
    def __init__(self, api_key: str, get_user_message, tools: list[ToolDefinition]):
        self.api_key = api_key
        self.get_user_message = get_user_message
        self.tools = tools
        self.client = httpx.Client(timeout=120.0)

    def run(self) -> None:
        system_prompt = SYSTEM_PROMPT
        if any(t.name == "translate" for t in self.tools):
            system_prompt += TRANSLATE_TOOL_PROMPT
        conversation: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]
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

        print(f"➡ \033[92m{name}\033[0m: {args_str}")
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            args = {}

        try:
            output = tool.function(args)
        except Exception as e:  # noqa: BLE001 - surface any tool failure to the model
            print(f"  \033[91m✗\033[0m {name}: {e}")
            return self._tool_result(call_id, {"error": str(e)})

        # Echo what the tool fed back to the model so retries aren't a black box.
        print(f"  \033[90m← {output}\033[0m")
        return {"role": "tool", "tool_call_id": call_id, "content": output}

    @staticmethod
    def _tool_result(call_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "role": "tool",
            "tool_call_id": call_id,
            # ensure_ascii=False so non-Latin scripts reach the model intact.
            "content": json.dumps(payload, ensure_ascii=False),
        }

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

        print(f"➡ \033[92m\033[0m: LLM call")
        # The endpoint is stateless: the system prompt and full tool set are part
        # of this request body on *every* call, not just the first. Set DEBUG=1 to
        # print the actual request each turn. (Gated so it doesn't clutter runs.)
        if os.getenv("DEBUG"):
            self._log_request(body)
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

        self._log_usage(data.get("usage") or {})

        message = choices[0]["message"]
        message.setdefault("role", "assistant")
        return message

    @staticmethod
    def _log_request(body: dict[str, Any]) -> None:
        """Pretty-print the actual request body going to the LLM.

        Renders each message as `[role] content` and lists the advertised tools,
        so it's obvious that the system prompt + full tool set ride along on every
        call. Long content is trimmed (with the original length shown) to keep the
        dump readable rather than faithful to the last byte.
        """
        dim, reset = "\033[90m", "\033[0m"

        def trim(text: str, limit: int = 300) -> str:
            text = text.replace("\n", " ")
            if len(text) <= limit:
                return text
            return f"{text[:limit]}… (+{len(text) - limit} more chars)"

        messages = body.get("messages") or []
        tools = body.get("tools") or []
        print(f"{dim}  ⇡ Request to {body.get('model')}:{reset}")
        print(f"{dim}    messages ({len(messages)}):{reset}")
        for msg in messages:
            role = msg.get("role", "?")
            content = msg.get("content")
            if content:
                print(f"{dim}      [{role:9}] {trim(content)}{reset}")
            else:
                print(f"{dim}      [{role:9}] (no text content){reset}")
            # Surface the structured bits a plain `content` print would hide.
            for call in msg.get("tool_calls") or []:
                fn = call.get("function", {})
                print(
                    f"{dim}                  → tool_call {fn.get('name')}"
                    f"({trim(fn.get('arguments') or '', 120)}){reset}"
                )
            if msg.get("tool_call_id"):
                print(
                    f"{dim}                  ↳ result for {msg['tool_call_id']}{reset}"
                )
        tool_names = ", ".join(t["function"]["name"] for t in tools)
        print(f"{dim}    tools ({len(tools)}): {tool_names}{reset}")

    @staticmethod
    def _log_usage(usage: dict[str, Any]) -> None:
        if not usage:
            return
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        print(
            f"  \033[90m← usage: prompt={prompt_tokens} "
            f"completion={completion_tokens}\033[0m"
        )


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
    # Opt-in only: the translate tool is expensive (see TRANSLATE_TOOL_PROMPT).
    if os.getenv("ENABLE_TRANSLATE_TOOL"):
        tools.append(TranslateTool)
    agent = Agent(api_key, get_user_message, tools)
    try:
        agent.run()
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
