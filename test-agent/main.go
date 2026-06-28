package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

// Free-tier capable models: gemini-2.5-flash, gemini-2.5-flash-lite.
// (Pro models require billing.)
const model = "gemini-2.5-flash"

const apiBase = "https://generativelanguage.googleapis.com/v1beta/models/"

func main() {
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		fmt.Println("Set GEMINI_API_KEY")
		return
	}

	scanner := bufio.NewScanner(os.Stdin)
	getUserMessage := func() (string, bool) {
		if !scanner.Scan() {
			return "", false
		}
		return scanner.Text(), true
	}
	tools := []ToolDefinition{ReadFileTool}
	agent := NewAgent(apiKey, getUserMessage, tools)
	if err := agent.Run(context.TODO()); err != nil {
		fmt.Printf("Error: %s\n", err.Error())
	}
}

type Agent struct {
	apiKey         string
	getUserMessage func() (string, bool)
	tools          []ToolDefinition
}

func NewAgent(apiKey string, getUserMessage func() (string, bool), tools []ToolDefinition) *Agent {
	return &Agent{apiKey: apiKey, getUserMessage: getUserMessage, tools: tools}
}

func (a *Agent) Run(ctx context.Context) error {
	conversation := []Content{}
	readUserInput := true

	fmt.Println("Agent: Sudarshana ☸️ :> ")
	for {
		if readUserInput {
			fmt.Print("[94mYou[0m: ")
			userInput, ok := a.getUserMessage()
			if !ok {
				break
			}
			conversation = append(conversation, Content{
				Role:  "user",
				Parts: []Part{{Text: userInput}},
			})
		}
		modelOutput, err := a.Infer(ctx, conversation)
		if err != nil {
			return err
		}
		conversation = append(conversation, modelOutput)
		fmt.Println(conversation)

		var functionResponses []Part
		for _, p := range modelOutput.Parts {
			if strings.TrimSpace(p.Text) != "" {
				fmt.Printf("> [93m%s[0m: %s\n\n", model, p.Text)
			}
			if p.FunctionCall != nil {
				fmt.Println("🔧 Calling " + p.FunctionCall.Name + "()")
				result := a.executeTool(p.FunctionCall.Name, p.FunctionCall.Args)
				functionResponses = append(functionResponses, result)
			}
		}

		if len(functionResponses) == 0 {
			readUserInput = true
		} else {
			readUserInput = false
			conversation = append(conversation, Content{
				Role:  "function",
				Parts: functionResponses,
			})
		}
	}
	return nil
}

func (a *Agent) executeTool(name string, _ json.RawMessage) Part {
	return Part{
		FunctionResponse: &FunctionResponse{
			Name:     name,
			Response: map[string]any{"result": "hello, world!"},
		},
	}

}

func (a *Agent) Infer(ctx context.Context, conversation []Content) (Content, error) {
	fmt.Println("🧠 Calling LLM")
	functionDeclarations := make([]FunctionDeclaration, 0, len(a.tools))
	for _, t := range a.tools {
		functionDeclarations = append(functionDeclarations, FunctionDeclaration{
			Name:        t.Name,
			Description: t.Description,
			Parameters:  t.InputSchema,
		})
	}

	body, err := json.Marshal(Request{
		Contents: conversation,
		Tools:    []Tool{{FunctionDeclarations: functionDeclarations}},
	})
	if err != nil {
		return Content{}, err
	}
	url := apiBase + model + ":generateContent"
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return Content{}, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-goog-api-key", a.apiKey)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return Content{}, err
	}
	defer resp.Body.Close()
	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return Content{}, err
	}

	var response Response
	if err := json.Unmarshal(raw, &response); err != nil {
		return Content{}, err
	}
	if response.Error != nil {
		return Content{}, fmt.Errorf("gemini error %d (%s): %s",
			response.Error.Code, response.Error.Status, response.Error.Message)
	}
	if resp.StatusCode != http.StatusOK {
		return Content{}, fmt.Errorf("gemini returned %d: %s", resp.StatusCode, string(raw))
	}
	if len(response.Candidates) == 0 {
		return Content{}, fmt.Errorf("no candidates returned: %s", string(raw))
	}

	// b, _ := json.MarshalIndent(response, "", "  ")
	// fmt.Println(string(b))

	c := response.Candidates[0].Content
	if c.Role == "" {
		c.Role = "model"
	}
	return c, nil
}

type Content struct {
	Role  string `json:"role"`
	Parts []Part `json:"parts"`
}

type Part struct {
	Text             string            `json:"text,omitempty"`
	FunctionCall     *FunctionCall     `json:"functionCall,omitempty"`
	FunctionResponse *FunctionResponse `json:"functionResponse,omitempty"`
}

type Request struct {
	Contents []Content `json:"contents"`
	Tools    []Tool    `json:"tools,omitempty"`
}

type Response struct {
	Candidates []struct {
		Content      Content `json:"content"`
		FinishReason string  `json:"finishReason"`
	} `json:"candidates"`

	UsageMetadata struct {
		TotalTokenCount int `json:"totalTokenCount"`
	} `json:"usageMetadata"`

	Error *struct {
		Code    int    `json:"code"`
		Message string `json:"message"`
		Status  string `json:"status"`
	} `json:"error,omitempty"`
}

// Tool related abstractions
type FunctionDeclaration struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Parameters  map[string]any `json:"parameters"`
}

type FunctionCall struct {
	Name string `json:"name"`
	// Gemini returns args as a JSON object, which flows straight into our
	// tool functions that unmarshal from json.RawMessage.
	Args json.RawMessage `json:"args,omitempty"`
}

type FunctionResponse struct {
	Name     string         `json:"name"`
	Response map[string]any `json:"response"`
}

type Tool struct {
	FunctionDeclarations []FunctionDeclaration `json:"functionDeclarations"`
}
