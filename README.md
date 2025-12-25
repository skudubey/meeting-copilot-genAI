# 🧠 Meeting Intelligence Copilot  
### GenAI + RAG using AWS Bedrock & OpenSearch

> 🚀 **Convert raw meeting notes into factual, searchable long-term memory.**
> 
> Upload → Chunk → Embed → Store → Query → Retrieve grounded answers.

---
## ⚙️ 👤 Author
### Saurabh Dubey 

Senior Software Development Engineer, Amazon.

"Building useful AI, one chunk at a time."

## 🎯 Objective

Build a **hallucination-safe knowledge retrieval system** that:
- ingests meeting text
- chunks & embeds it semantically
- stores vector embeddings & metadata
- retrieves the most relevant chunks by meaning
- generates grounded answers using only retrieved context

---

## 🚩 Current Status — **Level 0 Completed**

| Capability | Status |
|------------|--------|
| Upload meeting notes | ✔️ Lambda |
| Multi-chunk splitting | ✔️ Line-based chunker |
| Titan embeddings per chunk | ✔️ Bedrock Titan |
| Store vectors + metadata | ✔️ OpenSearch Serverless |
| Query by semantics | ✔️ Vector similarity |
| Grounded LLM answers | ✔️ Titan Text Express |
| No hallucinations outside context | ✔️ Prompt controlled |
| End-to-end tested | ✔️ Multi meeting ingestion + retrieval |

---

## ⚙️ Architecture

flowchart TD

###### Meeting upload flow

    A[User Uploads Meeting Text]
    
    A--> B[Lambda Ingest Handler]
    
    B --> C[S3 - Raw Storage]
    
    B --> D[Bedrock Titan Embeddings]
    
    D --> E[OpenSearch Serverless Vector Index]
    
###### User query flow 

    F[User Question] 
    
    F--> G[Lambda Query Handler]
    
    G --> H[Bedrock Titan Embeddings]
    H --> E
    E --> G
    G --> I[Bedrock Titan Text Express - Grounded Answer]
🔑 All interactions flow through Lambda for full orchestration. No service talks directly to another service.

## 🧱 Repository Structure

```bash
.
├── README.md                         # main documentation
├── docs
│   ├── Level0_Infrastructure_Setup.pdf
│   └── Level0_Architecture_and_Flow.pdf      # (optional, if exported later)
├── src
│   ├── upload_handler.py             # ingestion: chunk -> embed -> index
│   └── query_handler.py              # retrieval: embed -> search -> generate
└── tests
    ├── upload_test.json              # sample multi-topic meeting
    └── query_test.json               # example questions for validation
```


## ⚙️ Upload Example (Lambda Invoke)

    {
      "user_id": "saurabh",
      "meeting_text": "We reviewed Q1 metrics.\nDecision: Reduce P95 latency by 20% next quarter."
    }


## ⚙️ Query Example

    {
      "user_id": "saurabh",
      "question": "What latency decision was made for next quarter?"
    }


### ⚙️ Expected Answer

    "The decision was to reduce P95 latency by 20% next quarter."


## ⚙️ Multi-topic meeting used during testing

    We reviewed Q1 metrics.
    Decision: Reduce P95 latency by 20% next quarter.

    Customer Feedback:
    Need faster incident resolution and better postmortems.
    Decision: Introduce AI-based summarization for incident analysis.

    Action Items:
    Roll out auto-remediation scripts across services.


## ⚙️ What Level 0 Achieves

| Focus | Result |
|--------|--------|
| Data ingestion | Raw text persisted per user |
| Chunking | Semantic-ready segments |
| Embeddings | Meaning stored as vectors |
| Search | Retrieve by meaning, not keywords |
| Answering | LLM grounds its response in retrieved chunks |
| Hallucinations avoided | No retrieval → no answer |
| End-to-end system | Working production skeleton |


## 🪜 Build Roadmap (Levels)

| Level | Title | Purpose |
|-------|--------|---------|
| **0 — MVP** | ingest + search + answer | ✔️ complete |
| **1 — Retrieval Quality** | scoring, ranking, dedupe | next |
| **2 — APIs & UI** | REST, CLI, Slack/Notion UI | |
| **3 — Multi-user tenancy** | auth, RBAC, quotas | |
| **4 — Insights** | automated decisions, trends | |
| **5 — Organization brain** | memory graph + temporal RAG | |


## 🏗️ Level 0 Infrastructure (Complete)

| Service | Responsibility |
|---------|----------------|
| **S3** | raw meeting text |
| **Lambda (UploadHandler)** | chunk → embed → index |
| **Lambda (QueryHandler)** | embed query → retrieve → generate |
| **Bedrock Titan Embeddings** | vector generation |
| **OpenSearch Serverless** | vector storage + similarity |
| **Bedrock Titan Text Express** | grounded answering |


## 🧾 Production Summary

We built a functional **GenAI memory layer** that never answers from imagination —  
**only from retrieved context.**

**Done.**




