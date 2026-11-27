"""
02 Visual CLI Dashboard
Renders real-time hardware gauges (RAM/CPU/GPU), token pacing, team roster, and Triple-Gate status.
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Try importing guardian telemetry function
try:
    from guardian import get_memory_and_cpu, get_nvidia_gpu_status, TokenRatePacer, RAM_HARD_CEILING, CPU_HARD_CEILING
except ImportError:
    # If called from a different working directory
    sys.path.append(str(Path(__file__).parent))
    from guardian import get_memory_and_cpu, get_nvidia_gpu_status, TokenRatePacer, RAM_HARD_CEILING, CPU_HARD_CEILING


def render_progress_bar(percent, width=20, warn_thresh=85, crit_thresh=90):
    """Render a colored ASCII progress bar."""
    clamped = max(0, min(100, percent))
    filled = int(round(width * clamped / 100))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent:5.1f}%"


def render_dashboard(project_dir: str = "."):
    state_file = Path(project_dir).resolve() / ".02" / "state.json"
    state = {}
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            pass

    hw = get_memory_and_cpu()
    gpu = get_nvidia_gpu_status()
    pacer = TokenRatePacer()
    rate = pacer.current_velocity()

    print("\n" + "═" * 70)
    print("        02 AUTONOMOUS PRODUCTION TEAM — COMMAND DASHBOARD")
    print("═" * 70)

    # Hardware Gauges
    ram_bar = render_progress_bar(hw["ram_percent"])
    cpu_bar = render_progress_bar(hw["cpu_percent"])

    print("\n[ HARDWARE SENTINEL (Real-Time Gauges) ]")
    print(f"  RAM Usage:  {ram_bar}  (Hard Cap: < {RAM_HARD_CEILING}%)")
    if hw.get("ram_total_gb"):
        print(f"              {hw['ram_available_gb']} GB Free / {hw['ram_total_gb']} GB Total")
    print(f"  CPU Usage:  {cpu_bar}  (Hard Cap: < {CPU_HARD_CEILING}%)")

    if gpu.get("available"):
        gpu_bar = render_progress_bar(gpu["gpu_util_percent"])
        print(f"  NVIDIA GPU: {gpu_bar}  ({gpu['name']})")
        print(f"              VRAM: {gpu['memory_used_mb']} / {gpu['memory_total_mb']} MB | Policy: 100% UNLOCKED")
    else:
        print("  NVIDIA GPU: Idle / Host Rendering")

    # API Token Pacing
    print("\n[ PREDICTIVE TOKEN PACER ]")
    print(f"  Velocity:   RPM: {rate['current_rpm']} / {rate['rpm_safe_limit']} (85% Safety Margin)")
    print(f"  Status:     {rate['status']} (Zero 429 Lockouts Guarantee)")

    # Team Roster
    roster = state.get("roster", {
        "director": {"state": "ONLINE", "model_tier": "pro"},
        "lead_architect": {"state": "READY", "model_tier": "pro"},
        "scavenger": {"state": "READY", "model_tier": "flash"},
        "stealth_operator": {"state": "READY", "model_tier": "hybrid"},
        "builder": {"state": "READY", "model_tier": "flash"},
        "qa_auditor": {"state": "READY", "model_tier": "flash"}
    })

    print("\n[ PRODUCTION TEAM ROSTER ]")
    for name, info in roster.items():
        role_title = name.replace("_", " ").title()
        status = info.get("state", "READY")
        tier = info.get("model_tier", "flash").upper()
        print(f"  • {role_title:20} : [{status:7}] (Model Tier: {tier})")

    # Triple Gate Status
    gates = state.get("triple_gate", {})
    g1 = gates.get("gate_1_executable_tests", {}).get("status", "PENDING")
    g2 = gates.get("gate_2_qa_auditor_signoff", {}).get("status", "PENDING")
    g3 = gates.get("gate_3_director_approval", {}).get("status", "PENDING")

    print("\n[ TRIPLE-GATE VERIFICATION STATUS ]")
    print(f"  Gate 1 (Automated Tests):        [{g1}]")
    print(f"  Gate 2 (Independent QA Auditor): [{g2}]")
    print(f"  Gate 3 (Director Final Sign-off):[{g3}]")

    # Scavenged resources
    res_list = state.get("scavenged_resources", [])
    if res_list:
        print(f"\n[ SANDBOXED RESOURCES ({len(res_list)}) ] (.02/resources/)")
        for item in res_list[-3:]:
            print(f"  - {item.get('name')}: {item.get('license')} ({item.get('status')})")

    print("\n" + "═" * 70)
    stage = state.get("active_stage", "IDLE")
    goal = state.get("active_goal", "Awaiting goal...")
    print(f"  Loop Stage: [{stage}] | Goal: {goal}")
    print("═" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="02 Visual Dashboard")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    args = parser.parse_args()
    render_dashboard(args.project_dir)


if __name__ == "__main__":
    main()
