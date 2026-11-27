# 02 Scripts, CLI & State Reference

Complete reference for every script in `scripts/`, the global installer `install_global.ps1`, and the persistent `.02/state.json` schema.

---

## 1. Workspace Scaffold Layout

Running `bootstrap.py` provisions the following isolated directory structure inside any target project root:

```text
<project_root>/
└── .02/
    ├── .gitignore          # Ignores browser_profile/, logs/, *.tmp
    ├── state.json          # Team roster, Triple-Gate status, telemetry, scavenged manifests
    ├── resources/          # Shallow-cloned open-source repositories (scavenger.py)
    ├── browser_profile/    # Persistent Chromium user-data-dir (stealth_browser.py)
    └── logs/               # Telemetry & execution artifacts
```

---

## 2. `scripts/bootstrap.py`

Provisions `.02/` inside `--target-dir` and checks core Python dependencies (`psutil`, `playwright`).

### CLI Usage

```powershell
python scripts/bootstrap.py [--target-dir PATH] [--dry-run]
```

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--target-dir` | `.` | Target project root where `.02/` will be created. |
| `--dry-run` | `False` | Prints planned actions and runs dependency checks without modifying disk. |

### Behavior Details
- Creates `.02/resources`, `.02/browser_profile`, and `.02/logs` idempotently (`exist_ok=True`).
- Writes `DEFAULT_STATE` to `.02/state.json` **only if it does not already exist** (preserving active project state on re-runs).
- Writes `.02/.gitignore` containing `browser_profile/`, `logs/`, and `*.tmp` if missing.

---

## 3. `scripts/guardian.py`

Samples host RAM, CPU, and NVIDIA GPU metrics, tracks sliding-window API RPM/TPM velocity, and writes telemetry to `.02/state.json`.

### Constants

| Constant | Value | Meaning |
| :--- | :--- | :--- |
| `RAM_HARD_CEILING` | `90.0` | RAM percentage ceiling; status switches from `HEALTHY` to `ALERT`/`THROTTLED`. |
| `RAM_THROTTLE_TRIGGER` | `87.0` | Admission threshold above which `check_spawn_headroom()` blocks new workers. |
| `CPU_HARD_CEILING` | `90.0` | CPU percentage ceiling for `HEALTHY` status. |
| `CPU_THROTTLE_TRIGGER` | `85.0` | Admission threshold above which `check_spawn_headroom()` blocks new workers. |
| `API_RATE_SAFETY_MARGIN` | `0.85` | Caps `TokenRatePacer` safe RPM/TPM at 85% of configured ceilings. |

### CLI Usage

```powershell
python scripts/guardian.py [--project-dir PATH] [--check-once | --can-spawn | --daemon]
```

| Flag | Exit Codes | Description |
| :--- | :--- | :--- |
| `--project-dir` | — | Project root containing `.02/state.json` (default: `.`). |
| `--check-once` | `0` (`HEALTHY`) / `2` (`ALERT`) | Prints RAM/CPU/GPU/rate snapshot and updates `.02/state.json`. |
| `--can-spawn` | `0` (safe) / `1` (throttled) | Evaluates `ram_percent < 87.0 and cpu_percent < 85.0`. |
| `--daemon` | `0` on `SIGINT` | Polls every `1.0s`, emits threshold warnings, and continuously updates `.02/state.json`. |

### Python API Highlights
- `get_memory_and_cpu() -> dict` — Returns `ram_percent`, `ram_available_gb`, `ram_total_gb`, `cpu_percent`, and `psutil_available`.
- `get_nvidia_gpu_status() -> dict` — Queries `nvidia-smi`; returns `available`, `name`, `gpu_util_percent`, `memory_used_mb`, `memory_total_mb`, `temp_c`, and `policy`.
- `TokenRatePacer(max_rpm=1000, max_tpm=1_000_000)` — Exposes `record_request(tokens_used=0)` and `current_velocity()`.

---

## 4. `scripts/dashboard.py`

Renders a human-readable ASCII command dashboard aggregating live Guardian telemetry, `TokenRatePacer` velocity, roster states, Triple-Gate status, and the last 3 scavenged resources.

### CLI Usage

```powershell
python scripts/dashboard.py [--project-dir PATH]
```

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--project-dir` | `.` | Project root containing `.02/state.json`. |

---

## 5. `scripts/scavenger.py`

Audits open-source licenses for zero financial cost and shallow-clones repositories strictly inside `<project_dir>/.02/resources/<repo_name>/`.

### CLI Usage

```powershell
python scripts/scavenger.py [--clone REPO_URL] [--project-dir PATH] [--test-license] [--inspect-license TEXT_OR_PATH]
```

