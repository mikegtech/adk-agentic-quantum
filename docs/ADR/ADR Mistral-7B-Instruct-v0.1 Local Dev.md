## Overview
This ADR captures the decision to run the Mistral-7B-Instruct-v0.1 model locally—via vLLM in a Docker container—for the Google ADK agentic integration on a 16 GB RTX 5000 Ada GPU.

## Title
Use Mistral-7B-Instruct-v0.1 via vLLM for Local Google ADK Integration

## Status
Accepted

## Context and Problem Statement
We need a capable, instruction-tuned LLM to drive multi-agent tooling experiments in our Google ADK integration. The model must run entirely on a developer’s Ubuntu laptop with a single 16 GB RTX 5000 Ada GPU, expose an OpenAI-compatible HTTP API, and fit within our constrained VRAM budget without resorting to cloud services.

## Decision
We will deploy Mistral-7B-Instruct-v0.1 locally in a Docker container using the vLLM OpenAI API server image. We’ll configure vLLM to:
- Use up to 95 % of GPU memory  
- Disable chunked prefill  
- Cap context length to 4 096 tokens  

This configuration allows the model weights (~13.5 GiB BF16) plus KV-cache (~0.4 GiB) to fit under the 16 GiB hardware limit.

## Alternatives Considered
- **DeepSeek-R1-Distill-Llama-8B (NIM container)**
- **Llama 2-7B-chat or Mistral 7B via Hugging Face + bitsandbytes**
- **Pure-CPU quantized models (llama.cpp GGML)**
- **Cloud-hosted endpoints (Triton Inference, hosted APIs)**

## Decision Drivers

### Positive
- **On-prem GPU usage**: No cloud reliance; full control of data and latency.  
- **Open weights**: Mistral-Instruct is publicly available once license accepted.  
- **Performance**: vLLM’s compiled engine delivers interactive throughput.  
- **Compatibility**: Exposes standard `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`.

### Negative
- **Context cap**: Limited to 4 096 tokens, not the full 32 768 the model supports.  
- **Licensing**: Requires HF license acceptance and token injection.  
- **Complexity**: Must tune vLLM flags to fit VRAM, adding operational steps.

## Implementation Notes
- **Docker Run Command**
  ```bash
  docker run --gpus all \
    --name adk-agentic-quantum-mistral-hf \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -e HUGGING_FACE_HUB_TOKEN \
    -p 8001:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model mistralai/Mistral-7B-Instruct-v0.1 \
    --gpu-memory-utilization=0.95 \
    --no-enable-chunked-prefill \
    --max-model-len=4096
