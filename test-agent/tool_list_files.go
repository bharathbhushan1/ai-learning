// This file contains functions for listing files.
package main

import (
	"encoding/json"
	"os"
	"path/filepath"
)

var ListFilesTool = ToolDefinition{
	Name:        "list_files",
	Description: "List files and directories at a given path. If no path is provided, lists files in the current directory.",
	InputSchema: map[string]any{
		"type": "object",
		"properties": map[string]any{
			"path": map[string]any{
				"type":        "string",
				"description": "Optional relative path to list files from. Defaults to current directory if not provided.",
			},
		},
	},
	Function: listFiles,
}

type listFilesInput struct {
	Path string `json:"path,omitempty"`
}

func listFiles(input json.RawMessage) (string, error) {
	in := listFilesInput{}
	if len(input) > 0 {
		if err := json.Unmarshal(input, &in); err != nil {
			return "", err
		}
	}

	dir := "."
	if in.Path != "" {
		dir = in.Path
	}

	var files []string
	err := filepath.Walk(dir, func(p string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(dir, p)
		if err != nil {
			return err
		}
		if rel != "." {
			if info.IsDir() {
				files = append(files, rel+"/")
			} else {
				files = append(files, rel)
			}
		}
		return nil
	})
	if err != nil {
		return "", err
	}

	out, err := json.Marshal(files)
	if err != nil {
		return "", err
	}
	return string(out), nil
}
