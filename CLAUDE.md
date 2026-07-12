# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Flask-LearnPython is a security-focused Flask backend for an interactive Python-learning site with tier-gated content, AI (OpenAI) assistance, and safe user-code execution via a separate sandbox service. It is a defensive-security learning project — the emphasis throughout the codebase is on trust boundaries, documented threats, and practical mitigations, not on production polish (see "Known limitations" below).

## Commands

Run locally (three separate processes/terminals, from repo root unless noted):
```bash
redis-server                                    # 1. rate-limit storage
docker build -t python-sandbox ./sandbox        # 2. build sandbox image (one-time / after Dockerfile changes)
cd sandbox && python3.12 execution_service.py   # 3. sandbox service on :5001
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python3.12 app.py                               # 4. Flask app on :5000
```

Tests:
```bash
pytest                       # run full suite
pytest tests/test_auth.py    # run a single test file
pytest tests/test_auth.py::test_name -q   # run a single test
```
Tests run with `TESTING=true` (CI does this automatically). In this mode `app.py` skips Supabase/OpenAI initialization entirely — do not add code paths that require live credentials to pass tests.

CI (`.github/workflows/ci.yml`): installs `requirements.txt`, runs `python -m compileall .` as a syntax check, then `pytest` with `TESTING=true`. No linter is configured.

## Environment / secrets

Two dotenv files, loaded via `python-dotenv`, both git-ignored:
- `password.env` (repo root) — `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_API_KEY`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `WEBHOOK_ID`, `MAIL_PASSWORD`, `SANDBOX_SECRET`, `SECRET_KEY`
- `sandbox/secret.env` — `SANDBOX_SECRET` (must match the value in `password.env`; it's the shared auth secret between the Flask app and the sandbox service)

Never hardcode real values for these — only example/placeholder values belong in docs or commits.

## Architecture

**Single-file Flask app**: nearly all routes, decorators, and integration logic live in `app.py` (~800 lines). There is no blueprint/package structure — when adding routes, follow the existing `# ─── Section ───` comment-banner convention used to delimit logical sections (auth routes, main routes, pricing, reset-password, ChatGPT, code execution, PayPal IPN).

**Request flow / trust boundary**: Browser → Flask app (`app.py`) → Supabase (Postgres, user/tier data) / OpenAI API (AI assistance) / PayPal IPN (payment webhooks) / sandbox service (user code execution). All user input is untrusted at route boundaries. User-submitted code is never executed inside the Flask process.

**Two independent services**:
1. `app.py` — the main Flask app (port 5000).
2. `sandbox/execution_service.py` — a separate minimal Flask app (port 5001) that receives code via `X-SANDBOX-SECRET`-authenticated POST `/execute` requests and runs it in a throwaway Docker container (`docker run --rm --network=none --memory=128m --cpus=0.5 --pids-limit=32`, built from `sandbox/Dockerfile` running `sandbox/runner.py`). `runner.py` additionally applies `resource` rlimits (CPU, memory, no subprocesses, output size) and a restricted `SAFE_BUILTINS` dict inside the container itself. These are defense-in-depth layers, not a substitute for the container boundary — see `docs/SANDBOX_SECURITY.md`. Note there is also an in-process `run_in_sandbox()` helper in `app.py` that shells out to `docker run` directly; the actual `/run_code` route instead forwards to the standalone sandbox service over HTTP.

**Auth & authorization model**: session-based (`session['logged_in']`, `session['email']`, etc. set in `/login`), not Flask-Login. Two decorator layers gate routes:
- `login_required` — requires an active session.
- `require_tier(*allowed_tiers)` — additionally checks the user's `tier_name` (from Supabase) against a set of allowed tier strings (`"Standard Tier"`, `"Additional Learning Materials"`, `"Full Access Plan"`). Tiers are looked up fresh from Supabase per request, not cached in the session.

Supabase access is lazy and test-safe: `require_supabase()` / `init_supabase()` no-op when `app.config["TESTING"]` is set (set automatically when running under pytest or when `TESTING=true`), so route handlers that call Supabase helpers must go through those helpers rather than using a module-level `supabase` client directly.

**Rate limiting**: Flask-Limiter, configured centrally in the `LIMITS` dict near the top of `app.py`, applied per-route via `@limiter.limit(LIMITS["KEY"])`. Storage is `memory://` under `TESTING`, Redis (`REDIS_URL`) otherwise. When adding a new abusable endpoint, add an entry to `LIMITS` rather than inlining a limit string.

**Content model**: lesson content is static JSON, not database-backed — `content/content.json` and `content/content2.json` are loaded once at import time and looked up by a `chp` query param in `/learn` and `/learn2`. Adding lesson content means editing these JSON files, not adding routes/templates for each lesson.

**PayPal IPN**: `/paypal/ipn` is CSRF-exempt (webhook) and verifies authenticity by posting the payload back to PayPal's IPN verify endpoint (`verify_ipn`) rather than trusting the request directly — this is the model to follow for any other webhook-style endpoint.

**CSRF**: Flask-WTF `CSRFProtect` is applied globally; JSON API-style endpoints that can't easily carry a CSRF token (`/chatgpt`, `/paypal/ipn`) are explicitly exempted with `@csrf.exempt` — exemptions should stay explicit and commented, not silently added.

## Security docs

Read before changing anything auth-, sandbox-, or webhook-related:
- `docs/SECURITY_OVERVIEW.md` — threat model + trust boundaries
- `docs/ATTACK_SURFACE.md` — route-by-route risks/mitigations
- `docs/SANDBOX_SECURITY.md` — why container isolation (not keyword/blacklist filtering) is the actual security boundary for code execution
- `docs/BUG_LEDGER.md` — tracked known issues

## Known limitations (don't "fix" these without discussion — they're documented tradeoffs)

- Single-file `app.py`; not split into blueprints.
- Session/cookie hardening is not production-grade.
- Logging is informational (`app.before_request` logs path/IP/form data), not a redacted, event-based security audit log.
- No account lockout / progressive delay on repeated failed logins.
