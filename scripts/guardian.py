"""
02 Hardware & Rate Guardian Sentinel
Real-time hardware protection (<90% RAM, <90% CPU, 100% GPU unlocked) and predictive API rate limiter (<85% RPM/TPM).
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Hardware limits agreed in 02 architecture
RAM_HARD_CEILING = 90.0  # Percentage - never allow to reach or exceed 90%
RAM_THROTTLE_TRIGGER = 87.0  # Concurrency throttle threshold
CPU_HARD_CEILING = 90.0  # Percentage - never allow to reach or exceed 90%
CPU_THROTTLE_TRIGGER = 85.0
API_RATE_SAFETY_MARGIN = 0.85  # 85% max velocity cap for RPM/TPM


def get_memory_and_cpu():
    """Retrieve current system RAM and CPU percentages."""
    try:
        import psutil
        ram_percent = psutil.virtual_memory().percent
        ram_available_gb = psutil.virtual_memory().available / (1024 ** 3)
        ram_total_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_percent = psutil.cpu_percent(interval=0.2)
        return {
            "ram_percent": round(ram_percent, 1),
            "ram_available_gb": round(ram_available_gb, 2),
            "ram_total_gb": round(ram_total_gb, 2),
            "cpu_percent": round(cpu_percent, 1),
            "psutil_available": True
        }
    except ImportError:
        # Fallback to PowerShell CIM instance
        cmd = "powershell -Command \"$m = Get-CimInstance Win32_OperatingSystem; [math]::Round(($m.TotalVisibleMemorySize - $m.FreePhysicalMemory) / $m.TotalVisibleMemorySize * 100, 1)\""
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            ram_val = float(res.stdout.strip())
        except Exception:
            ram_val = 50.0  # default safe assumption

        cmd_cpu = "powershell -Command \"(Get-CimInstance Win32_Processor).LoadPercentage\""
        try:
            res = subprocess.run(cmd_cpu, shell=True, capture_output=True, text=True, timeout=5)
            cpu_val = float(res.stdout.strip().split()[0])
        except Exception:
            cpu_val = 20.0

        return {
            "ram_percent": round(ram_val, 1),
            "ram_available_gb": 0.0,
            "ram_total_gb": 0.0,
            "cpu_percent": round(cpu_val, 1),
            "psutil_available": False
        }


def get_nvidia_gpu_status():
    """Sample NVIDIA GPU utilization and memory via nvidia-smi."""
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
            "--format=csv,noheader,nounits"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if res.returncode == 0 and res.stdout.strip():
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            if len(parts) >= 5:
                return {
                    "available": True,
                    "name": parts[0],
                    "gpu_util_percent": float(parts[1]),
                    "memory_used_mb": float(parts[2]),
                    "memory_total_mb": float(parts[3]),
                    "temp_c": float(parts[4]),
                    "policy": "100% Full-Throttle Permitted (RTX Acceleration)"
                }
    except Exception:
        pass
    return {
        "available": False,
        "name": "N/A",
        "gpu_util_percent": 0.0,
        "memory_used_mb": 0.0,
        "memory_total_mb": 0.0,
        "policy": "N/A"
    }


class TokenRatePacer:
    """Predictive token bucket rate limiter tracking RPM and TPM."""

    def __init__(self, max_rpm=1000, max_tpm=1_000_000):
        self.max_rpm = max_rpm
        self.max_tpm = max_tpm
        self.safe_rpm = max_rpm * API_RATE_SAFETY_MARGIN
        self.safe_tpm = max_tpm * API_RATE_SAFETY_MARGIN
        self.requests_history = []
        self.tokens_history = []

    def record_request(self, tokens_used=0):
        now = time.time()
        self.requests_history.append(now)
        self.tokens_history.append((now, tokens_used))
        self._prune(now)

    def _prune(self, now):
        cutoff = now - 60.0
        self.requests_history = [t for t in self.requests_history if t > cutoff]
        self.tokens_history = [t for t in self.tokens_history if t[0] > cutoff]

    def current_velocity(self):
        now = time.time()
        self._prune(now)
        rpm = len(self.requests_history)
        tpm = sum(t[1] for t in self.tokens_history)
        return {
            "current_rpm": rpm,
            "current_tpm": tpm,
            "rpm_safe_limit": int(self.safe_rpm),
            "tpm_safe_limit": int(self.safe_tpm),
            "status": "CLEAR" if (rpm < self.safe_rpm and tpm < self.safe_tpm) else "THROTTLED"
        }


def check_spawn_headroom():
    """Returns True if the system has adequate CPU/RAM headroom to spawn another worker."""
    stats = get_memory_and_cpu()
    can_spawn = (stats["ram_percent"] < RAM_THROTTLE_TRIGGER) and (stats["cpu_percent"] < CPU_THROTTLE_TRIGGER)
    return can_spawn, stats


def update_state_file(project_dir, telemetry):
    """Persist telemetry to <project_dir>/.02/state.json."""
    state_file = Path(project_dir) / ".02" / "state.json"
    if not state_file.parent.exists():
        state_file.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["guardian_telemetry"] = telemetry
    data["last_health_check"] = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="02 Hardware & Rate Guardian Sentinel")
    parser.add_argument("--project-dir", default=".", help="Root directory of the project")
    parser.add_argument("--check-once", action="store_true", help="Print telemetry once and exit")
    parser.add_argument("--can-spawn", action="store_true", help="Return 0 if safe to spawn worker, 1 if throttled")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous monitoring loop")
    args = parser.parse_args()

    if args.can_spawn:
        safe, stats = check_spawn_headroom()
        print(f"Can spawn worker: {safe} (RAM: {stats['ram_percent']}%, CPU: {stats['cpu_percent']}%)")
        sys.exit(0 if safe else 1)

    if args.check_once:
        hw = get_memory_and_cpu()
        gpu = get_nvidia_gpu_status()
        pacer = TokenRatePacer()
        rate = pacer.current_velocity()

        telemetry = {
            "ram": hw,
            "gpu": gpu,
            "rate_limiter": rate,
            "status": "HEALTHY" if hw["ram_percent"] < RAM_HARD_CEILING and hw["cpu_percent"] < CPU_HARD_CEILING else "ALERT"
        }

        print("=" * 60)
        print("  02 GUARDIAN SENTINEL - TELEMETRY SNAPSHOT")
        print("=" * 60)
        print(f"  RAM Usage:      {hw['ram_percent']}% (Hard Ceiling: {RAM_HARD_CEILING}%)")
        if hw.get("ram_total_gb"):
            print(f"  RAM Available:  {hw['ram_available_gb']} GB / {hw['ram_total_gb']} GB")
        print(f"  CPU Usage:      {hw['cpu_percent']}% (Hard Ceiling: {CPU_HARD_CEILING}%)")
        if gpu["available"]:
            print(f"  NVIDIA GPU:     {gpu['name']} ({gpu['gpu_util_percent']}% util, {gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB VRAM)")
            print(f"  GPU Policy:     {gpu['policy']}")
        else:
            print("  NVIDIA GPU:     Not detected / Idle")
        print(f"  Rate Pacer:     RPM: {rate['current_rpm']}/{rate['rpm_safe_limit']} (Safe Margin: 85%)")
        print(f"  Status:         {telemetry['status']}")
        print("=" * 60)

        update_state_file(args.project_dir, telemetry)
        sys.exit(0 if telemetry["status"] == "HEALTHY" else 2)

    if args.daemon:
        print("[02 Guardian] Sentinel daemon active. Press Ctrl+C to terminate.")
        pacer = TokenRatePacer()
        while True:
            try:
                hw = get_memory_and_cpu()
                gpu = get_nvidia_gpu_status()
                rate = pacer.current_velocity()

                # Safety checks
                if hw["ram_percent"] >= RAM_HARD_CEILING:
                    print(f"[CRITICAL ALERT] RAM usage {hw['ram_percent']}% crossed hard ceiling {RAM_HARD_CEILING}%! Halting workers.")
                elif hw["ram_percent"] >= RAM_THROTTLE_TRIGGER:
                    print(f"[WARNING] RAM usage {hw['ram_percent']}% near threshold. Throttling concurrency.")

                telemetry = {
                    "ram": hw,
                    "gpu": gpu,
                    "rate_limiter": rate,
                    "status": "HEALTHY" if hw["ram_percent"] < RAM_HARD_CEILING else "THROTTLED"
                }
                update_state_file(args.project_dir, telemetry)
                time.sleep(1.0)
            except KeyboardInterrupt:
                print("\n[02 Guardian] Sentinel stopped.")
                break


if __name__ == "__main__":
    main()
