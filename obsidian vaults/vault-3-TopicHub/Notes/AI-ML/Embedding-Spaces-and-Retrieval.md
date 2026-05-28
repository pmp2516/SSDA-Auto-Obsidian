---
type: note
topic: AI/ML
subtopic: retrieval
created: 2026-03-05
modified: 2026-05-15
tags: [AI, ML, embeddings, RAG, retrieval, semantic-search]
---

# Embedding Spaces and Retrieval

> Notes on vector embeddings, similarity search, and RAG patterns. Directly relevant to Meridian AI suggestion engine.

## What Embeddings Are

A neural network encoder maps text (or images) to a point in high-dimensional space (e.g. 768 dimensions). Semantically similar texts map to nearby points. Distance = semantic dissimilarity.

The key property: **meaning is geometry**. "King − Man + Woman ≈ Queen" is a real result from word2vec, demonstrating that semantic relationships are encoded as geometric relationships.

## Cosine Similarity

For two vectors A and B:

```
cos(θ) = (A · B) / (||A|| × ||B||)
```

Ranges from -1 (opposite) to 1 (identical). For text similarity, values > 0.7 generally indicate semantic relatedness.

Meridian's suggestion engine uses threshold **0.72** (tuned empirically — see [[Claude-API-Workflow]] for calibration experiment notes).

## Retrieval Architectures

### Dense retrieval (embedding-based)
- Encode query and documents into the same embedding space
- Find nearest neighbours (FAISS, Annoy, or pgvector)
- Fast at query time; requires embedding all documents upfront
- Good for semantic similarity; misses exact keyword matches

### Sparse retrieval (BM25/TF-IDF)
- Classic keyword-based scoring
- Fast, interpretable, no GPU required
- Misses synonyms and paraphrases

### Hybrid retrieval
- Combine dense + sparse scores (e.g. Reciprocal Rank Fusion)
- Best of both: semantic understanding + keyword precision
- What production RAG systems typically use

## RAG Pattern

Retrieval-Augmented Generation:
1. User query → encode → find top-k similar documents
2. Concatenate retrieved documents with query as context
3. Pass to generation model → grounded, factual response

Avoids hallucination by grounding generation in retrieved evidence. Useful when:
- Knowledge changes frequently (can update the index without retraining)
- Source attribution is required
- Context exceeds what fits in a prompt

## Practical Notes

- **Model choice**: `all-MiniLM-L6-v2` (384 dims, 22MB) is a good starting point. For Meridian: using a fine-tuned variant on product documentation corpus.
- **Index size**: 1M vectors at 768 dims ≈ 3GB RAM. At 384 dims ≈ 1.5GB.
- **Re-ranking**: After top-k retrieval, a cross-encoder re-ranker improves precision significantly at the cost of latency.

## Related

- [[../../Hubs/Technology-Hub]]
- [[Transformer-Architecture-Primer]] — the architecture producing these embeddings
- [[GPT-Finetuning-Notes]] — fine-tuning vs RAG decision framework
- [[Claude-API-Workflow]] — Claude as generation model in RAG pipeline
