# agent

A minimal Go skeleton for a CLI-based agent that reads user input from stdin.

## test-agent/main.go

- `Agent` struct holds an `apiKey` and a `getUserMessage` callback (`func() (string, bool)`).
- `NewAgent(apiKey, getUserMessage)` constructs an `Agent`.
- `Agent.Run(ctx context.Context) error` prints a prompt (`Agent: Sudarshana:>`), then loops: reads a line from stdin, appends it to the conversation as a `user` message, calls `Agent.Infer` to get a `model` response, appends that, and prints the conversation so far. The loop exits when `getUserMessage` returns `false`.
- `Agent.Infer(ctx context.Context, conversation []Content) (Content, error)` is currently a stub that always returns a fixed `model` reply (`"will do !"`); no real API call is wired up yet.
- `Content` and `Part` model the Gemini-style conversation shape (`Role` plus a list of `Parts`, each with a `Text` field).
- `main()` reads the API key from the `GEMINI_API_KEY` environment variable (exits with a message if unset), wires up a `bufio.Scanner` over `os.Stdin` as the message source, constructs an `Agent`, and calls `Run(context.TODO())`, printing any returned error.

This is currently a scaffold: the conversation loop and message shapes are in place, but `Infer` doesn't call a real model yet.

## Changelog

- `6f5e1ed` — Add initial Go agent skeleton (main.go, go.mod)
- `eb92cd0` — Add README documenting main.go and a commit changelog
- `6e22698` — Make Agent.Run return an error and handle it in main
- Move Go sources into `test-agent/`
- Add conversation loop with `Content`/`Part` types, a stubbed `Infer`, and `GEMINI_API_KEY`-based config
