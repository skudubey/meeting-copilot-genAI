import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

# === CONFIG ===
REGION = "us-east-1"
SERVICE = "aoss"
INDEX = "meeting-vectors-prod"
OPENSEARCH_ENDPOINT = "https://sas8zzz9v3owi1udjryf.us-east-1.aoss.amazonaws.com"

# === AUTH ===
session = boto3.Session()
credentials = session.get_credentials()

awsauth = AWS4Auth(
    credentials.access_key, credentials.secret_key,
    REGION, SERVICE, session_token=credentials.token
)

headers = {"Content-Type": "application/json"}

# === CLIENTS ===
bedrock = boto3.client("bedrock-runtime", region_name=REGION)


# === EMBEDDINGS ===
def get_embedding(text):
    resp = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps({"inputText": text})
    )
    return json.loads(resp["body"].read())["embedding"]


# === MAIN HANDLER ===
def handler(event, context):
    user_id = event["user_id"]
    question = event["question"]

    # 1️⃣ embed question
    query_vec = get_embedding(question)

    # 2️⃣ vector search (Top-4)
    search_payload = {
        "size": 4,
        "query": {
            "knn": {
                "vector": {
                    "vector": query_vec,
                    "k": 4
                }
            }
        },
        "_source": ["chunk_text", "meeting_id", "chunk_id"]
    }

    resp = requests.post(
        f"{OPENSEARCH_ENDPOINT}/{INDEX}/_search",
        auth=awsauth,
        headers=headers,
        data=json.dumps(search_payload)
    )

    hits = resp.json().get("hits", {}).get("hits", [])
    if not hits:
        return {"answer": "No matching context found.", "context_used": []}

    context_chunks = [h["_source"]["chunk_text"] for h in hits]
    context_str = "\n".join(context_chunks)

    # 3️⃣ grounded generation
    prompt = f"""
Answer ONLY using the context below.

Context:
{context_str}

Question:
{question}
"""

    llm_resp = bedrock.invoke_model(
        modelId="amazon.titan-text-express-v1",
        body=json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {"maxTokenCount": 200, "temperature": 0}
        })
    )

    answer = json.loads(llm_resp["body"].read())["results"][0]["outputText"]
    return {"answer": answer, "context_used": context_chunks}
