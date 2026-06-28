// This file contains functions for reading files.
package main

import (
	"encoding/json"
	"os"
)

var ReadFileTool = ToolDefinition{
	Name:        "read_file",
	Description: "Read the contents of a given relative file path. Use this when you want to see what's inside a file. Do not use this with directory names.",
	InputSchema: map[string]any{
		"type": "object",
		"properties": map[string]any{
			"path": map[string]any{
				"type":        "string",
				"description": "The relative path of a file in the working directory.",
			},
		},
		"required": []string{"path"},
	},
	Function: readFile,
}

type readFileInput struct {
	Path string `json:"path"`
}

func readFile(input json.RawMessage) (string, error) {
	in := readFileInput{}
	if err := json.Unmarshal(input, &in); err != nil {
		return "", err
	}
	content, err := os.ReadFile(in.Path)
	if err != nil {
		return "", err
	}
	return string(content), nil
}
