# rag_engine.py

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
KB_ID = os.getenv("BEDROCK_KB_ID")
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"

client = boto3.client("bedrock-agent-runtime", region_name=REGION)

def check_environment():
    print(f"Region: {REGION}")
    print(f"Knowledge Base ID: {KB_ID}")
    print(f"Model ARN: {MODEL_ARN}")
    
    if not KB_ID:
        print("Warning: BEDROCK_KB_ID environment variable is not set")
    if not MODEL_ARN:
        print("Warning: MODEL_ARN is not properly configured")

def check_kb_status():
    try:
        response = client.get_knowledge_base(
            knowledgeBaseId=KB_ID
        )
        print(f"Knowledge Base status: {response['status']}")
        print(f"Storage configuration: {response['storageConfiguration']}")
    except Exception as e:
        print(f"Error checking Knowledge Base status: {str(e)}")

def verify_kb_and_model():
    try:
        # Test a simple query
        response = client.retrieve_and_generate(
            input={"text": "test query"},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KB_ID,
                    "modelArn": MODEL_ARN
                }
            }
        )
        print("Knowledge Base and Model configuration is valid")
        return True
    except client.exceptions.ValidationException as ve:
        print(f"Validation error: {str(ve)}")
        return False
    except Exception as e:
        print(f"Other error: {str(e)}")
        return False

def get_semantic_matches_bedrock(query):
    """Query Bedrock Knowledge Base using Claude 3 Haiku."""
    try:
        print(f"Attempting query with KB_ID: {KB_ID}")
        print(f"Using model: {MODEL_ARN}")
        
        response = client.retrieve_and_generate(
            input={"text": query},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KB_ID,
                    "modelArn": MODEL_ARN
                }
            }
        )

        # DEBUG: Show raw response
        print("Raw Bedrock response:")
        print(response)

        return response["output"]["text"]

    except client.exceptions.ValidationException as ve:
        print(f"Configuration error: {str(ve)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    print("Running diagnostics...")
    check_environment()
    check_kb_status()
    verify_kb_and_model()
