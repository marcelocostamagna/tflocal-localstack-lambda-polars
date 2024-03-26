import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Extract bucket name and object key from the event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    destination_bucket = 'bronze'
    
    # Define the copy operation
    copy_object = {'Bucket': source_bucket, 'Key': s3_key}
    
    # Copy the object to the destination bucket
    try:
        s3_client.copy_object(CopySource=copy_object, Bucket=destination_bucket, Key=s3_key)
        logger.info(f"File {s3_key} copied to the destination bucket successfully!")
    except Exception as e:
        logger.error(f"Error copying file {s3_key} to the destination bucket: {e}")

    return {
        'statusCode': 200,
        'body': f"File {s3_key} has been successfully copied."
    }
