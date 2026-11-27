"""
Gate 1 & Gate 2 Automated Verification Suite for the 02 Skill Repository.
Verifies all 5 core scripts plus repository-wide privacy and sanitization invariants.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import bootstrap
import dashboard
import guardian
import scavenger
import stealth_browser


def test_bootstrap_scaffolds_and_preserves_state(tmp_path):
    """Verify .02/ directory provisioning and idempotent state preservation."""
    dot_02 = bootstrap.scaffold_workspace(tmp_path)
    assert (dot_02 / "resources").is_dir()
    assert (dot_02 / "browser_profile").is_dir()
    assert (dot_02 / "logs").is_dir()
    assert (dot_02 / ".gitignore").is_file()

    state_file = dot_02 / "state.json"
    assert state_file.is_file()
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["team_status"] == "READY"
    assert set(state["roster"].keys()) == {
        "director",
        "lead_architect",
        "scavenger",
        "stealth_operator",
        "builder",
        "qa_auditor",
    }

    # Modify state and confirm re-running scaffold preserves custom goal
    state["active_goal"] = "Preserved Goal"
    state_file.write_text(json.dumps(state), encoding="utf-8")
    bootstrap.scaffold_workspace(tmp_path)
    reloaded = json.loads(state_file.read_text(encoding="utf-8"))
    assert reloaded["active_goal"] == "Preserved Goal"

    gitignore_text = (dot_02 / ".gitignore").read_text(encoding="utf-8")
    assert "browser_profile/" in gitignore_text
    assert "logs/" in gitignore_text


def test_bootstrap_dry_run_makes_no_changes(tmp_path):
    """Verify --dry-run exits 0 without creating .02/."""
    res = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "bootstrap.py"), "--target-dir", str(tmp_path), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert res.returncode == 0
    assert not (tmp_path / ".02").exists()


def test_guardian_token_rate_pacer():
    """Verify 85% RPM/TPM sliding-window pacer and pruning logic."""
    pacer = guardian.TokenRatePacer(max_rpm=10, max_tpm=1000)
    # Safe RPM = 8.5, Safe TPM = 850
    for _ in range(4):
        pacer.record_request(tokens_used=100)
    vel = pacer.current_velocity()
    assert vel["current_rpm"] == 4
    assert vel["current_tpm"] == 400
    assert vel["rpm_safe_limit"] == 8
    assert vel["tpm_safe_limit"] == 850
    assert vel["status"] == "CLEAR"

    # Cross TPM safe threshold (850)
    pacer.record_request(tokens_used=500)
    vel_throttled = pacer.current_velocity()
    assert vel_throttled["current_tpm"] == 900
    assert vel_throttled["status"] == "THROTTLED"

    # Simulate entries older than 60s
    old_ts = time.time() - 65.0
    pacer.requests_history = [old_ts]
    pacer.tokens_history = [(old_ts, 999)]
    vel_pruned = pacer.current_velocity()
    assert vel_pruned["current_rpm"] == 0
    assert vel_pruned["current_tpm"] == 0
    assert vel_pruned["status"] == "CLEAR"


def test_guardian_check_once_writes_telemetry(tmp_path):
    """Verify --check-once persists guardian_telemetry into <project_dir>/.02/state.json."""
    bootstrap.scaffold_workspace(tmp_path)
    res = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "guardian.py"), "--project-dir", str(tmp_path), "--check-once"],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert res.returncode in (0, 2)
    state = json.loads((tmp_path / ".02" / "state.json").read_text(encoding="utf-8"))
    assert "guardian_telemetry" in state
    assert "last_health_check" in state
    assert "ram" in state["guardian_telemetry"]
    assert "rate_limiter" in state["guardian_telemetry"]


def test_dashboard_renders_without_error(tmp_path, capsys):
    """Verify progress bar clamping and full CLI dashboard rendering."""
    assert dashboard.render_progress_bar(-10, width=10) == "[░░░░░░░░░░] -10.0%"
    assert dashboard.render_progress_bar(150, width=10) == "[██████████] 150.0%"

    bootstrap.scaffold_workspace(tmp_path)
    dashboard.render_dashboard(str(tmp_path))
    captured = capsys.readouterr().out
    assert "02 AUTONOMOUS PRODUCTION TEAM" in captured
    assert "TRIPLE-GATE VERIFICATION STATUS" in captured


def test_scavenger_license_classification():
    """Verify FOSS approval, commercial rejection, and unknown flagging."""
    mit = scavenger.check_license_string("MIT License\nPermission is hereby granted, free of charge...")
    assert mit["is_free"] is True
    assert mit["status"] == "APPROVED"

    apache = scavenger.check_license_string("Licensed under the Apache License, Version 2.0")
    assert apache["is_free"] is True
    assert apache["status"] == "APPROVED"

    gpl = scavenger.check_license_string("GNU GENERAL PUBLIC LICENSE Version 3")
    assert gpl["is_free"] is True
    assert gpl["status"] == "APPROVED"

    paid = scavenger.check_license_string("Proprietary Software. Commercial license required. All rights reserved.")
    assert paid["is_free"] is False
    assert paid["status"] == "REJECTED"

    unknown = scavenger.check_license_string("Custom notes without standard license header.")
    assert unknown["status"] == "FLAGGED_FOR_REVIEW"


def test_scavenger_cli_test_license():
    """Verify scavenger.py --test-license CLI runs cleanly."""
    res = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "scavenger.py"), "--test-license"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert res.returncode == 0
    assert "APPROVED" in res.stdout
    assert "REJECTED" in res.stdout


def test_stealth_browser_human_kinematics():
    """Verify cubic Bezier endpoints, step counts, and keystroke latency range."""
    p0, p3 = (100.0, 100.0), (800.0, 600.0)
    assert stealth_browser.bezier_curve(p0, (200, 150), (600, 500), p3, 0.0) == p0
    assert stealth_browser.bezier_curve(p0, (200, 150), (600, 500), p3, 1.0) == p3

    path = stealth_browser.generate_human_path(p0, p3, steps=20)
    assert len(path) == 21
    assert abs(path[0][0] - p0[0]) <= 1.5
    assert abs(path[-1][1] - p3[1]) <= 1.5

    for _ in range(50):
        delay = stealth_browser.human_type_delay()
        assert 0.05 <= delay <= 0.15


def test_stealth_browser_cli_trajectory():
    """Verify stealth_browser.py --test-trajectory CLI exits 0."""
    res = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "stealth_browser.py"), "--test-trajectory"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert res.returncode == 0
    assert "Point 00:" in res.stdout
    assert "Point 10:" in res.stdout


def test_repo_privacy_and_sanitization():
    """Ensure no secrets, .env files, runtime .02/ state, or personal local paths exist in repo files."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for required_ignore in (".env", ".env.*", ".02/", "browser_profile/", "__pycache__/", "*.py[cod]", ".pytest_cache/"):
        assert required_ignore in gitignore, f"Missing required .gitignore rule: {required_ignore}"

    forbidden_tracked_dirs = {".02", "__pycache__", ".pytest_cache", "browser_profile"}
    forbidden_filenames = {".env", ".env.local", ".env.production", "credentials.json", "secrets.json"}

    secret_patterns = [
        re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
        re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}"),
        re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
        re.compile(r"\bAKIA[0-9A-Z]{16}"),
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    ]
    personal_path_pattern = re.compile(r"[A-Za-z]:[/\\]Users[/\\][^<>\\/\s\"']+", re.IGNORECASE)
    gmail_pattern = re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com", re.IGNORECASE)

    # Check git-tracked files if inside a git repository; otherwise scan non-cache repo files
    if (REPO_ROOT / ".git").exists():
        import shutil

        git_bin = shutil.which("git")
        if git_bin:
            tracked = subprocess.run(
                [git_bin, "-C", str(REPO_ROOT), "ls-files"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if tracked.returncode == 0 and tracked.stdout.strip():
                files_to_scan = [REPO_ROOT / line for line in tracked.stdout.splitlines() if line.strip()]
            else:
                files_to_scan = [p for p in REPO_ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
        else:
            files_to_scan = [
                p for p in REPO_ROOT.rglob("*")
                if p.is_file() and not any(part in {".git", "__pycache__", ".pytest_cache"} for part in p.parts)
            ]
    else:
        files_to_scan = [
            p for p in REPO_ROOT.rglob("*")
            if p.is_file() and not any(part in {".git", "__pycache__", ".pytest_cache"} for part in p.parts)
        ]

    for path in files_to_scan:
        assert not any(part in forbidden_tracked_dirs for part in path.parts), f"Forbidden runtime directory tracked: {path}"
        assert path.name not in forbidden_filenames, f"Forbidden secret file found: {path}"
        assert path.suffix != ".pyc", f"Compiled bytecode file found: {path}"

        content = path.read_text(encoding="utf-8", errors="ignore")
        for pat in secret_patterns:
            assert not pat.search(content), f"Potential secret pattern {pat.pattern} found in {path}"
        assert not personal_path_pattern.search(content), f"Local personal path found in {path}"
        assert not gmail_pattern.search(content), f"Personal email address found in {path}"
