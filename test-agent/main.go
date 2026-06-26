package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
)

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
	return Content{
		Role:  "model",
		Parts: []Part{{Text: "will do !"}},
	}, nil
}

type Content struct {
	Role  string `json:"role"`
	Parts []Part `json:"parts"`
}

type Part struct {
	Text string `json:"text,omitempty"`
}
