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
	agent.Run()
}

type Agent struct {
	apiKey         string
	getUserMessage func() (string, bool)
}

func NewAgent(apiKey string, getUserMessage func() (string, bool)) *Agent {
	return &Agent{apiKey: apiKey, getUserMessage: getUserMessage}
}

func (a *Agent) Run() {
	fmt.Println("Agent: Sudarshana:> ")
	fmt.Println(a.getUserMessage())
}
