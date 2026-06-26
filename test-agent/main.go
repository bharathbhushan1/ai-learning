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
	agent := NewAgent(apiKey, getUserMessage)
	if err := agent.Run(context.TODO()); err != nil {
		fmt.Printf("Error: %s\n", err.Error())
	}
}

type Agent struct {
	apiKey         string
	getUserMessage func() (string, bool)
}

func NewAgent(apiKey string, getUserMessage func() (string, bool)) *Agent {
	return &Agent{apiKey: apiKey, getUserMessage: getUserMessage}
}

func (a *Agent) Run(ctx context.Context) error {
	conversation := []Content{}

	fmt.Println("Agent: Sudarshana:> ")
	for {
		fmt.Print("[94mYou[0m: ")
		userInput, ok := a.getUserMessage()
		if !ok {
			break
		}
		conversation = append(conversation, Content{
			Role:  "user",
			Parts: []Part{{Text: userInput}},
		})
		modelOutput, err := a.Infer(ctx, conversation)
		if err != nil {
			return err
		}
		conversation = append(conversation, modelOutput)
		fmt.Println(conversation)
	}
	return nil
}

func (a *Agent) Infer(ctx context.Context, conversation []Content) (Content, error) {
	body, err := json.Marshal(Request{
		Contents: conversation,
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
	Text string `json:"text,omitempty"`
}

type Request struct {
	Contents []Content `json:"contents"`
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
