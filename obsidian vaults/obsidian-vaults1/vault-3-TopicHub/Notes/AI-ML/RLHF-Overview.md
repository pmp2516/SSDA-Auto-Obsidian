---
type: note
topic: AI/ML
subtopic: training
created: 2026-02-10
modified: 2026-05-10
tags: [AI, ML, RLHF, alignment, training, LLM]
---

# RLHF Overview — Reinforcement Learning from Human Feedback

## What It Is

RLHF is the training technique that transforms a raw language model (which predicts plausible continuations) into an assistant (which produces helpful, harmless, honest outputs). Three stages:

1. **Supervised fine-tuning (SFT)**: Fine-tune the base model on human-written demonstrations of desired behaviour.
2. **Reward model training**: Train a separate model to predict which of two outputs a human would prefer.
3. **RL optimisation**: Use the reward model as a signal to optimise the language model via PPO (Proximal Policy Optimisation).

## Why It Works

Base LLMs are trained to be plausible, not helpful or safe. Plausible includes confident misinformation, toxic content, and verbose non-answers. RLHF steers the model toward outputs that humans rate as better — and human raters can express preferences far more easily than they can write demonstrations.

## Key Papers

- **"Training language models to follow instructions with human feedback"** (OpenAI, InstructGPT, 2022) — the RLHF foundation
- **"Constitutional AI: Harmlessness from AI Feedback"** (Anthropic, 2022) — alternative using AI self-critique to reduce human labelling cost
- **"Direct Preference Optimisation"** (Stanford, 2023) — simplification: eliminates the separate RL step, uses preference data directly

## Limitations

- **Reward hacking**: The model optimises for reward model approval, not the underlying human preference. The two diverge over training.
- **Annotator bias**: Human preferences vary by annotator demographics, mood, and instructions. "Helpful" is culturally variable.
- **Over-refusal**: RLHF often produces models that are over-cautious — refuse ambiguous but benign requests.
- **Distributional shift**: The reward model was trained on a specific data distribution; out-of-distribution inputs may receive unreliable scores.

## Related

- [[../../../Hubs/Technology-Hub]]
- [[GPT-Finetuning-Notes]] — RLHF is fine-tuning with a human-preference reward signal
- [[Transformer-Architecture-Primer]] — understanding the architecture being trained
