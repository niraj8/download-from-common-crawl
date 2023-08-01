import csv
from io import BytesIO
from warcio.archiveiterator import WARCIterator

from constants import S3_RESULTS_BUCKET_NAME


def query_results(athena, s3_client, query):
    output_location = "s3://{}/results".format(S3_RESULTS_BUCKET_NAME)

    query_execution_id = athena.execute_query(query.get_query_string(), output_location)
    print("Athena query execution id:", query_execution_id)

    query_status = athena.poll_query_execution_status(query_execution_id)
    if query_status["State"] == "FAILED" or query_status["State"] == "CANCELLED":
        raise RuntimeError("Query failed or cancelled:", query_status)

    response = s3_client.get_object(
        Bucket=S3_RESULTS_BUCKET_NAME,
        Key="results/" + query_execution_id + ".csv",
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        results_content = response["Body"].read().decode("utf-8")
        print("Row Count:", len(results_content.split("\n")) - 2)
        # parse csv from results_content
        csv_reader = csv.reader(results_content.split("\n"))
        next(csv_reader)  # skip header

        # skip empty rows
        for row in csv_reader:
            if len(row) > 0:
                yield row
        return csv_reader
    else:
        raise RuntimeError("Failed to get results from s3", response)


def get_warc(s3_client, s3_key, warc_offset, warc_length):
    response = s3_client.get_object(
        Bucket="commoncrawl",
        Key=s3_key,
        Range="bytes={}-{}".format(warc_offset, warc_offset + warc_length - 1),
    )
    # raise exception if response is not 200
    if response["ResponseMetadata"]["HTTPStatusCode"] != 206:
        raise RuntimeError("Failed to get warc file from s3", response)

    # only 1 record in our warc files
    for record in WARCIterator(BytesIO(response["Body"].read())):
        return record
