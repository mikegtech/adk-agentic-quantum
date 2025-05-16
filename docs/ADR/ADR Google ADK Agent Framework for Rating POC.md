# ADR: Selection of the Google ADK Agent Framework for the Rating-System POC

## Overview

We need a lightweight, Python-native agent-orchestration framework to showcase an end-to-end Retrieval-Augmented Generation (RAG) workflow—context retrieval, tool invocation, large-language-model (LLM) calls, observability, and security control—within our local NVIDIA AI Workbench environment. After evaluating several options, the Google Agent Development Kit (ADK) has been selected as the first framework to integrate.

## Issue

Select an agent framework that:

- Easily composes custom tools (vector search, XML diff, report export) with an LLM call chain.
- Supports asynchronous I/O to avoid blocking GPU inference on a single-GPU laptop.
- Provides built-in telemetry hooks for latency and trace collection.
- Uses a permissive OSS license compatible with our planned Apache-2 release.

## Decision

Adopt Google ADK ≥ 0.4 as the primary agent framework for the proof of concept:

- Declarative `ActionGraph` lets us whitelist tool sequences and enforce security boundaries.  
- `@tool` / `@agent` decorators cut boilerplate—first runnable agent fits in < 50 lines.  
- Native `asyncio` design aligns with our FastAPI backend.  
- Built-in OpenTelemetry emitters feed straight into the Prometheus + Grafana stack bundled in the Enterprise RAG blueprint.  
- Apache-2.0 license meshes with QuantumRate Navigator’s licensing strategy.

## Status

**Proposed**: Pending sign-off at the next architecture checkpoint (Q2-Sprint 2, Day 5).

## Assumptions

1. A single-agent pattern is sufficient for the initial pilot; multi-agent coordination can be added later.  
2. RTX 5000 Ada (16 GB) GPU can host one FP16 Llama-3 8B NIM plus the ADK runtime without memory pressure.  
3. Developers are comfortable with Python ≥ 3.10 and `async`/`await` syntax.  
4. Vector store (Milvus) and LLM endpoint (Llama-3 8B NIM) are already running via the Enterprise RAG blueprint.

## Constraints

- ADK is pre-1.0; breaking changes are likely between minor versions.  
- Smaller community than LangChain or LlamaIndex; fewer example snippets.  
- Google-centric docs focus on Vertex AI; cloud-agnostic patterns may require extra work.

## Implications

- **Agent Runner**: Wrap ADK inside `agent_runner.py`; swap-friendly if we change frameworks later.  
- **Tooling**: Implement `VectorSearchTool`, `XMLSourceTool`, and `DiffViewerTool` as ADK `@tool` functions; register them in the agent’s `ActionGraph`.  
- **Observability**: Enable ADK’s OpenTelemetry exporter; scrape metrics via the Prometheus instance in the RAG `docker-compose`.  
- **Security**: Use `ActionGraph` edge filters to prevent the LLM from invoking non-whitelisted shell commands.  
- **Testing**: Add pytest harness that sends 20 golden questions to the `/agent/chat` endpoint and asserts semantic-answer accuracy ≥ 0.8.  
- **Upgrade Path**: Pin ADK in `requirements.txt`; schedule monthly review of release notes and regression tests.

## Notes

### Quick Install

```bash
pip install "google-adk>=0.4"
