# agent

A minimal Go skeleton for a CLI-based agent that reads user input from stdin. Based on https://ampcode.com/notes/how-to-build-an-agent. 

## test-agent/main.go

- `Agent` struct holds an `apiKey`, a `getUserMessage` callback (`func() (string, bool)`), and a slice of `tools`.
- `NewAgent(apiKey, getUserMessage, tools)` constructs an `Agent`.
- `Agent.Run(ctx context.Context) error` prints a prompt (`Agent: Sudarshana ☸️ :>`), then loops: when `readUserInput` is set it reads a line from stdin and appends it to the conversation as a `user` message, calls `Agent.Infer` to get a `model` response, appends that, and prints any text parts. For each function call the model requests it prints `🔧 Calling <name>()` and runs the tool via `Agent.executeTool`, collecting the results. If the model made any function calls, the collected results are appended as a `function` message and the loop re-infers without reading stdin (so the model can act on the tool output); otherwise it reads the next user message. The loop exits when `getUserMessage` returns `false`.
- `Agent.executeTool(name, args)` runs a named tool and returns a `Part` carrying its `FunctionResponse`. It is currently a stub that always responds with `{"result": "hello, world!"}` regardless of the tool or arguments.
- `Agent.Infer(ctx context.Context, conversation []Content) (Content, error)` builds a `FunctionDeclaration` from each registered tool, POSTs the conversation (with the tools) to the Gemini `generateContent` API (`apiBase` + `model` + `:generateContent`), authenticating via the `x-goog-api-key` header, and returns a `model` `Content` reply.
- `model` is set to `gemini-2.5-flash` (a free-tier-capable model; Pro models require billing).
- `Content` and `Part` model the Gemini-style conversation shape (`Role` plus a list of `Parts`). A `Part` carries a `Text` field and optional `FunctionCall`/`FunctionResponse` fields for tool use. `Request` wraps `Contents` and an optional `Tools` list for the API call; `Response` mirrors the Gemini reply shape: a list of `Candidates` (each with a `Content` and `FinishReason`), `UsageMetadata.TotalTokenCount`, and an optional `Error` (`Code`, `Message`, `Status`).
- `main()` reads the API key from the `GEMINI_API_KEY` environment variable (exits with a message if unset), wires up a `bufio.Scanner` over `os.Stdin` as the message source, registers the available tools (`ReadFileTool`), constructs an `Agent`, and calls `Run(context.TODO())`, printing any returned error.

`Infer` parses the Gemini response: it surfaces API-level errors (`response.Error`), checks the HTTP status code, errors if no candidates are returned, and otherwise returns the first candidate's `Content` (defaulting `Role` to `"model"` if the API omits it).

## Tools

- `tool.go` defines `ToolDefinition`: a `Name`, `Description`, JSON-schema `InputSchema` (`map[string]any`), and a `Function` (`func(json.RawMessage) (string, error)`) that executes the tool.
- Tool-related wire types live in `main.go`: `FunctionDeclaration` (sent to Gemini), `FunctionCall` (the model's request, with `Args` as `json.RawMessage`), `FunctionResponse` (a tool result), and `Tool` (a list of `FunctionDeclarations`).
- `tool_read_file.go` implements `ReadFileTool` (`read_file`): it takes a relative `path` and returns the file's contents via `os.ReadFile`.

## Changelog

- `2026-06-26` — `6f5e1ed` — Add initial Go agent skeleton (main.go, go.mod)
- `2026-06-26` — `eb92cd0` — Add README documenting main.go and a commit changelog
- `2026-06-26` — `6e22698` — Make Agent.Run return an error and handle it in main
- `2026-06-26` — Move Go sources into `test-agent/`
- `2026-06-26` — Add conversation loop with `Content`/`Part` types, a stubbed `Infer`, and `GEMINI_API_KEY`-based config
- `2026-06-26` — Wire `Infer` up to call the real Gemini `generateContent` API
- `2026-06-26` — Parse the Gemini API response into the returned `Content`, handling API errors and empty candidates
- `2026-06-28` — Add tool support (`ToolDefinition`, function-call wire types) and wire the `read_file` tool into the agent
- `2026-06-28` — Execute requested tools in the loop via a stubbed `executeTool`, feeding `function` responses back so the model can continue without new user input
