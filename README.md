# agent

A minimal Go skeleton for a CLI-based agent that reads user input from stdin.

## test-agent/main.go

- `Agent` struct holds an `apiKey` and a `getUserMessage` callback (`func() (string, bool)`).
- `NewAgent(apiKey, getUserMessage)` constructs an `Agent`.
- `Agent.Run() error` prints a prompt (`Agent: Sudarshana:>`) and echoes the next line read from stdin.
- `main()` wires up a `bufio.Scanner` over `os.Stdin` as the message source, constructs an `Agent` with a placeholder API key (`"test"`), calls `Run()`, and prints any returned error.

This is currently a scaffold: input is read once and echoed back, with no real agent loop or API integration yet.

## Changelog

- `6f5e1ed` — Add initial Go agent skeleton (main.go, go.mod)
- `eb92cd0` — Add README documenting main.go and a commit changelog
- `6e22698` — Make Agent.Run return an error and handle it in main
- Move Go sources into `test-agent/`
