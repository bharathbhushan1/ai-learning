package main

import "encoding/json"

type ToolDefinition struct {
	Name        string
	Description string
	InputSchema map[string]any
	Function    func(input json.RawMessage) (string, error)
}
