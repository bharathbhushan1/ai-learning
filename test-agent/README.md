# agent

A minimal Go skeleton for a CLI-based agent that reads user input from stdin.

## test-agent/main.go

- `Agent` struct holds an `apiKey` and a `getUserMessage` callback (`func() (string, bool)`).
- `NewAgent(apiKey, getUserMessage)` constructs an `Agent`.
- `Agent.Run(ctx context.Context) error` prints a prompt (`Agent: Sudarshana:>`), then loops: reads a line from stdin, appends it to the conversation as a `user` message, calls `Agent.Infer` to get a `model` response, appends that, and prints the conversation so far. The loop exits when `getUserMessage` returns `false`.
- `Agent.Infer(ctx context.Context, conversation []Content) (Content, error)` POSTs the conversation to the Gemini `generateContent` API (`apiBase` + `model` + `:generateContent`), authenticating via the `x-goog-api-key` header, and returns a `model` `Content` reply.
- `model` is set to `gemini-2.5-flash` (a free-tier-capable model; Pro models require billing).
- `Content` and `Part` model the Gemini-style conversation shape (`Role` plus a list of `Parts`, each with a `Text` field). `Request` wraps `Contents` for the API call; `Response` is currently an empty placeholder for the API's reply shape.
- `main()` reads the API key from the `GEMINI_API_KEY` environment variable (exits with a message if unset), wires up a `bufio.Scanner` over `os.Stdin` as the message source, constructs an `Agent`, and calls `Run(context.TODO())`, printing any returned error.

`Infer` now makes a real call to the Gemini API, though the response is not yet parsed into the returned `Content` (it still returns a fixed `"will do!"` text).

## Changelog

- `6f5e1ed` — Add initial Go agent skeleton (main.go, go.mod)
- `eb92cd0` — Add README documenting main.go and a commit changelog
- `6e22698` — Make Agent.Run return an error and handle it in main
- Move Go sources into `test-agent/`
- Add conversation loop with `Content`/`Part` types, a stubbed `Infer`, and `GEMINI_API_KEY`-based config
- Wire `Infer` up to call the real Gemini `generateContent` API
