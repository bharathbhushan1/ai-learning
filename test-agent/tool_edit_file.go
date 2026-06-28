// This file contains functions for editing files.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path"
	"strings"
)

var EditFileTool = ToolDefinition{
	Name: "edit_file",
	Description: `Make edits to a text file.

Replaces 'old_str' with 'new_str' in the given file. 'old_str' and 'new_str' MUST be different from each other.

If the file specified with path doesn't exist, it will be created.`,
	InputSchema: map[string]any{
		"type": "object",
		"properties": map[string]any{
			"path": map[string]any{
				"type":        "string",
				"description": "The path to the file",
			},
			"old_str": map[string]any{
				"type":        "string",
				"description": "Text to search for - must match exactly and must only have one match exactly",
			},
			"new_str": map[string]any{
				"type":        "string",
				"description": "Text to replace old_str with",
			},
		},
		"required": []string{"path", "new_str"},
	},
	Function: editFile,
}

type editFileInput struct {
	Path   string `json:"path"`
	OldStr string `json:"old_str"`
	NewStr string `json:"new_str"`
}

func editFile(input json.RawMessage) (string, error) {
	in := editFileInput{}
	if err := json.Unmarshal(input, &in); err != nil {
		return "", err
	}

	if in.Path == "" || in.OldStr == in.NewStr {
		return "", fmt.Errorf("invalid input parameters")
	}

	content, err := os.ReadFile(in.Path)
	if err != nil {
		if os.IsNotExist(err) && in.OldStr == "" {
			return createNewFile(in.Path, in.NewStr)
		}
		return "", err
	}

	oldContent := string(content)
	newContent := strings.Replace(oldContent, in.OldStr, in.NewStr, -1)

	if oldContent == newContent && in.OldStr != "" {
		return "", fmt.Errorf("old_str not found in file")
	}

	if err := os.WriteFile(in.Path, []byte(newContent), 0644); err != nil {
		return "", err
	}
	return "OK", nil
}

func createNewFile(filePath, content string) (string, error) {
	dir := path.Dir(filePath)
	if dir != "." {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return "", fmt.Errorf("failed to create directory: %w", err)
		}
	}
	if err := os.WriteFile(filePath, []byte(content), 0644); err != nil {
		return "", fmt.Errorf("failed to create file: %w", err)
	}
	return fmt.Sprintf("Successfully created file %s", filePath), nil
}
