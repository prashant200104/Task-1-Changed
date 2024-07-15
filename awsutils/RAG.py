import boto3
import os
import logging
from botocore.exceptions import ClientError
from pprint import pprint
from dotenv import load_dotenv


bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def retrieve_and_generate(input_text, kbId, modelArn):
    """Retrieve and generate a response using the Bedrock Agent runtime"""
    try:
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': input_text
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kbId,
                    'modelArn': modelArn
                }
            }
        )
        return response
    except ClientError as e:
        logging.error(f"Failed to retrieve and generate response for input {input_text}: {e}")
        return None

def process_questions(questions, kbId, modelArn):
    """Process a list of questions and generate responses"""
    responses = []
    for question in questions:
        response = retrieve_and_generate(question, kbId, modelArn)
        responses.append(response)
    return responses


