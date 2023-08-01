import boto3

from io import BytesIO
from athena import AthenaQuery, Athena
from commoncrawl import CommonCrawlQuery
from constants import S3_RESULTS_BUCKET_NAME, AWS_REGION

from query_results import get_warc, query_results


def main():
    print("Using S3 bucket for results:", S3_RESULTS_BUCKET_NAME)
    athena = Athena(boto3.client("athena", region_name=AWS_REGION))
    s3_client = boto3.client("s3")

    query = AthenaQuery(
        CommonCrawlQuery(
            crawl="CC-MAIN-2020-24",
            urls=["twitter.com"],
            url_path="/robots.txt",
            fetch_status=200,
            limit=1,
        )
    )

    results = query_results(athena, s3_client, query)
    for row in results:
        print("start processing:", row)
        warc_object = get_warc(s3_client, row[0], int(row[1]), int(row[2]))
        # TODO do something with warc_object

        print(warc_object)
        print(warc_object.rec_headers)
        print(warc_object.content_stream().read())


main()
