# test-agent-v2

A minimal CLI agent in Python, managed with [uv](https://docs.astral.sh/uv/).
It is a port of the Go [`test-agent`](../test-agent) and keeps the same
functionality — a stdin-driven conversation loop with file tools — but targets
the **Sarvam API** instead of Gemini.

## Why a different backend looks similar

Sarvam exposes an **OpenAI-compatible** `POST /v1/chat/completions` endpoint, so
the wire format is the standard OpenAI chat shape rather than Gemini's
`contents`/`parts` shape:

| | Go `test-agent` (Gemini) | `test-agent-v2` (Sarvam) |
| --- | --- | --- |
| Endpoint | `…/models/{model}:generateContent` | `https://api.sarvam.ai/v1/chat/completions` |
| Auth | `x-goog-api-key` header | `Authorization: Bearer <key>` header |
| Model | `gemini-2.5-flash-lite` | `sarvam-30b` |
| Conversation | `contents` of `{role, parts}` | `messages` of `{role, content, …}` |
| Roles | `user`, `model` only | `system`, `user`, `assistant`, `tool` |
| Tool advertise | `tools[].functionDeclarations[]` | `tools[].{type:"function", function:{…}}` |
| Tool call | a `Part.functionCall` on the model turn | `tool_calls[]` on the assistant message |
| Tool result | a `functionResponse` part in a `user` turn | a dedicated `tool` message keyed by `tool_call_id` |
| API key env | `GEMINI_API_KEY` | `SARVAM_API_KEY` |

## Setup

```sh
cd test-agent-v2
uv sync
export SARVAM_API_KEY=...   # your Sarvam subscription key
```

## Run

```sh
uv run main.py
```

You'll get a `You:` prompt. Type a message and the agent (`Sudarshana ☸️`) will
reply, calling tools as needed. Ctrl-D (EOF) exits.

## Files

- `main.py` — entry point plus the `Agent` class. `Agent.run()` drives the
  loop: read a line from stdin, append it as a `user` message, call
  `Agent.infer()` for the assistant reply, print any text, and run any
  `tool_calls`. Each tool result is appended as a `tool` message and the loop
  re-infers (without reading stdin) so the model can act on the output;
  otherwise it reads the next user line. EOF exits.
  - `Agent.infer()` builds the OpenAI `tools` array from the registered tools,
    POSTs the conversation to Sarvam's `/v1/chat/completions` with
    `Authorization: Bearer`, surfaces API/HTTP errors, and returns the first
    choice's assistant `message`.
  - `Agent.execute_tool()` looks up the named tool, parses its JSON
    `arguments`, runs it, and returns a `tool` message carrying the result (or
    an `{"error": …}` payload on failure / unknown tool).
- `tool.py` — the `ToolDefinition` dataclass (`name`, `description`,
  JSON-schema `input_schema`, and a `function(args: dict) -> str`).
- `tool_read_file.py` — `read_file`: returns the contents of a relative path.
- `tool_list_files.py` — `list_files`: returns a JSON array of files and
  directories beneath an (optional) path, walking the tree; directory entries
  are suffixed with `/`.
- `tool_edit_file.py` — `edit_file`: replaces `old_str` with `new_str` in a
  file. Creates the file (and parent dirs) when it doesn't exist and `old_str`
  is empty; errors when `old_str` equals `new_str` or isn't found.
- `tool_translate.py` — `translate`: translates text between Indian languages
  (and English) via Sarvam's dedicated `POST /translate` model
  (`sarvam-translate:v1`). Unlike the chat loop it authenticates with the
  `api-subscription-key` header and reads `SARVAM_API_KEY` itself. Exposes
  optional `mode` (formal/colloquial/code-mixed) and `output_script` controls
  the chat path lacks.

## Changelog

- `2026-06-28` — Initial Python port of `test-agent` targeting the Sarvam
  OpenAI-compatible chat completions API, managed with uv.
- `2026-06-28` — Switch model to `sarvam-30b` (`sarvam-m` is deprecated);
  tool calling confirmed working with `Authorization: Bearer` auth.
- `2026-06-28` — Add the `translate` tool, calling Sarvam's dedicated
  `/translate` endpoint (`sarvam-translate:v1`) with the `api-subscription-key`
  header.
