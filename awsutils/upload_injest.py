import boto3
import os
import logging
from botocore.exceptions import ClientError
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

client_s3 = boto3.client('s3')
bedrock_agent_client = boto3.client('bedrock-agent')

def upload_fileobj_to_s3(file_obj, bucket, object_name):
    """Upload a file-like object to an S3 bucket"""
    try:
        client_s3.upload_fileobj(file_obj, bucket, object_name)
        logging.info(f"File uploaded to {bucket}/{object_name}")
        return True
    except ClientError as e:
        logging.error(f"Failed to upload file to {bucket}/{object_name}: {e}")
        return False

def start_ingestion_job(knowledgeBaseId, dataSourceId):
    """Start the ingestion job with the Bedrock Agent"""
    try:
        start_job_response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=knowledgeBaseId,
            dataSourceId=dataSourceId
        )
        pprint(start_job_response)
        logging.info(f"Ingestion job started with response: {start_job_response}")
        return True
    except ClientError as e:
        logging.error(f"Failed to start ingestion job for dataSourceId {dataSourceId} and knowledgeBaseId {knowledgeBaseId}: {e}")
        return False

def upload_and_ingest(file_name, bucket, datasourceID, knowledgeBaseId, object_name=None):
    """Upload a file to S3 and start an ingestion job"""
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, "data", file_name)

    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        with open(file_path, "rb") as file_obj:
            if upload_fileobj_to_s3(file_obj, bucket, object_name):
                if start_ingestion_job(knowledgeBaseId, datasourceID):
                    return True, "Success"
    except Exception as e:
        logging.error(f"Failed during file handling: {e}")

    return False, "Failed"


