package main

import (
	"context"
	"log"
	"strings"

	"example.com/s3update/types"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/athena"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func HandleRequest(ctx context.Context, event types.LambdaEvent) error {
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
		log.Printf("key: %s", record.S3.Object.Key)
		if strings.HasPrefix(record.S3.Object.Key, "queries/") {
			content, err := GetObject(ctx, s3Client, record.S3.Bucket.Name, record.S3.Object.Key)
			if err != nil {
				log.Fatalf("unable to get %s object, %v", record.S3.Object.Key, err)
			}

			strContent := string(content)
			err = StartQueryExecution(ctx, athenaClient, s3Client, record.S3, strContent)
			if err != nil {
				log.Fatalf("unable to start query, %v", err)
			}

			continue
		}

		if strings.HasPrefix(record.S3.Object.Key, "results/") {
			if strings.HasSuffix(record.S3.Object.Key, ".txt") {
				content, err := GetObject(ctx, s3Client, record.S3.Bucket.Name, record.S3.Object.Key)
				if err != nil {
					log.Fatalf("unable to get %s object, %v", record.S3.Object.Key, err)
				}

				strContent := string(content)
				if strContent == "" {
					err = StartRepairTable(ctx, s3Client, record)
					if err != nil {
						log.Fatalf("unable to start repair table, %v", err)
					}
				}

				continue
			}

			if strings.HasSuffix(record.S3.Object.Key, ".csv") {
				err = DownloadWarc(ctx, s3Client, record.S3)
				if err != nil {
					log.Fatalf("unable to download warc, %v", err)
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
