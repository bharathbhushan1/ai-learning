# agent

A minimal Go skeleton for a CLI-based agent that reads user input from stdin.

## main.go

- `Agent` struct holds an `apiKey` and a `getUserMessage` callback (`func() (string, bool)`).
- `NewAgent(apiKey, getUserMessage)` constructs an `Agent`.
- `Agent.Run()` prints a prompt (`Agent: Sudarshana:>`) and echoes the next line read from stdin.
- `main()` wires up a `bufio.Scanner` over `os.Stdin` as the message source, constructs an `Agent` with a placeholder API key (`"test"`), and calls `Run()`.

This is currently a scaffold: input is read once and echoed back, with no real agent loop or API integration yet.

## Changelog

- `6f5e1ed` — Add initial Go agent skeleton (main.go, go.mod)
