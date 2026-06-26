package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	getUserMessage := func() (string, bool) {
		if !scanner.Scan() {
			return "", false
		}
		return scanner.Text(), true
	}
	agent := NewAgent("test", getUserMessage)
	if err := agent.Run(); err != nil {
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

func (a *Agent) Run() error {
	fmt.Println("Agent: Sudarshana:> ")
	fmt.Println(a.getUserMessage())
	return nil
}
