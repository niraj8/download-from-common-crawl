import os
from dotenv import load_dotenv
from constants import S3_RESULTS_BUCKET_NAME, AWS_REGION

import boto3
from athena import Athena

load_dotenv()


S3_RESULTS_BUCKET_NAME = os.getenv("S3_RESULTS_BUCKET_NAME")

output_location = "s3://{}/results".format(S3_RESULTS_BUCKET_NAME)

athena = Athena(boto3.client("athena", region_name=AWS_REGION))
query_execution_id=athena.repair_table(output_location)
print("Table Repair Initiated:", query_execution_id)
athena.poll_query_execution_status(query_execution_id)
print("Table Repair Completed:", query_execution_id)