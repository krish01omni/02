# Contributing to `02`

Contributions that improve reliability, cross-platform compatibility, test coverage, and documentation clarity are welcome.

## Development Setup

```powershell
git clone https://github.com/krish01omni/02.git
cd 02
python -m pip install -r requirements.txt
pytest -v
```

## Guidelines

1. **Preserve Privacy & Portability:** Never commit `.env` files, API tokens, `.02/` runtime directories, or hardcoded absolute paths containing OS usernames.
2. **Maintain Role Separation:** Keep orchestration policies in `SKILL.md` and `references/`, and keep executable automation deterministic and testable inside `scripts/`.
3. **Pass All Gates Before Opening a PR:**
   - **Gate 1:** `pytest -v` passes with exit code `0`.
   - **Gate 2:** Edge cases (missing `psutil`, missing `nvidia-smi`, missing `playwright`, empty/malformed `.02/state.json`) degrade gracefully without unhandled exceptions.
   - **Gate 3:** Documentation in `README.md` and `docs/` accurately reflects any changed CLI flags, constants, or schema fields.
