import boto3
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

KB_ID = os.getenv('BEDROCK_KB_ID')
REGION = os.getenv('AWS_REGION', 'us-east-1')
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"

# Create the client
client = boto3.client("bedrock-agent-runtime", region_name=REGION)

def test_query():
    try:
        response = client.retrieve_and_generate(
            input={"text": "test query"},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KB_ID,
                    "modelArn": MODEL_ARN,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 3
                        }
                    }
                }
            }
        )
        
        print("Raw response:", json.dumps(response, indent=2))
        
        if "output" in response and "text" in response["output"]:
            print("\nProcessed response:", response["output"]["text"])
        else:
            print("\nUnexpected response format")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Testing knowledge base query...")
    print(f"Knowledge Base ID: {KB_ID}")
    print(f"Region: {REGION}")
    print(f"Model ARN: {MODEL_ARN}")
    print("\nExecuting test query...")
    test_query()
