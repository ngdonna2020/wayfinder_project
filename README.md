# Wayfinder project
Context Augmented Gen AI final project: Donna Nguyen, Aryaan Upadhyay, Aram Jimenez


RAG
The system is built in two layers:

Deterministic profile matching based on structured multiple-choice answers (24 profiles)

Semantic job recommendation using RAG, powered by AWS Bedrock Claude 3 Haiku and a Knowledge Base of job listings extracted from PDF documents

🧠 RAG Design
🔹 Input
Users complete a 5-question form (4 multiple-choice + 1 free-form)

The structured responses are mapped to a predefined profile (e.g., A-A-B-B)

The free-form response (Q5) is passed as a query to the RAG pipeline

🔹 Retrieval
The system uses AWS Bedrock Knowledge Bases to semantically retrieve relevant job chunks

Data source: PDFs of real job listings (hosted in S3 and auto-synced to the KB)

Embedding model: Amazon Titan Embeddings G1

Chunking strategy: semantic chunking, preserving job description sections

🔹 Generation
Retrieved chunks are passed to Claude 3 Haiku, a fast, lightweight LLM

The model is prompted to:
"Match this user description to appropriate job roles: <user free-form response>"

🔹 Output
The result is displayed as:

A personalized work analysis (based on structured profile)

A semantic recommendation (from Claude Haiku)

If Claude cannot produce a helpful result (e.g., responds with “Sorry…”), a fallback job recommendation is provided

💡 Design Rationale

Component	Reason
AWS Bedrock	Fully managed, serverless RAG pipeline with scalable embeddings and fast LLMs
Claude 3 Haiku	Optimized for fast, low-cost inference while preserving quality
Semantic Chunking	More accurate than fixed sizes, aligns with real job listing structure
Fallback Match	Prevents blank results or unhelpful AI responses, improves user trust
Structured Profile Layer	Guarantees deterministic results for users who skip free-text entry

