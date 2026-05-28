---
type: note
topic: AI/ML
subtopic: architecture
created: 2026-02-20
modified: 2026-04-15
tags: [AI, ML, transformer, attention, architecture]
---

# Transformer Architecture Primer

> Personal reference for transformer architecture. Goal: understand deeply enough to reason about product tradeoffs, not to implement from scratch.

## The Core Intuition

The transformer solved a problem that RNNs couldn't: how to let every token in a sequence attend to every other token simultaneously, regardless of distance.

An RNN reads left to right. By the time it reaches token 100, information from token 1 has passed through 99 intermediate states and is largely forgotten. The transformer reads the whole sequence at once.

## Attention Mechanism

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

- **Q (Query)**: "What am I looking for?"
- **K (Key)**: "What do I contain?"
- **V (Value)**: "What do I give you if you attend to me?"

Each token asks: "which other tokens are relevant to me?" and receives a weighted average of their values, weighted by similarity (dot product of Q and K).

**Why the √d_k scaling**: Prevents dot products from growing too large in high dimensions, which would push softmax into saturation (very peaked distribution, vanishing gradients).

## Multi-Head Attention

Rather than one attention function, compute H parallel attention functions with different learned projections. Each head can attend to different aspects:
- Head 1 might learn syntactic relationships
- Head 2 might learn semantic similarity
- Head 3 might learn positional proximity

Output is concatenated and projected back to model dimension.

## Position Encodings

Since attention is permutation-invariant (no inherent sense of order), position must be injected explicitly. Original paper used sinusoidal encodings. Modern models use learned positional embeddings or RoPE (Rotary Position Embeddings).

## Feed-Forward Layers

After each attention layer: a two-layer MLP applied position-wise (independently to each token). This is where most model capacity lives — the FFN is 4× wider than the attention layers. Hypothesis: FFN layers store factual knowledge; attention layers handle routing and composition.

## Product Relevance

For [[../../Hubs/Technology-Hub]] and Meridian's AI suggestion engine:
- The embedding space used for semantic similarity (cosine similarity > 0.72 threshold) is the output of the encoder's final layer
- Latency budget (400ms P95) is primarily determined by sequence length × attention complexity (O(n²)) — motivates Flash Attention
- Client-side embedding computation is feasible with distilled models (e.g. ~40M parameter sentence-transformers)

## Related

- [[../../Hubs/Technology-Hub]]
- [[RLHF-Overview]] — what gets trained on top of this architecture
- [[Embedding-Spaces-and-Retrieval]] — the downstream use
- [[../../People/Elena-Vasquez]] — discussed architecture tradeoffs in context of AI feature spec
