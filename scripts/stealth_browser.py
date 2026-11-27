"""
02 Stealth Web & App Automation Operator
Interacts with websites and web applications with human-like behavioral emulation
(Bezier mouse paths, keystroke jitter, persistent real Chrome profile, anti-bot evasion).
"""

import argparse
import json
import math
import os
import random
import sys
import time
from pathlib import Path

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def bezier_curve(p0, p1, p2, p3, t):
    """Cubic Bezier curve formula for natural human mouse trajectories."""
    x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
    y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
    return (x, y)


def generate_human_path(start, end, steps=25):
    """Generate realistic human cursor movements with micro-adjustments."""
    ctrl1 = (
        start[0] + (end[0] - start[0]) * random.uniform(0.2, 0.4) + random.uniform(-40, 40),
        start[1] + (end[1] - start[1]) * random.uniform(0.1, 0.3) + random.uniform(-40, 40)
    )
    ctrl2 = (
        start[0] + (end[0] - start[0]) * random.uniform(0.6, 0.8) + random.uniform(-40, 40),
        start[1] + (end[1] - start[1]) * random.uniform(0.7, 0.9) + random.uniform(-40, 40)
    )
    path = []
    for i in range(steps + 1):
        t = i / steps
        point = bezier_curve(start, ctrl1, ctrl2, end, t)
        # Add micro-tremor
        jitter_x = point[0] + random.uniform(-1.5, 1.5)
        jitter_y = point[1] + random.uniform(-1.5, 1.5)
        path.append((jitter_x, jitter_y))
    return path


def human_type_delay():
    """Human typing delay between keystrokes in seconds."""
    return random.uniform(0.05, 0.15)


def run_stealth_fetch(url: str, output_file: str = None, project_dir: str = "."):
    """Fetch webpage content or screenshot using stealth settings."""
    profile_dir = Path(project_dir).resolve() / ".02" / "browser_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Launching Stealth Operator against: {url}")
    print(f"[*] Utilizing persistent user profile: {profile_dir}")

    # Check if Playwright is available
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Launch persistent context to simulate real user browser
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--start-maximized"
                ],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )

            page = context.new_page()

            # Remove webdriver flag
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            # Human-like random scroll & pause
            time.sleep(random.uniform(1.0, 2.5))
            page.mouse.wheel(0, random.randint(200, 500))
            time.sleep(random.uniform(0.5, 1.2))

            title = page.title()
            print(f"[✓] Page loaded successfully: '{title}'")

            if output_file:
                if output_file.endswith(".png") or output_file.endswith(".jpg"):
                    page.screenshot(path=output_file)
                    print(f"[✓] Screenshot saved to: {output_file}")
                else:
                    content = page.content()
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[✓] HTML dump saved to: {output_file}")

            context.close()
            return True
    except ImportError:
        # Fallback to standard urllib with human headers
        import urllib.request
        print("[-] Playwright not installed. Falling back to HTTP request with human headers...")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                print(f"[✓] HTTP GET 200 OK ({len(data)} characters retrieved)")
                if output_file:
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(data)
                    print(f"[✓] Content saved to: {output_file}")
                return True
        except Exception as e:
            print(f"[!] Request failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="02 Stealth Browser Operator")
    parser.add_argument("--url", help="Target URL to navigate to")
    parser.add_argument("--output", help="Path to save HTML or screenshot")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--test-trajectory", action="store_true", help="Test Bezier curve trajectory calculation")
    args = parser.parse_args()

    if args.test_trajectory:
        start = (100, 100)
        end = (800, 600)
        path = generate_human_path(start, end, steps=10)
        print(f"[✓] Generated Bezier mouse curve points (Start: {start} -> End: {end}):")
        for i, pt in enumerate(path):
            print(f"  Point {i:02d}: ({pt[0]:.1f}, {pt[1]:.1f})")
        sys.exit(0)

    if args.url:
        success = run_stealth_fetch(args.url, args.output, args.project_dir)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
