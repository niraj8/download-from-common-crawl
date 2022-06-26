package main

import (
	"context"
	"fmt"

	"github.com/aws/aws-lambda-go/lambda"
)

func HandleRequest(ctx context.Context, event LambdaEvent) error {
	fmt.Printf("Hello %+v!", event)
	return nil
}

func main() {
	lambda.Start(HandleRequest)
}
