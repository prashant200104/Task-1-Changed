import boto3
import os
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

logging.basicConfig(level=logging.INFO)

client_s3 = boto3.client('s3')

def clear_s3_bucket(bucket_name):
    """Delete all objects in an S3 bucket"""
    try:
        # List all objects in the bucket
        objects = client_s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in objects:
            for obj in objects['Contents']:
                # Delete each object
                client_s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                logging.info(f"Deleted {obj['Key']} from bucket {bucket_name}")

        logging.info(f"All objects in bucket {bucket_name} have been deleted")
        return True
    except ClientError as e:
        logging.error(f"Failed to clear bucket {bucket_name}: {e}")
        return False

def clear_pinecone_index(index_name):
    """Delete all vectors in a Pinecone index"""
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        
        # Connect to the index
        index = pc.Index(index_name)
        
        # Fetch all vector IDs (the method may vary based on the Pinecone API)
        vector_ids = index.describe_index_stats()['index_size']
        
        if vector_ids > 0:
            # Delete all vectors by ID
            for i in range(vector_ids):
                index.delete(ids=[f'vector_id_{i}'])
        
        logging.info(f"All vectors in Pinecone index {index_name} have been deleted")
        return True
    except Exception as e:
        logging.error(f"Failed to clear Pinecone index {index_name}: {e}")
        return False


