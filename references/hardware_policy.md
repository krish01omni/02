# 02 Hardware Sentinel & Resource Policy

This document outlines the strict hardware envelope and resource allocation policies enforced by the Guardian sentinel to protect the host machine from freezing, memory exhaustion, or crashes.

---

## 1. Hardware Limits Specification

| Resource | Target Limit | Hard Ceiling | Policy Action on Breach |
| :--- | :--- | :--- | :--- |
| **System RAM** | $\le 85\%$ | **$< 90\%$ (Strict)** | At 87%, pause spawning new workers and serialize tasks. At 89%, suspend active worker processes until memory drops below 80%. **Never allow RAM to reach or exceed 90%.** |
| **System CPU** | $\le 80\%$ | **$< 90\%$ (Strict)** | At 85%, throttle subagent polling rates and insert micro-sleeps. At 90%, prioritize foreground Windows responsiveness. |
| **NVIDIA GPU** | **Up to 100%** | **No Artificial Limit** | Full 100% utilization of CUDA, Tensor Cores, and VRAM permitted on the NVIDIA GeForce RTX 4050 for ML, video/audio rendering, or vision processing. |

---

## 2. Dynamic Worker Pool Concurrency

The number of concurrent worker processes (subagents, compilers, browser instances) is calculated dynamically by `scripts/guardian.py` based on available headroom:

$$\text{Safe Workers} = \max\left(1, \min\left(4, \left\lfloor \frac{\text{Available RAM (GB)} - 2.0}{1.5} \right\rfloor \right)\right)$$

- Always preserves a minimum of 2.0 GB free memory for Windows OS background processes.
- Browser instances are limited to a maximum of 2 concurrent headless contexts.

---

## 3. GPU Acceleration Guidelines

When tasks require heavy compute (e.g., local Whisper audio transcription, video encoding, tensor math, or embedding calculations):
- Direct workers to initialize PyTorch with `cuda:0` / `torch.cuda.is_available()`.
- GPU memory is managed with `torch.cuda.empty_cache()` upon task completion.
- Driver: NVIDIA SMI 592.82 | CUDA 13.1.
