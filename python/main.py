import gzip
import io
import os
import boto3

from athena import AthenaQuery, Athena
from commoncrawl import CommonCrawlQuery
from dotenv import load_dotenv

load_dotenv()


S3_RESULTS_BUCKET_NAME = os.getenv("S3_RESULTS_BUCKET_NAME")


def result_size(s3_client, query_execution_id):
    response = s3_client.get_object(
        Bucket=S3_RESULTS_BUCKET_NAME,
        Key="results/" + query_execution_id + ".csv",
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return len(response["Body"].read().split(b"\n")) - 2
    else:
        raise RuntimeError("Failed to get results from s3", response)


def get_warc_file_keys(s3_client, query_execution_id):
    result_row_count = result_size(s3_client, query_execution_id)
    print("Result row count:", result_row_count)

    #  list all objects in the warc_segment folder
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(
        Bucket=S3_RESULTS_BUCKET_NAME,
        Prefix="warc_segment/" + query_execution_id + ".csv/",
    )

    warc_file_s3_keys = []

    for page in pages:
        for obj in page["Contents"]:
            warc_file_s3_keys.append(obj["Key"])

    if len(warc_file_s3_keys) != result_row_count:
        print(
            "warning: Result row count:{} does not match warc file count:{}".format(
                result_row_count, len(warc_file_s3_keys)
            )
        )

    return warc_file_s3_keys


def get_uncompressed_warc_file_content_from_s3_key(s3_client, s3_key):
    response = s3_client.get_object(Bucket=S3_RESULTS_BUCKET_NAME, Key=s3_key)
    # raise exception if response is not 200
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise RuntimeError("Failed to get warc file from s3", response)

    content = response["Body"].read()
    return gzip.GzipFile(fileobj=io.BytesIO(content)).read()


def main():
    print("Using S3 bucket for results:", S3_RESULTS_BUCKET_NAME)
    athena = Athena(boto3.client("athena"))

    query = AthenaQuery(
        CommonCrawlQuery(
            crawl="CC-MAIN-2020-24",
            urls=["twitter.com"],
            url_path="/robots.txt",
            fetch_status=200,
            limit=1,
        )
    )

    output_location = "s3://{}/results".format(S3_RESULTS_BUCKET_NAME)
    query_execution_id = athena.execute_query(query.get_query_string(), output_location)
    print("Athena query execution id:", query_execution_id)

    query_status = athena.poll_query_execution_status(query_execution_id)
    if query_status["State"] == "FAILED" or query_status["State"] == "CANCELLED":
        raise RuntimeError("Query failed or cancelled:", query_status)

    s3_client = boto3.client("s3")
    warc_file_s3_urls = get_warc_file_keys(s3_client, query_execution_id)

    for warc_s3_key in warc_file_s3_urls:
        print(warc_s3_key)

    warc_file_content = get_uncompressed_warc_file_content_from_s3_key(
        s3_client, warc_file_s3_urls[0]
    )
    print(warc_file_content)


main()

# query_execution_id = "d9625e4b-4fcf-4b40-86e2-a9ab152fbc29"

# s3_client = boto3.client("s3")
# warc_file_s3_urls = get_warc_file_keys(s3_client, query_execution_id)
# print(get_uncompressed_warc_file_content_from_s3_key(s3_client, warc_file_s3_urls[0]))
