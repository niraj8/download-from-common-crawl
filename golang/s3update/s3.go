package main

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"log"

	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func GetObject(
	ctx context.Context,
	s3Client *s3.Client,
	s3BucketId string,
	key string,
) ([]byte, error) {
	log.Printf("GetObject: %s", key)
	resp, err := s3Client.GetObject(ctx, &s3.GetObjectInput{
		Bucket: &s3BucketId,
		Key:    &key,
	})
	if err != nil {
		return nil, err
	}

	defer resp.Body.Close()
	if resp.ContentLength == 0 {
		return nil, fmt.Errorf("contentLength is 0")
	}

	log.Printf("ContentLength %d", resp.ContentLength)
	var bbuffer bytes.Buffer
	buffer := make([]byte, resp.ContentLength)
	for {
		num, rerr := resp.Body.Read(buffer)
		if num > 0 {
			bbuffer.Write(buffer[:num])
		} else if rerr == io.EOF || rerr != nil {
			break
		}
	}
	return bbuffer.Bytes(), nil
}
