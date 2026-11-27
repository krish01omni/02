"""
02 Bootstrap Initializer
Provisions the project-level .02/ workspace scaffold and verifies runtime dependencies.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


DEFAULT_STATE = {
    "team_status": "READY",
    "active_goal": None,
    "active_stage": "IDLE",  # RESEARCH, BUILD, TEST, RUN, ANALYZE, LEARN, IMPROVE
    "roster": {
        "director": {"state": "ONLINE", "model_tier": "pro"},
        "lead_architect": {"state": "IDLE", "model_tier": "pro"},
        "scavenger": {"state": "IDLE", "model_tier": "flash"},
        "stealth_operator": {"state": "IDLE", "model_tier": "hybrid"},
        "builder": {"state": "IDLE", "model_tier": "flash"},
        "qa_auditor": {"state": "IDLE", "model_tier": "flash"}
    },
    "triple_gate": {
        "gate_1_executable_tests": {"status": "PENDING", "last_run": None, "exit_code": None},
        "gate_2_qa_auditor_signoff": {"status": "PENDING", "auditor_notes": None},
        "gate_3_director_approval": {"status": "PENDING", "approved": False}
    },
    "hardware_safety": {
        "ram_ceiling_percent": 90.0,
        "cpu_ceiling_percent": 90.0,
        "gpu_acceleration": "100% UNLOCKED (RTX 4050 CUDA)"
    },
    "scavenged_resources": []
}


def scaffold_workspace(target_dir: Path):
    """Create .02/ workspace directories inside target project root."""
    dot_02 = target_dir / ".02"
    resources_dir = dot_02 / "resources"
    browser_dir = dot_02 / "browser_profile"
    logs_dir = dot_02 / "logs"
    state_file = dot_02 / "state.json"
    gitignore_file = dot_02 / ".gitignore"

    print(f"[*] Initializing 02 workspace in: {target_dir.resolve()}")
    resources_dir.mkdir(parents=True, exist_ok=True)
    browser_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Initialize state.json if not present
    if not state_file.exists():
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_STATE, f, indent=2)
        print("  [+] Created .02/state.json")
    else:
        print("  [.] .02/state.json already exists (preserved).")

    # Add .gitignore inside .02 to prevent checking in huge browser caches or temp artifacts
    if not gitignore_file.exists():
        with open(gitignore_file, "w", encoding="utf-8") as f:
            f.write("# Ignore browser cache and telemetry\nbrowser_profile/\nlogs/\n*.tmp\n")
        print("  [+] Created .02/.gitignore")

    print(f"  [+] Scavenger sandbox ready at: {resources_dir.resolve()}")
    print(f"  [+] Stealth browser profile ready at: {browser_dir.resolve()}")
    return dot_02


def check_python_dependencies():
    """Verify presence of helper packages (psutil, etc.)."""
    print("[*] Checking runtime dependencies...")
    missing = []
    try:
        import psutil
        print(f"  [✓] psutil {psutil.__version__} installed")
    except ImportError:
        missing.append("psutil")

    try:
        import playwright
        print(f"  [✓] playwright installed")
    except ImportError:
        print("  [-] playwright not found (recommended for stealth browser, can install with 'pip install playwright')")

    if missing:
        print(f"\n[!] Notice: Recommended package(s) missing: {', '.join(missing)}")
        print(f"    You can install them quickly using: pip install {' '.join(missing)}")
    else:
        print("  [✓] Core Python dependencies satisfied.")


def main():
    parser = argparse.ArgumentParser(description="02 Workspace Bootstrap")
    parser.add_argument("--target-dir", default=".", help="Target project directory to initialize")
    parser.add_argument("--dry-run", action="store_true", help="Test bootstrap logic without modifications")
    args = parser.parse_args()

    target = Path(args.target_dir).resolve()
    if args.dry_run:
        print(f"[Dry Run] Target directory: {target}")
        print(f"[Dry Run] Would provision .02/resources, .02/browser_profile, .02/logs, .02/state.json")
        check_python_dependencies()
        sys.exit(0)

    scaffold_workspace(target)
    check_python_dependencies()
    print("\n[✓] 02 Workspace initialization complete!")


if __name__ == "__main__":
    main()
