import os
from dotenv import load_dotenv

load_dotenv()


S3_RESULTS_BUCKET_NAME = os.getenv("S3_RESULTS_BUCKET_NAME")
AWS_REGION = "us-east-1"
