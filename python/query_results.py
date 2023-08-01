import csv
import gzip
import io


def query_results(s3_client, s3_results_bucket_name, query_execution_id):
    response = s3_client.get_object(
        Bucket=s3_results_bucket_name,
        Key="results/" + query_execution_id + ".csv",
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        results_content = response["Body"].read().decode("utf-8")
        print("Row Count:", len(results_content.split("\n")) - 2)
        # parse csv from results_content
        csv_reader = csv.reader(results_content.split("\n"))
        next(csv_reader)  # skip header
        return csv_reader
    else:
        raise RuntimeError("Failed to get results from s3", response)


def get_uncompressed_warc_file_content_from_s3_key(
    s3_client, s3_key, warc_offset, warc_length
):
    response = s3_client.get_object(
        Bucket="commoncrawl",
        Key=s3_key,
        Range="bytes={}-{}".format(warc_offset, warc_offset + warc_length - 1),
    )
    # raise exception if response is not 200
    if response["ResponseMetadata"]["HTTPStatusCode"] != 206:
        raise RuntimeError("Failed to get warc file from s3", response)

    content = response["Body"].read()
    return gzip.GzipFile(fileobj=io.BytesIO(content)).read()
