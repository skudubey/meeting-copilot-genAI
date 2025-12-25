import json
import uuid
import boto3
import requests
from requests_aws4auth import AWS4Auth

# === CONFIG ===
REGION = "us-east-1"
SERVICE = "aoss"
INDEX = "meeting-vectors-prod"
OPENSEARCH_ENDPOINT = "https://sas8zzz9v3owi1udjryf.us-east-1.aoss.amazonaws.com"
BUCKET = "meeting-notes-prod"

# === AWS AUTH ===
session = boto3.Session()
credentials = session.get_credentials()

awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    SERVICE,
    session_token=credentials.token
)

headers = {"Content-Type": "application/json"}

# === CLIENTS ===
bedrock = boto3.client("bedrock-runtime", region_name=REGION)
s3 = boto3.client("s3")

# === EMBEDDINGS ===
def get_embedding(text: str):
    resp = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps({"inputText": text})
    )
    output = json.loads(resp["body"].read())
    return output["embedding"]

# === CHUNKING (simple) ===
def chunk_text(text: str, max_chars=400):
    raw_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    final_chunks = []

    for c in raw_chunks:
        while len(c) > max_chars:
            split_at = c.rfind(".", 0, max_chars)
            if split_at == -1:
                split_at = max_chars
            final_chunks.append(c[:split_at+1].strip())
            c = c[split_at+1:].strip()
        if c:
            final_chunks.append(c)

    return final_chunks


# === MAIN HANDLER ===
def handler(event, context):
    user_id = event["user_id"]
    meeting_text = event["meeting_text"]
    meeting_id = str(uuid.uuid4())

    # 1️⃣ store raw meeting
    s3.put_object(
        Bucket=BUCKET,
        Key=f"{user_id}/{meeting_id}.txt",
        Body=meeting_text
    )

    # 2️⃣ chunk meeting
    chunks = chunk_text(meeting_text)
    if not chunks:
        return {"status": "NO_CHUNKS", "meeting_id": meeting_id}

    # 3️⃣ embed + index
    chunks_indexed = 0
    for i, chunk in enumerate(chunks):
        vector = get_embedding(chunk)
        doc = {
            "user_id": user_id,
            "meeting_id": meeting_id,
            "chunk_text": chunk,
            "chunk_id": i,
            "vector": vector
        }

        resp = requests.post(
            f"{OPENSEARCH_ENDPOINT}/{INDEX}/_doc",
            auth=awsauth,
            headers=headers,
            data=json.dumps(doc)
        )

        if resp.status_code in (200, 201):
            chunks_indexed += 1

    return {
        "status": "INGESTED",
        "meeting_id": meeting_id,
        "user_id": user_id,
        "chunks_indexed": chunks_indexed
    }
