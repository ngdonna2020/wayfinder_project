# rag_engine.py

import json
import os

def load_vectorstore_mock(path="jobs_mock_data.json"):  # ✅ Removed faiss_index/
    """Loads precomputed job data from a static JSON mock file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Vectorstore not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_semantic_matches(query, jobs, top_k=3):
    """
    Simulate semantic similarity by counting word overlaps between query and job descriptions.
    """
    query_words = set(query.lower().split())
    scored = []

    for job in jobs:
        job_words = set(job["description"].lower().split())
        score = len(query_words & job_words)
        scored.append((job, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [dict(**job, score=score) for job, score in scored[:top_k]]
