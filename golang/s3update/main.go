package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/athena"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func HandleRequest(ctx context.Context, event LambdaEvent) error {
	log.Printf("Hello %+v!", event)
	if len(event.Records) == 0 {
		log.Fatalf("no records")
	}

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		log.Fatalf("unable to load SDK config, %v", err)
	}

	athenaClient := athena.NewFromConfig(cfg)
	s3Client := s3.NewFromConfig(cfg)
	for _, record := range event.Records {
		content, err := GetObject(ctx, s3Client, record.S3.Bucket.Name, record.S3.Object.Key)
		strContent := ""
		if err == nil {
			strContent = string(content)
		} else if err.Error() != "contentLength is 0" {
			log.Fatalf("unable to get %s object, %v", record.S3.Object.Key, err)
		}

		if strings.HasPrefix(record.S3.Object.Key, "queries/") {
			err = StartQueryExecution(ctx, athenaClient, s3Client, record, strContent)
			if err != nil {
				log.Fatalf("unable to start query, %v", err)
			}

			continue
		}

		if strings.HasPrefix(record.S3.Object.Key, "results/") && strings.HasSuffix(record.S3.Object.Key, ".txt") {
			if strContent == "" {
				queryStartKey := strings.Split(record.S3.Object.Key, "/")[1]
				queryStartKey = fmt.Sprintf("query_start/%s", queryStartKey)
				content, err = GetObject(ctx, s3Client, record.S3.Bucket.Name, queryStartKey)
				if err != nil {
					log.Fatalf("unable to get %s object, %v", queryStartKey, err)
				}

				queryKey := string(content)
				queryKey = strings.Split(queryKey, "\n")[0]
				if queryKey == "queries/create_ccindex.athena" {
					err = StartRepairTable(ctx, s3Client, record.S3.Bucket.Name)
					if err != nil {
						log.Fatalf("unable to start query, %v", err)
					}
				}
			}

			continue
		}
	}

	return nil
}

func main() {
	lambda.Start(HandleRequest)
}
