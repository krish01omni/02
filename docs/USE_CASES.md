# 02 Detailed Use Cases & End-to-End Playbooks

This guide demonstrates how **`02`** operates across six real-world engineering, research, local AI, and automation scenarios—showing which specialist roles activate, which scripts run, and how the **Triple-Gate Verification Protocol** prevents incomplete or fragile output.

---

## Use Case 1: Full-Stack Multi-File Feature Delivery

### Scenario
You want to add a new authenticated API service, database schema, background worker, and React dashboard to an existing repository without causing file merge conflicts, skipped tests, or half-wired mocks.

### How `02` Executes
1. **Bootstrap & Telemetry Gate:**
   - `bootstrap.py --target-dir .` creates `.02/` and initializes `state.json`.
   - `guardian.py --check-once` confirms host RAM/CPU headroom before parallel subagents spawn.
2. **Contract-First Design (`Lead Architect`, `Pro` Tier):**
   - Inspects existing project conventions and outputs exact TypeScript/Python interfaces, schema migrations, and a strict file ownership table so parallel `Builders` never overwrite each other's files.
3. **Parallel Construction (`Builders`, `Flash` / `Pro` Tier):**
   - Backend builder implements routes and schema; frontend builder implements UI components against the Architect's shared contract.
   - Before each parallel worker launches, the **Executive Director** checks `guardian.py --can-spawn`.
4. **Triple-Gate Validation:**
   - **Gate 1 (`QA Auditor`):** Runs build, typechecker, linter, and `pytest`/`jest` integration tests until exit code `0`.
   - **Gate 2 (`QA Auditor`):** Audits missing auth checks, malformed JSON payloads, empty states, and unclosed DB connections.
   - **Gate 3 (`Executive Director`):** Confirms every item in the original prompt is delivered and no temporary files leak into the repo.

### Example Activation Prompt
```text
/02 Build a rate-limited webhook ingestion API with SQLite persistence, retry worker,
and unit/integration tests. Ensure full Triple-Gate sign-off before finishing.
```

---

## Use Case 2: Zero-Cost Open-Source Discovery & Sandboxed Prototyping

### Scenario
You need an algorithm, UI parser, or media utility (e.g., an audio alignment library or parser) and want to evaluate open-source GitHub implementations safely without bloating your main repo's `package.json` or accidentally pulling in paid/proprietary code.

### How `02` Executes
1. **`Scavenger & Researcher` (`Flash` Tier)** searches GitHub for candidate tools and evaluates their `LICENSE` files before cloning:
   ```powershell
   python scripts/scavenger.py --inspect-license path/to/candidate_LICENSE
   ```
2. **Sandboxed Harvest:**
   - Approved MIT / Apache-2.0 / BSD / GPL / CC0 repositories are shallow-cloned strictly into `.02/resources/<repo_name>/`:
     ```powershell
     python scripts/scavenger.py --clone https://github.com/example/open-tool.git --project-dir .
     ```
   - `scavenger.py` audits the cloned `LICENSE*` file and appends provenance (`name`, `url`, `local_path`, `license`, `status`) into `.02/state.json`.
   - Any repository containing `"commercial license required"`, `"proprietary"`, or `"subscription"` is marked `REJECTED` and never integrated.
3. **Isolated Integration (`Builder` + `QA Auditor`):**
   - `Builder` writes clean adapter code in the main project or runs prototypes against `.02/resources/`, while `.gitignore` prevents external clones from ever being committed directly by accident.

---

## Use Case 3: Local GPU-Accelerated AI, Vision, or Media Pipelines

### Scenario
You are running heavy local compute—such as Whisper speech transcription, PyTorch embedding extraction, FFmpeg NVENC video encoding, or local vision inference on an NVIDIA GeForce RTX 4050—while running multiple agent checks simultaneously.

### Why `02` Fits
Standard naive throttlers either cap GPU unnecessarily (slowing CUDA jobs by 5x) or spawn too many Python workers concurrently and trigger an Out-Of-Memory crash on 16 GB system RAM.

### How `02` Executes
1. **Asymmetric Hardware Policy (`hardware_policy.md`):**
   - **GPU Unlocked (`100%`):** Workers are instructed to target `cuda:0` (`torch.cuda.is_available()`) and call `torch.cuda.empty_cache()` between batches.
   - **RAM/CPU Protected (`< 90%`):** `guardian.py --daemon` polls every second; if system RAM hits `87%`, `check_spawn_headroom()` returns `False` (`exit 1`) so CPU/RAM-heavy subagents pause while the GPU pipeline completes safely.
