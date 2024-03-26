import polars as pl
import boto3
import s3fs
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Extract bucket name and object key from the event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    destination_bucket = 'silver'
    
    # Construct the S3 file URL
    s3_file_url = f"s3://{source_bucket}/{s3_key}"

    # Read the file from S3 using Polars
    fs = s3fs.S3FileSystem()
    with fs.open(s3_file_url, mode='rb') as f:
        df = pl.read_csv(f)

    # Convert the DataFrame to a Parquet file
    parquet_file = f"/tmp/{os.path.splitext(s3_key)[0]}.parquet"
    df.write_parquet(parquet_file)
    
    # Convert and copy the object to the destination bucket
    try:
        s3_client.upload_file(parquet_file, destination_bucket, f"{os.path.splitext(s3_key)[0]}.parquet")
        logger.info(f"File {s3_key} converted to the destination bucket successfully!")
    except Exception as e:
        logger.error(f"Error converting file {s3_key} to the destination bucket: {e}")

    return {
        'statusCode': 200,
        'body': f"File {s3_key} has been successfully converted."
    }
