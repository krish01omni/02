"""
02 Open-Source Scavenger & Resource Harvester
Discovers, verifies 100% free open-source licenses, and sandboxes downloaded GitHub repositories
and web code strictly inside <project_root>/.02/resources/.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# Permitted free & open-source licenses (all free licenses, including copyleft, agreed in 02 architecture)
FREE_LICENSES = [
    "mit",
    "apache",
    "apache-2.0",
    "apache 2.0",
    "bsd-2-clause",
    "bsd-3-clause",
    "bsd",
    "gnu general public license",
    "gpl-2.0",
    "gpl-3.0",
    "gpl",
    "lgpl-2.1",
    "lgpl-3.0",
    "lgpl",
    "agpl-3.0",
    "agpl",
    "unlicense",
    "cc0",
    "public domain",
    "isc",
    "mpl-2.0",
    "mozilla public license"
]


def check_license_string(text: str) -> dict:
    """Analyze license text or name to verify it is 100% free with zero financial cost."""
    clean_text = text.lower()
    for lic in FREE_LICENSES:
        if lic in clean_text:
            return {
                "is_free": True,
                "detected_license": lic.upper(),
                "cost": "Zero Cost (Free Open-Source)",
                "status": "APPROVED"
            }

    # If it contains commercial purchase or proprietary terms
    if any(k in clean_text for k in ["proprietary", "commercial license required", "all rights reserved", "pay", "pricing", "subscription"]):
        return {
            "is_free": False,
            "detected_license": "PROPRIETARY / PAID",
            "cost": "Non-Free / Commercial Restriction",
            "status": "REJECTED"
        }

    # Default to open if generic permissive language found
    if "permission is hereby granted" in clean_text or "redistribution and use in source and binary" in clean_text:
        return {
            "is_free": True,
            "detected_license": "PERMISSIVE (CUSTOM)",
            "cost": "Zero Cost (Free Open-Source)",
            "status": "APPROVED"
        }

    return {
        "is_free": True,
        "detected_license": "UNSPECIFIED (ASSUMED FREE PUBLIC CODE)",
        "cost": "Zero Cost",
        "status": "FLAGGED_FOR_REVIEW"
    }


def clone_or_download_repo(repo_url: str, project_dir: str = ".") -> dict:
    """Clones a GitHub repository strictly into <project_dir>/.02/resources/<repo_name>."""
    resources_dir = Path(project_dir).resolve() / ".02" / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Derive repository name
    repo_name = repo_url.rstrip("/").split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    destination = resources_dir / repo_name
    print(f"[*] Scavenger targeting: {repo_url}")
    print(f"[*] Sandboxed destination: {destination}")

    if destination.exists():
        print(f"[!] Target folder {destination.name} already exists in sandbox. Skipping clone.")
        return {"status": "EXISTS", "path": str(destination)}

    cmd = ["git", "clone", "--depth", "1", repo_url, str(destination)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if res.returncode != 0:
            print(f"[!] Git clone failed: {res.stderr}")
            return {"status": "ERROR", "error": res.stderr}

        print(f"[✓] Successfully cloned into sandbox: {destination.name}")

        # Scan for LICENSE file
        license_file = None
        for f in destination.iterdir():
            if f.is_file() and f.name.upper().startswith("LICENSE"):
                license_file = f
                break

        lic_info = {"is_free": True, "detected_license": "UNKNOWN"}
        if license_file:
            with open(license_file, "r", encoding="utf-8", errors="ignore") as lf:
                lic_text = lf.read(2048)
            lic_info = check_license_string(lic_text)
            print(f"[✓] License audit: {lic_info['detected_license']} ({lic_info['status']})")

        # Update state.json
        state_file = Path(project_dir).resolve() / ".02" / "state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as sf:
                    sdata = json.load(sf)
                sdata.setdefault("scavenged_resources", []).append({
                    "name": repo_name,
                    "url": repo_url,
                    "local_path": str(destination.relative_to(Path(project_dir).resolve())),
                    "license": lic_info["detected_license"],
                    "status": lic_info["status"]
                })
                with open(state_file, "w", encoding="utf-8") as sf:
                    json.dump(sdata, sf, indent=2)
            except Exception:
                pass

        return {
            "status": "SUCCESS",
            "repo_name": repo_name,
            "sandbox_path": str(destination),
            "license": lic_info
        }
    except Exception as e:
        print(f"[!] Scavenging error: {e}")
        return {"status": "ERROR", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="02 Open-Source Scavenger & Resource Harvester")
    parser.add_argument("--clone", help="Git repository URL to clone into sandbox")
    parser.add_argument("--project-dir", default=".", help="Project root path")
    parser.add_argument("--test-license", action="store_true", help="Run license test suite")
    parser.add_argument("--inspect-license", help="Text or file path to inspect")
    args = parser.parse_args()

    if args.test_license:
        print("[*] Testing Scavenger License Verification...")
        samples = [
            ("MIT License sample", "Permission is hereby granted, free of charge, to any person obtaining a copy of this software (MIT)..."),
            ("Apache 2.0 sample", "Licensed under the Apache License, Version 2.0 (the 'License')..."),
            ("GPL 3.0 sample", "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007..."),
            ("Commercial restriction", "Proprietary Software. Commercial license required. All rights reserved.")
        ]
        for name, text in samples:
            res = check_license_string(text)
            print(f"  Sample: {name:25} -> Status: {res['status']:10} | Lic: {res['detected_license']}")
        sys.exit(0)

    if args.inspect_license:
        if os.path.exists(args.inspect_license):
            with open(args.inspect_license, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read(2048)
        else:
            text = args.inspect_license
        res = check_license_string(text)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    if args.clone:
        result = clone_or_download_repo(args.clone, args.project_dir)
        sys.exit(0 if result.get("status") in ["SUCCESS", "EXISTS"] else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
