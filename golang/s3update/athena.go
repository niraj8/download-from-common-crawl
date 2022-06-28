package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/aws/aws-sdk-go-v2/service/athena"
	"github.com/aws/aws-sdk-go-v2/service/athena/types"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func StartQueryExecution(
	ctx context.Context,
	athenaClient *athena.Client,
	s3Client *s3.Client,
	record Record,
	strContent string,
) error {
	outputLocation := fmt.Sprintf("s3://%s/results", record.S3.Bucket.Name)
	queryStartResult, err := athenaClient.StartQueryExecution(
		ctx,
		&athena.StartQueryExecutionInput{
			QueryString: &strContent,
			ResultConfiguration: &types.ResultConfiguration{
				OutputLocation: &outputLocation,
			},
		},
	)
	if err != nil {
		return fmt.Errorf("unable to start query, %v", err)
	}

	queryStartId := fmt.Sprintf("query_start/%s.txt", *queryStartResult.QueryExecutionId)
	body := fmt.Sprintf("%s\n%s", record.S3.Object.Key, strContent)
	log.Printf("queryStartId: %s", queryStartId)
	_, err = s3Client.PutObject(
		ctx,
		&s3.PutObjectInput{
			Body:   strings.NewReader(body),
			Bucket: &record.S3.Bucket.Name,
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
	bucketName string,
) error {
	queryKey := "queries/msck_repair_table_ccindex.athena"
	_, err := s3Client.PutObject(
		ctx,
		&s3.PutObjectInput{
			Body:   strings.NewReader("MSCK REPAIR TABLE ccindex"),
			Bucket: &bucketName,
			Key:    &queryKey,
		},
	)
	return err
}