| Flag | Description |
| :--- | :--- |
| `--clone` | Shallow-clones (`git clone --depth 1`) into `.02/resources/`, scans any `LICENSE*` file, and logs the entry to `.02/state.json`. Exits `0` on `SUCCESS`/`EXISTS`, `1` on error. |
| `--project-dir` | Target project root (default: `.`). |
| `--test-license` | Runs built-in license classification checks across MIT, Apache 2.0, GPL 3.0, and proprietary samples. |
| `--inspect-license` | Reads a file path (up to 2048 bytes) or raw text string and prints structured JSON classification. |

### `check_license_string(text)` Return Values

| Result `status` | `is_free` | Trigger Condition |
| :--- | :--- | :--- |
| `APPROVED` | `True` | Matches `FREE_LICENSES` (MIT, Apache, BSD, GPL, LGPL, AGPL, Unlicense, CC0, Public Domain, ISC, MPL 2.0) or standard permissive grant text. |
| `REJECTED` | `False` | Contains proprietary/commercial terms (`proprietary`, `commercial license required`, `all rights reserved`, `pay`, `pricing`, `subscription`). |
| `FLAGGED_FOR_REVIEW` | `True` | No recognized license keywords found; requires manual/Director check. |

---

## 6. `scripts/stealth_browser.py`

Provides cubic Bézier cursor path calculation, human keystroke latency jitter, and persistent-profile browser fetching with Playwright + `urllib` fallback.

### CLI Usage

```powershell
python scripts/stealth_browser.py [--url URL] [--output FILE] [--project-dir PATH] [--test-trajectory]
```

| Flag | Description |
| :--- | :--- |
| `--url` | Navigates to `URL` using persistent profile `<project_dir>/.02/browser_profile`. |
| `--output` | Saves `.png`/`.jpg` screenshot (Playwright) or HTML text dump to `FILE`. |
| `--project-dir` | Project root holding `.02/browser_profile` (default: `.`). |
| `--test-trajectory` | Generates and prints an 11-point cubic Bézier curve from `(100, 100)` to `(800, 600)`. |

### Python API Highlights
- `bezier_curve(p0, p1, p2, p3, t)` — Evaluates cubic Bézier point at parameter `t`.
- `generate_human_path(start, end, steps=25)` — Returns list of `(x, y)` coordinates with randomized dual control points and $\pm 1.5\text{ px}$ micro-tremor.
- `human_type_delay()` — Returns uniform random delay in `[0.05, 0.15]` seconds.

---

## 7. `install_global.ps1` & `plugin.json`

Installs `02` as a global Antigravity plugin on Windows under `$env:USERPROFILE\.gemini\config\plugins\02`:
- Writes `plugin.json` (`name: "02-autonomous-team"`, `version: "1.0.0"`).
- Copies `SKILL.md`, `scripts/`, and `references/` into `skills\02\`.

---

## 8. `.02/state.json` Schema Overview

Initialized by `bootstrap.py` and enriched at runtime by `guardian.py` and `scavenger.py`:

```json
{
  "team_status": "READY",
  "active_goal": null,
  "active_stage": "IDLE",
  "roster": {
    "director": { "state": "ONLINE", "model_tier": "pro" },
    "lead_architect": { "state": "IDLE", "model_tier": "pro" },
    "scavenger": { "state": "IDLE", "model_tier": "flash" },
    "stealth_operator": { "state": "IDLE", "model_tier": "hybrid" },
    "builder": { "state": "IDLE", "model_tier": "flash" },
    "qa_auditor": { "state": "IDLE", "model_tier": "flash" }
  },
  "triple_gate": {
    "gate_1_executable_tests": { "status": "PENDING", "last_run": null, "exit_code": null },
    "gate_2_qa_auditor_signoff": { "status": "PENDING", "auditor_notes": null },
    "gate_3_director_approval": { "status": "PENDING", "approved": false }
  },
  "hardware_safety": {
    "ram_ceiling_percent": 90.0,
    "cpu_ceiling_percent": 90.0,
    "gpu_acceleration": "100% UNLOCKED (RTX 4050 CUDA)"
  },
  "scavenged_resources": [],
  "guardian_telemetry": {
    "ram": { "ram_percent": 0.0, "ram_available_gb": 0.0, "ram_total_gb": 0.0, "cpu_percent": 0.0, "psutil_available": true },
    "gpu": { "available": false, "name": "N/A", "gpu_util_percent": 0.0, "memory_used_mb": 0.0, "memory_total_mb": 0.0, "policy": "N/A" },
    "rate_limiter": { "current_rpm": 0, "current_tpm": 0, "rpm_safe_limit": 850, "tpm_safe_limit": 850000, "status": "CLEAR" },
    "status": "HEALTHY"
  },
  "last_health_check": "YYYY-MM-DD HH:MM:SS"
}
```