2. **Real-Time Observability (`dashboard.py`):**
   - Inspect live GPU utilization, VRAM consumption (`MB`), RAM availability, and active loop stage in one terminal command:
     ```powershell
     python scripts/dashboard.py --project-dir .
     ```

---

## Use Case 4: Stealth Web Automation & Persistent Portal Workflows

### Scenario
You need an agent to inspect a JavaScript-rendered web dashboard, download documentation behind a login session, or perform UI verification on sites that block headless bots via `navigator.webdriver` checks or reset cookies on every run.

### How `02` Executes
1. **`Stealth Web Specialist` (`Hybrid` Tier)** operates `scripts/stealth_browser.py`:
   - Launches Chromium with `launch_persistent_context` pointed at `<project_root>/.02/browser_profile/`.
   - Preserves cookies, OAuth sessions, and local storage across runs without re-authenticating every time.
   - Disables `--disable-blink-features=AutomationControlled` and injects an init script overriding `navigator.webdriver` to `undefined`.
   - Uses `generate_human_path()` (cubic Bézier curves + $\pm 1.5\text{ px}$ micro-tremor) and `human_type_delay()` (`50–150 ms`) for natural interaction timing.
2. **CLI Invocation:**
   ```powershell
   python scripts/stealth_browser.py --url https://example.com --output .02/logs/snapshot.png --project-dir .
   ```
3. **Graceful Degraded Mode:**
   - If Playwright is unavailable in a lightweight container or CI environment, `stealth_browser.py` automatically falls back to `urllib.request` with realistic browser headers for static HTML fetches.

> **Security Note:** Because `.02/browser_profile/` contains active session cookies, both `.02/.gitignore` and the root `.gitignore` strictly block it from version control.

---

## Use Case 5: Legacy Codebase Hardening & Regression Stabilization

### Scenario
You inherit a fragile repository with flaky tests, silent `except: pass` blocks, unclosed file handles, and unclear module boundaries.

### How `02` Executes
1. **Baseline Diagnosis (`Lead Architect` + `QA Auditor`):**
   - Maps dependencies and runs the current test suite to establish a reproducible failure baseline (**Gate 1** initially fails).
2. **Iterative Remediation Loop (`Build -> Test -> Run -> Analyze -> Improve`):**
   - `Builder` refactors modules one boundary at a time.
   - `QA Auditor` writes targeted boundary tests (empty inputs, oversized payloads, invalid encodings, closed resource verification) and rejects any patch that leaves leaked handles or mocked-out assertions (**Gate 2**).
3. **Empirical Exit Criterion:**
   - The loop cannot terminate until `Gate 1` exits with `0`, `Gate 2` logs an explicit sign-off in `.02/state.json`, and `Gate 3` confirms all user objectives are satisfied.

---

## Use Case 6: Token-Budgeted Long-Running Autonomous Research

### Scenario
You ask the agent to perform an extensive multi-source technical benchmark across 20+ repositories or synthesize a large multi-chapter engineering report where aggressive parallel LLM calls would otherwise trigger API HTTP `429` rate-limit lockouts.

### How `02` Executes
1. **Tiered Delegation:**
   - `Flash` / `Flash-Lite` workers handle file reading, repo scanning, log parsing, and structured summarization.
   - `Pro` tier (`Executive Director` & `Lead Architect`) synthesizes cross-cutting findings and adjudicates conflicting sources.
2. **Predictive `85%` Rate Margin:**
   - `TokenRatePacer` tracks rolling 60-second request counts (`RPM`) and token consumption (`TPM`) against `0.85 * max_rpm` and `0.85 * max_tpm`.
   - When `current_velocity()["status"] == "THROTTLED"`, the Director staggers worker batches rather than hitting provider hard ceilings and losing in-flight progress.

---

## Summary Matrix: Choosing the Right `02` Workflow

| Goal Type | Primary Roles Engaged | Key Script(s) | Primary Gate Focus |
| :--- | :--- | :--- | :--- |
| **New App / Feature** | Director, Architect, Builders, QA | `bootstrap.py`, `guardian.py` | Gate 1 (Tests) + Gate 2 (Edges) |
| **OSS Dependency Hunt** | Scavenger, Architect, Builder | `scavenger.py` | License Audit + `.02/resources/` isolation |
| **Local AI / CUDA Job** | Director, Builder, Guardian | `guardian.py`, `dashboard.py` | RAM `< 90%` + GPU `100%` unlocked |
| **Web Portal / UI Check** | Stealth Specialist, QA | `stealth_browser.py` | Persistent `.02/browser_profile/` + Privacy |
| **Refactor & Bug Hunt** | Architect, QA Auditor, Builder | `guardian.py`, `dashboard.py` | Strict non-mocked Gate 1 & Gate 2 loop |
