# Security & Privacy Policy

## Sandboxing Guarantees

- **Filesystem Containment:** `scavenger.py` clones external repositories strictly inside `<project_root>/.02/resources/` and `bootstrap.py` isolates runtime profiles and logs inside `<project_root>/.02/`.
- **Session Isolation:** `stealth_browser.py` stores browser cookies and state in `<project_root>/.02/browser_profile/`, excluded from git by both `.gitignore` and `.02/.gitignore`.
- **Zero-Cost License Gate:** `scavenger.py` checks repository `LICENSE*` files and rejects proprietary or commercial-license-required terms prior to integration.

## Secret & Personal Data Hygiene

- Never store API keys, `.env` files, session exports, or personal email addresses inside this repository.
- When running `02` on sensitive projects, inspect `.02/logs/` and `.02/state.json` before sharing bug reports externally.

## Reporting Issues

If you discover a path-traversal edge case, unintended credential persistence, or license-matching bypass in any `02` script, please open an issue or submit a minimal reproducible fix without posting live secrets or sensitive profile data.
