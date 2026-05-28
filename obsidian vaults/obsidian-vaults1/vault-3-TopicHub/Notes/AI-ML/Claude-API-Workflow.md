---
type: note
topic: AI/ML
subtopic: tools
created: 2026-05-26
modified: 2026-05-26
tags: [AI, Claude, API, workflow, prompting, practical]
---

# Claude API Workflow

> Personal reference for working with the Claude API via Anthropic SDK. Updated as I discover better patterns.

## Setup

```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_API_KEY")  # or set ANTHROPIC_API_KEY env var

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude."}
    ]
)
print(message.content[0].text)
```

## Model Selection (2026)

| Model | Use case | Context window |
|---|---|---|
| claude-opus-4 | Complex reasoning, nuanced tasks | 200k tokens |
| claude-sonnet-4 | Balanced speed/quality | 200k tokens |
| claude-haiku-4 | Fast, simple tasks, high volume | 200k tokens |

## Prompt Patterns That Work

### Structured output
```python
# Ask for JSON explicitly and parse it
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": 
        "Extract the key entities from this text as JSON: {text}"
        "\n\nReturn only valid JSON with keys: people, organisations, dates."
    }]
)
```

### Long document Q&A (with context window)
- Place document first, question last
- Use XML tags to delimit sections: `<document>...</document><question>...</question>`
- For very long docs, chunk and map-reduce

### Tool use
```python
tools = [{
    "name": "search_database",
    "description": "Search the product database for items matching a query",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Max results", "default": 10}
        },
        "required": ["query"]
    }
}]
```

## Cost Optimisation

- Cache system prompts with `cache_control` (beta) for long repeated contexts
- Use Haiku for classification and routing; Sonnet for generation
- Batch API for offline processing: 50% cost reduction, 24h turnaround

## Related

- [[../../../Hubs/Technology-Hub]]
- [[GPT-Finetuning-Notes]] — comparison: Claude via API vs fine-tuned GPT
