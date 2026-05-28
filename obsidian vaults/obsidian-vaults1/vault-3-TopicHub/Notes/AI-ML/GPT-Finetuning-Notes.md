---
type: note
topic: AI/ML
subtopic: fine-tuning
created: 2026-04-15
modified: 2026-05-20
tags: [AI, ML, fine-tuning, GPT, LLM, practical]
---

# GPT Fine-Tuning Notes

> Practical notes from experimenting with OpenAI fine-tuning API and reading research. Goal: understand when fine-tuning is worth it vs prompting or RAG.

## When to Fine-Tune (vs Prompt Engineering vs RAG)

| Approach | Best for | Limitations |
|---|---|---|
| Prompt engineering | Style, format, tone | Limited by context window; doesn't add knowledge |
| RAG | Factual retrieval, dynamic knowledge | Latency cost; retrieval quality matters |
| Fine-tuning | Consistent format, style, domain jargon | Expensive; doesn't update knowledge after training cutoff |
| Full pre-training | Domain-specific foundation | Extremely expensive; rarely justified |

**Rule of thumb**: Exhaust prompting first. Use RAG for knowledge. Use fine-tuning only for style/format consistency at scale.

## Fine-Tuning Workflow (OpenAI API)

```python
# 1. Prepare training data
# Format: JSONL, each line is one training example
# {"messages": [{"role": "system", "content": "..."}, 
#               {"role": "user", "content": "..."},
#               {"role": "assistant", "content": "..."}]}

# 2. Upload file
client.files.create(file=open("training.jsonl", "rb"), purpose="fine-tune")

# 3. Create fine-tuning job
client.fine_tuning.jobs.create(
    training_file="file-abc123",
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={"n_epochs": 3}
)

# 4. Monitor
client.fine_tuning.jobs.retrieve("ftjob-abc123")
```

## Dataset Quality Notes

- Minimum viable: ~50 examples. Meaningful improvement: ~200+. Saturation: usually ~1,000.
- Quality > quantity. 50 hand-curated examples beat 500 auto-generated ones.
- Include edge cases and failure modes explicitly.
- Maintain 80/10/10 train/validation/test split.

## Experiments Run

| Date | Model | Dataset | Task | Result |
|---|---|---|---|---|
| 2026-03-20 | gpt-4o-mini | 150 examples | Product changelog generation | 40% reduction in editing time |
| 2026-04-10 | gpt-4o-mini | 80 examples | Meeting notes → action items | Inconsistent; abandoned |
| 2026-04-28 | gpt-4o-mini | 220 examples | Technical spec from user story | Promising; still evaluating |

## Related

- [[../../../Hubs/Technology-Hub]]
- [[RLHF-Overview]] — connection: RLHF is fine-tuning with human preference signal
- [[Claude-API-Workflow]] — contrast: Claude via API vs fine-tuned GPT for product use case
