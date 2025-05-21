# QuantumRate Navigator – Proof-of-Concept (POC)

> **An agent-driven retrieval-augmented AI assistant that explains and tests legacy Insbridge rating programs.**

---

## Table of Contents
1. [Project Goals](#project-goals)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Repository Layout](#repository-layout)
5. [Configuration](#configuration)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
10. [License](#license)

---

## Project Goals

| Goal | KPI |
|------|-----|
| **Transparent Q&A** over rating logic | ≥ 90 % hit-@-5 on SME gold set |
| **Version diff & export** | Unified diff generated in < 500 ms |
| **Sample premium calc** | Round-trip latency < 1 s |
| **Local-first** development | Runs on single RTX 5000 (16 GB) using NVIDIA AI Workbench |

---

## Architecture

```mermaid
flowchart TD
    subgraph Workbench
        A[ADK Agent<br/>QuantumRate] -->|calls tools| T1[Vector Search]
        A --> T2[XML Fetch]
        A --> T3[Diff Versions]
        A --> T4[Premium Calc]
    end

    subgraph Containers (docker-compose)
        NIM[Llama-3 8B NIM<br/>(FP16)] -->|OpenAI API| A
        Embed[NeMo Retriever] -->|Embeddings| Milvus[(Milvus DB)]
        A -->|ANN query| Milvus
    end

    User[Actuary / Engineer] -->|chat| A
