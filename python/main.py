import os
import boto3

from athena import AthenaQuery, Athena
from commoncrawl import CommonCrawlQuery
from constants import S3_RESULTS_BUCKET_NAME, AWS_REGION

from query_results import get_uncompressed_warc_file_content_from_s3_key, query_results

def main():
    print("Using S3 bucket for results:", S3_RESULTS_BUCKET_NAME)
    athena = Athena(boto3.client("athena", region_name=AWS_REGION))

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
    results = query_results(s3_client, S3_RESULTS_BUCKET_NAME, query_execution_id)
    for row in results:
        if len(row) == 3:
            print(row)
            warc_file_content = get_uncompressed_warc_file_content_from_s3_key(
                s3_client, row[0], int(row[1]), int(row[2])
            )
            # TODO do something with warc_file_content
            print(warc_file_content)

main()
