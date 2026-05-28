---
type: resource
category: product-documentation
version: "2.0-draft"
last_updated: 2026-05-10
status: in-review
tags: [resource, meridian, product, spec, v2]
---

# Meridian v2.0 — Product Specification

> [!info]
> Living document. Current status: in review with [[People/Tom Reyes]] and [[People/Sarah Kim]].
> Full spec in Notion (link). This note = summary of key decisions for personal reference.

## Feature 1: Async Collaboration

**Problem**: Teams across time zones lose context when async discussion happens in disconnected tools (Slack, email, comments).

**Solution**: Meridian's native async layer attaches threaded discussion directly to any document element. Decision history travels with the content.

**Key decisions**:
- Threads are immutable after 48h (prevents retroactive edits) — [[People/Tom Reyes]]'s recommendation
- Notification model: mention-only by default (reduces noise)
- Mobile: view-only in v2.0; full compose in v2.1

## Feature 2: AI Suggestion Engine

**Problem**: Users waste time searching for related content already in their workspace.

**Solution**: Semantic similarity engine surfaces related documents, snippets, and templates inline as the user writes.

**Key decisions**:
- Model: fine-tuned sentence-transformer, not GPT call (latency + cost)
- Privacy: all embeddings computed client-side (enterprise requirement)
- Threshold: only surface suggestions with cosine similarity > 0.72

**References**: [[Resources/AI-ML-Reading]] — embedding spaces and retrieval patterns

## Feature 3: Settings Redesign

**Problem**: Settings are currently a single 47-item flat list. Power users are fine; new users are lost.

**Solution**: Progressive disclosure architecture — 3 tiers: Quick Setup, Standard, Advanced.

**Key decisions**:
- Quick Setup: 8 items max (informed by [[People/Priya-Nair]]'s research: users complete setup if <8 decisions)
- Advanced: hidden behind "Show advanced settings" toggle
- Terminology: "workspace" replaces "vault" in Quick Setup tier (see [[Daily/2026-W20-Standup]])

## Related

- [[Projects/Q3-Product-Launch]]
- [[People/Tom Reyes]], [[People/Sarah Kim]], [[People/Elena Vasquez]]
- [[Resources/AI-ML-Reading]]
