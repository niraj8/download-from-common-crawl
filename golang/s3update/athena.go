package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"example.com/s3update/types"
	"github.com/aws/aws-sdk-go-v2/service/athena"
	athenaTypes "github.com/aws/aws-sdk-go-v2/service/athena/types"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func StartQueryExecution(
	ctx context.Context,
	athenaClient *athena.Client,
	s3Client *s3.Client,
	s3Record types.S3,
	strContent string,
) error {
	outputLocation := fmt.Sprintf("s3://%s/results", s3Record.Bucket.Name)
	queryStartResult, err := athenaClient.StartQueryExecution(
		ctx,
		&athena.StartQueryExecutionInput{
			QueryString: &strContent,
			ResultConfiguration: &athenaTypes.ResultConfiguration{
				OutputLocation: &outputLocation,
			},
		},
	)
	if err != nil {
		return fmt.Errorf("unable to start query, %v", err)
	}

	queryStartId := fmt.Sprintf("query_start/%s.txt", *queryStartResult.QueryExecutionId)
	body := fmt.Sprintf("%s\n%s", s3Record.Object.Key, strContent)
	log.Printf("queryStartId: %s", queryStartId)
	_, err = s3Client.PutObject(
		ctx,
		&s3.PutObjectInput{
			Body:   strings.NewReader(body),
			Bucket: &s3Record.Bucket.Name,
			Key:    &queryStartId,
		},
	)
	if err != nil {
		return fmt.Errorf("unable to save query execution id, %v", err)
	}

	return nil
}

func StartRepairTable(
	ctx context.Context,
	s3Client *s3.Client,
	record types.Record,
) error {
	queryStartKey := strings.Split(record.S3.Object.Key, "/")[1]
	queryStartKey = fmt.Sprintf("query_start/%s", queryStartKey)
	content, err := GetObject(ctx, s3Client, record.S3.Bucket.Name, queryStartKey)
	if err != nil {
		log.Fatalf("unable to get %s object, %v", queryStartKey, err)
	}

	queryKey := string(content)
	queryKey = strings.Split(queryKey, "\n")[0]
	if queryKey != "queries/create_ccindex.athena" {
		return nil
	}

	queryKey = "queries/msck_repair_table_ccindex.athena"
	_, err = s3Client.PutObject(
		ctx,
		&s3.PutObjectInput{
			Body:   strings.NewReader("MSCK REPAIR TABLE ccindex"),
			Bucket: &record.S3.Bucket.Name,
			Key:    &queryKey,
		},
	)
	return err
}
