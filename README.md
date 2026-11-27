# 02 — Autonomous Multi-Agent Production Team

> **A self-governing multi-agent software engineering, research, and verification skill for Antigravity — engineered with real-time hardware safety ceilings, predictive token rate pacing, sandboxed open-source scavenging, stealth browser automation, and a Triple-Gate Verification Protocol.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](./requirements.txt)
[![Verification: Triple-Gate](https://img.shields.io/badge/Verification-Triple--Gate-2ea44f.svg)](./references/triple_gate.md)

---

## What is `02`?

**`02`** transforms a single AI coding assistant into a structured, hierarchical production agency. When activated (`activate 02` or `/02`), the primary agent operates as an **Executive Director** orchestrating five specialized roles across an iterative closed loop:

$$\text{Research} \longrightarrow \text{Build} \longrightarrow \text{Test} \longrightarrow \text{Run} \longrightarrow \text{Analyze} \longrightarrow \text{Learn \& Improve}$$

Rather than letting agents run unconstrained—burning API rate limits, exhausting host RAM/CPU, polluting project roots with unvetted dependencies, or declaring success without empirical execution—**`02`** enforces strict operational guardrails across four planes:

1. **Hierarchical Team Plane** — Separates orchestration (`Executive Director`), system design (`Lead Architect`), open-source discovery (`Scavenger`), humanized web interaction (`Stealth Web Specialist`), implementation (`Builder`), and adversarial verification (`QA Auditor`).
2. **Hardware & Rate Guardian Plane** — Monitors RAM (`< 90%` hard cap), CPU (`< 90%` hard cap), NVIDIA CUDA GPU utilization (`100%` unlocked for compute workloads), and sliding-window API velocity (`85%` RPM/TPM safety cap).
3. **Sandboxed Data & Asset Plane** — Isolates all scavenged repositories, persistent browser profiles, telemetry logs, and runtime state inside `<project_root>/.02/`.
4. **Triple-Gate Verification Plane** — Prevents premature task completion until deliverables clear **Gate 1 (Automated Execution Tests, Exit Code `0`)**, **Gate 2 (Independent QA Auditor Review)**, and **Gate 3 (Executive Director Holistic Sign-Off)**.

---

## Repository Structure

```text
02/
├── README.md                       # Project overview, installation, quick start, and navigation
├── SKILL.md                        # Antigravity Skill entrypoint & activation playbook
├── plugin.json                     # Antigravity plugin manifest
├── install_global.ps1              # Windows PowerShell installer for global Antigravity plugin setup
├── requirements.txt                # Runtime & testing dependencies (psutil, playwright, pytest)
├── LICENSE                         # MIT License
├── CONTRIBUTING.md                 # Contribution and extension guidelines
├── SECURITY.md                     # Security, privacy hygiene, and responsible use policy
├── .gitignore                      # Excludes runtime .02/ workspaces, .env files, keys, and caches
├── docs/
│   ├── ARCHITECTURE.md             # Deep-dive architecture, plane diagrams, state schema, and formulas
│   ├── USE_CASES.md                # Detailed use cases with end-to-end multi-agent workflows
│   ├── SCRIPTS_REFERENCE.md        # Full CLI flags, Python APIs, exit codes, and state.json contract
│   └── PRIVACY_AND_SAFETY.md       # Sandboxing, hardware protection, and PII/secret prevention guide
├── references/
│   ├── roles.md                    # Specialist employee roster, model tiers, and system prompt snippets
│   ├── hardware_policy.md          # RAM/CPU safety ceilings, worker pool formula, and GPU guidelines
│   └── triple_gate.md              # 3-stage verification protocol flowchart and sign-off checklists
├── scripts/
│   ├── bootstrap.py                # Provisions .02/ workspace scaffold and verifies dependencies
│   ├── guardian.py                 # Hardware telemetry sentinel, spawn gating, and TokenRatePacer
│   ├── dashboard.py                # Terminal CLI dashboard for hardware, rate, roster, and gate state
│   ├── scavenger.py                # License compliance verifier and sandboxed GitHub shallow cloner
│   └── stealth_browser.py          # Cubic Bézier mouse trajectory, keystroke jitter, persistent browser
└── tests/
    └── test_02_suite.py            # Automated test suite for all scripts & repository privacy checks
```

---

## Quick Start

### 1. Clone & Install Dependencies

```powershell
git clone https://github.com/krish01omni/02.git
cd 02
python -m pip install -r requirements.txt
# Optional: install Chromium binary for Playwright stealth browser automation
python -m playwright install chromium
```

### 2. Install as a Global Antigravity Skill (Windows)

Run the bundled installer to register `02` inside `%USERPROFILE%\.gemini\config\plugins\02`:

```powershell
.\install_global.ps1
```

Or install **per-project** by copying this repository (or its `SKILL.md`, `references/`, and `scripts/` folders) into `<your_project>/.agents/skills/02/`.

### 3. Bootstrap Any Target Project

From your target project root (or passing `--target-dir`), initialize the `.02/` sandbox, run the Guardian health snapshot, and inspect the team dashboard:

```powershell
# Phase 1: Provision <project_root>/.02/ scaffold
python path/to/02/scripts/bootstrap.py --target-dir .

# Phase 2: Run hardware & token-rate telemetry snapshot
python path/to/02/scripts/guardian.py --check-once --project-dir .

# Phase 3: Display real-time team command dashboard
python path/to/02/scripts/dashboard.py --project-dir .
```

### 4. Verify the Installation Locally

```powershell
pytest -v
```

---

## Architecture at a Glance

```mermaid
flowchart TB
    User([User Goal / /02 Activation]) --> Director[Executive Director<br/>Pro Tier — Orchestration & Gate 3]

    subgraph ControlPlane [Control & Governance Plane]
        Director --> Architect[Lead Architect<br/>Pro Tier — Specs & Contracts]
        Director --> Guardian[Guardian Sentinel<br/>RAM/CPU < 90% | API <= 85% RPM/TPM]
        Director --> Dashboard[CLI Command Dashboard<br/>Telemetry & Gate Visibility]
    end

    subgraph ExecutionPlane [Specialist Execution Plane]
        Architect --> Scavenger[Scavenger & Researcher<br/>Flash Tier — FOSS License Audit]
        Architect --> Stealth[Stealth Web Specialist<br/>Hybrid — Bezier & Persistent Profile]
        Architect --> Builder[Builder / Engineers<br/>Flash/Pro — Modular Implementation]
    end

    subgraph VerificationPlane [Triple-Gate Verification Loop]
        Builder --> G1{Gate 1<br/>Automated Tests<br/>Exit Code 0}
        G1 -- Fail --> Builder
        G1 -- Pass --> G2{Gate 2<br/>Independent QA Auditor<br/>Edge Cases & Leaks}
        G2 -- Reject --> Builder
        G2 -- Approve --> G3{Gate 3<br/>Executive Director<br/>Holistic Prompt Alignment}
        G3 -- Revise --> Builder
        G3 -- Approve --> Done([Verified Deliverable])
    end

    subgraph SandboxPlane [Project-Local Sandbox: .02/]
        State[(state.json)]
        Resources[(resources/)]
        Browser[(browser_profile/)]
        Logs[(logs/)]
    end

    Guardian <--> State
    Scavenger --> Resources
    Stealth <--> Browser
    ControlPlane --> Logs
```

---

## Core Operational Policies

| Domain | Policy / Ceiling | Mechanism | Reference |
| :--- | :--- | :--- | :--- |
| **System RAM** | Target $\le 85\%$, Throttle at $87\%$, Hard Cap $< 90\%$ | `guardian.py` + `Safe Workers` formula | [`hardware_policy.md`](./references/hardware_policy.md) |
| **System CPU** | Target $\le 80\%$, Throttle at $85\%$, Hard Cap $< 90\%$ | `check_spawn_headroom()` admission check | [`hardware_policy.md`](./references/hardware_policy.md) |
| **NVIDIA GPU** | Up to **100% Unlocked** (example: RTX 4050 / CUDA) | `nvidia-smi` telemetry + `cuda:0` guidance | [`hardware_policy.md`](./references/hardware_policy.md) |
| **API Rate Budget** | Maximum **85%** of RPM / TPM ceilings | `TokenRatePacer` 60s sliding window | [`guardian.py`](./scripts/guardian.py) |
| **Model Routing** | `Pro` for architecture/sign-off; `Flash` for execution/QA | Tiered assignment in `state.json` roster | [`roles.md`](./references/roles.md) |
| **External Code** | 100% zero-cost FOSS licenses; strictly sandboxed | `scavenger.py` -> `.02/resources/` | [`scavenger.py`](./scripts/scavenger.py) |
| **Web Automation** | Cubic Bézier mouse paths + key jitter + persistent profile | `stealth_browser.py` -> `.02/browser_profile/` | [`stealth_browser.py`](./scripts/stealth_browser.py) |
| **Completion** | Must pass Gates 1, 2, and 3 in sequence | `.02/state.json` gate records | [`triple_gate.md`](./references/triple_gate.md) |

---

## Primary Use Cases

- **Autonomous Multi-File Software Engineering** — Decompose a feature spec into contracts (`Lead Architect`), build modules in parallel (`Builders`), run real tests (`Gate 1`), and verify edge cases (`QA Auditor`).
- **Zero-Cost Open-Source Research & Rapid Prototyping** — Discover, license-audit, and shallow-clone GitHub repositories into `.02/resources/` without polluting your production codebase.
- **Resource-Safe Local AI & Media Pipelines** — Maximize NVIDIA CUDA GPU throughput (`100%`) for local inference, audio/video processing, or embeddings while guaranteeing host RAM/CPU stays below `90%`.
- **Authenticated & Anti-Bot Resilient Web Workflows** — Interact with web dashboards, documentation portals, or dynamic SPAs using a persistent isolated Chromium profile and humanized pointer/keyboard pacing.
- **High-Reliability Codebase Refactoring & Regression Hardening** — Use the adversarial QA Auditor persona (`Gate 2`) and strict exit-code-0 enforcement (`Gate 1`) to eliminate silent failures and resource leaks.

Read the full walkthroughs in [`docs/USE_CASES.md`](./docs/USE_CASES.md) and the deep architectural specification in [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

---

## Documentation Index

- [**Skill Entrypoint (`SKILL.md`)**](./SKILL.md) — Activation prompt contract and quick-start workflow used by Antigravity.
- [**System Architecture (`docs/ARCHITECTURE.md`)**](./docs/ARCHITECTURE.md) — Multi-plane design, role orchestration, math formulas, state transitions, and design boundaries.
- [**Detailed Use Cases (`docs/USE_CASES.md`)**](./docs/USE_CASES.md) — Six real-world production scenarios with role handoffs and verification traces.
- [**Scripts & CLI Reference (`docs/SCRIPTS_REFERENCE.md`)**](./docs/SCRIPTS_REFERENCE.md) — Complete documentation for all 5 Python utilities and `.02/state.json`.
- [**Privacy & Safety Guide (`docs/PRIVACY_AND_SAFETY.md`)**](./docs/PRIVACY_AND_SAFETY.md) — Sandboxing guarantees, secret isolation, and pre-publish hygiene.
- [**Specialist Roster (`references/roles.md`)**](./references/roles.md) — Detailed employee mandates and system prompt templates.
- [**Hardware Policy (`references/hardware_policy.md`)**](./references/hardware_policy.md) — Exact resource thresholds and concurrency formulas.
- [**Triple-Gate Protocol (`references/triple_gate.md`)**](./references/triple_gate.md) — Gate 1, Gate 2, and Gate 3 verification checklists.

---

## License & Security

Released under the [MIT License](./LICENSE). See [SECURITY.md](./SECURITY.md) for sandboxing boundaries, credential hygiene, and responsible web automation guidelines.
