---
type: note
topic: systems
subtopic: observability
created: 2026-05-20
modified: 2026-05-20
tags: [systems, observability, tracing, OpenTelemetry, distributed]
---

# Distributed Tracing 101

> Notes from conversations with [[../../People/Tom-Reyes]] on Meridian's observability stack. Useful context for product discussions about performance SLAs.

## The Problem

A single user request to a modern service typically touches 5–15 microservices. When something is slow or broken, which service is at fault? Logs from each service tell a local story. Tracing tells the *whole story across all services*.

## Key Concepts

**Trace**: The complete record of one request as it travels through the system. Has a unique `trace_id`.

**Span**: One unit of work within a trace (e.g. one database query, one API call). Has a `span_id`, `parent_span_id`, start time, end time, and attributes.

**Context propagation**: Each service passes the `trace_id` and `parent_span_id` to downstream services via HTTP headers. This is how spans are stitched into a trace tree.

## OpenTelemetry

The de facto standard (CNCF project). Three pillars:
- **Traces**: as above
- **Metrics**: counters, histograms, gauges
- **Logs**: structured log records

OTel provides instrumentation libraries for most languages and an OTLP protocol for exporting to backends (Jaeger, Zipkin, Tempo, Datadog, etc.).

Meridian uses: OTel SDKs in Go services → Grafana Tempo backend → Grafana for dashboards.

## Practical Application (Product Perspective)

When discussing performance SLAs with [[../../People/Tom-Reyes]]:
- "P95 latency" = 95th percentile of trace durations. The number I care about for the 400ms AI suggestion budget.
- "Flame graph" = visualisation of span durations; shows where time is spent
- "Error rate" = spans with `error=true` / total spans

Understanding tracing lets me read [[People/Tom-Reyes]]'s Grafana dashboards and ask intelligent questions rather than relying on his translation.

## Related

- [[../../Hubs/Technology-Hub]]
- [[../../People/Tom-Reyes]]
- [[Rust-Ownership-Model]] — the Go services use similar ownership/concurrency patterns
