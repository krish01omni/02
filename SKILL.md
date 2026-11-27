---
name: 02
description: >-
  Autonomous multi-agent production team engine. Use whenever the user says "activate 02",
  "/02", or asks for an autonomous team of specialized AI agents working iteratively in a loop
  (Research -> Build -> Test -> Run -> Analyze -> Learn -> Improve) with strict hardware limits,
  token rate budgeting, stealth browser automation, and free open-source resource scavenging.
---

# 02: Autonomous Multi-Agent Production Team

`02` is an autonomous, self-governing software engineering and research agency that executes complex project goals iteratively. It organizes work into a hierarchical team led by an **Executive Director**, staffed by **Specialist Employees**, backed by a real-time **Hardware & Rate Guardian**, and validated through a **Triple-Gate Verification Protocol**.

---

## 1. Quick Start & Activation

Whenever the user prompts:
> *"activate 02"* or *"/02"* or requests autonomous production team execution on any task:

*(Replace `<02_SKILL_DIR>` below with either your project-local skill directory such as `.agents/skills/02` or your global Antigravity plugin path `%USERPROFILE%\.gemini\config\plugins\02\skills\02`.)*

### Phase 1: Zero-Config Bootstrap
1. Locate the current project root directory.
2. Run the bootstrap initialization script:
   ```powershell
   python "<02_SKILL_DIR>/scripts/bootstrap.py" --target-dir .
   ```
3. Verify that `<project_root>/.02/` has been provisioned:
   - `.02/resources/` (Isolated storage for scavenged GitHub repos and assets)
   - `.02/browser_profile/` (Persistent, isolated real Chrome profile for stealth automation)
   - `.02/logs/` (Team activity and telemetry logs)
   - `.02/state.json` (Milestones, active workers, rate budget, and gate passes)

### Phase 2: Launch Hardware & Rate Guardian
Launch the guardian sentinel to enforce hardware ceilings and token rate pacing:
```powershell
python "<02_SKILL_DIR>/scripts/guardian.py" --check-once
```
If ongoing background monitoring is required during long tasks, spawn it as a background task with `--daemon`.

### Phase 3: Display Team Dashboard & Await / Engage Goal
Run the visual dashboard to report system health and team readiness:
```powershell
python "<02_SKILL_DIR>/scripts/dashboard.py"
```

---

## 2. Hardware Protection Envelope & Safety Rules

The Guardian strictly enforces your PC safety specifications:
- **RAM Ceiling:** **Strictly < 90% at all times**. If RAM approaches 88%, the Guardian throttles concurrency and queues memory-heavy tasks. RAM will never be allowed to reach or exceed 90%.
- **CPU Ceiling:** **Strictly < 90% at all times**. Dynamically balances thread execution to prevent system freezing or stuttering.
- **NVIDIA GPU Utilization:** **Up to 100% Unlocked**. Hardware acceleration (CUDA, PyTorch, TensorRT, video/image processing, or local inference) is fully permitted to run at maximum GPU throughput on the NVIDIA GeForce RTX 4050.

---

## 3. Token Budgeting & Predictive Rate Pacing

To prevent HTTP 429 lockouts and optimize token consumption:
1. **Tiered Model Routing:**
   - **Lightweight / Fast Models (Flash / Flash-Lite):** Scavenging GitHub, parsing docs, formatting logs, writing unit tests, running shell verification.
   - **Deep Reasoning Models (Pro):** Lead Architecture design, complex multi-file logic, root-cause debugging, and final holistic sign-off.
2. **Predictive Rate Pacer:**
   - Limits API velocity to **85% of RPM/TPM ceilings**.
   - Introduces jittered delay buffers when token bursts occur, ensuring uninterrupted operation without API bans or rate exhaustion.

---

## 4. The Specialist Employee Roster

When `02` runs, the primary agent acts as or orchestrates the **Executive Director**, delegating to specialized subagents defined in [`references/roles.md`](./references/roles.md):

| Role | Primary Function | Primary Tools |
| :--- | :--- | :--- |
| **Executive Director** | High-level orchestration, goal decomposition, token budget control, and Gate 3 evaluation. | Task Management, Subagent Delegation |
| **Lead Architect** | System diagrams, interface definitions, database schemas, and modular contract design. | Codebase exploration, Documentation |
| **Scavenger & Researcher** | Scours GitHub and the web for free tools/code. Ensures zero financial cost (all open-source licenses allowed). | `scripts/scavenger.py`, Search, Git |
| **Stealth Web Specialist** | Interacts with websites/web apps using human mouse curves and typing cadence. | `scripts/stealth_browser.py`, Playwright |
| **Builder / Engineers** | Writes modular, production-grade source code, handles dependencies, compiles, and refactors. | File editing, Compilers, Linters |
| **QA Auditor** | Writes automated unit/integration tests, executes code, performs regression analysis (Gate 2). | Test runners (`pytest`, `jest`, `cargo`) |

---

## 5. Free Open-Source Resource Scavenging

When the team requires external libraries, templates, or GitHub repositories:
1. **Zero Financial Cost:** The Scavenger validates the repository license. Any open-source license (MIT, Apache 2.0, BSD, GPL, LGPL, AGPL, Unlicense, CC0) is accepted, provided it requires no financial payment.
2. **Project Sandboxing:** All scavenged assets are cloned/downloaded **strictly into**:
   ```text
   <project_root>/.02/resources/
   ```
   No global system folders or parent directories are polluted.

---

## 6. The Autonomous Loop: Triple-Gate Verification

The team executes in a continuous loop:
$$\text{Research} \longrightarrow \text{Build} \longrightarrow \text{Test} \longrightarrow \text{Run} \longrightarrow \text{Analyze} \longrightarrow \text{Learn \& Improve}$$

The loop repeats until the deliverable satisfies the **Triple-Gate Verification Protocol**:
- **Gate 1 (Automated Execution Tests):** Code must build and pass 100% of executable tests, linters, and runtime health checks with exit code `0`.
- **Gate 2 (Independent QA Auditor):** The QA Auditor independently audits the implementation against edge cases, stress conditions, and security guidelines.
- **Gate 3 (Executive Director Sign-Off):** The Director evaluates the final solution against the user's initial prompt and overarching vision before marking the task complete.

See [`references/triple_gate.md`](./references/triple_gate.md) for full gate criteria.
