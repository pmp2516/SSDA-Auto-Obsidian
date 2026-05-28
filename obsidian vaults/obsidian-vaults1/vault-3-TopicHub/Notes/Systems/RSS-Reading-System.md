---
type: note
topic: systems
subtopic: information-diet
created: 2026-02-15
modified: 2026-04-10
tags: [systems, RSS, reading, information, workflow, tools]
---

# RSS Reading System

> My current setup for staying informed without doom-scrolling or algorithmic distraction. Feeds curated as of May 2026.

## Why RSS

Algorithmic feeds (Twitter/X, LinkedIn, Reddit front page) optimise for engagement, not quality. RSS is pull-based and chronological: you decide what you read, and you see everything from sources you chose.

## Stack

- **Aggregator**: Miniflux (self-hosted on a €4/month VPS) — clean, keyboard-navigable, API access
- **Read-later**: Omnivore (free, open source) — syncs highlights to Obsidian via plugin
- **Mobile reading**: Reeder 5 (iOS) connected to Miniflux API

## Feed List (curated)

### Technology & AI
- **Lilian Weng** — lilianweng.github.io/feed.xml — best ML technical writing
- **Simon Willison** — simonwillison.net/atom/everything/ — AI tools, practical use
- **Stratechery** (paid) — technology business strategy
- **The Diff** (paid) — technology, finance, business

### Product & Business
- **Lenny's Newsletter** — lennysnewsletter.com/feed — product management
- **Shreyas Doshi** (Substack) — PM mental models

### Science & Long-form
- **Quanta Magazine** — quantamagazine.org/feed/ — physics, biology, mathematics
- **Aeon** — aeon.co/feed.rss — philosophy, psychology, culture

## Workflow

**Morning read**: 08:00 before deep work. Max 20 minutes. Mark interesting items as "read later" in Omnivore.

**Processing**: Weekly (Sunday, 30min) — review Omnivore queue. Highlight key passages → auto-synced to Obsidian via Omnivore plugin → processed into notes.

**Culling**: Every 90 days, unsubscribe from feeds I've read <20% of.

## Related

- [[../../Hubs/Technology-Hub]]
- [[../../Hubs/Life-Design-Hub]] — information system as part of deep work protocol
- [[../LifeDesign/Deep-Work-Protocol]] — morning reading fits before the 08:00–12:00 protected block
