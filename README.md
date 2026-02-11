![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Flask](https://img.shields.io/badge/flask-web%20framework-lightgrey)
![CI](https://github.com/minkong05/Flask-Learnpython/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)


# Flask-LearnPython
A Flask backend for an interactive Python-learning platform: structured lessons, AI assistance, and **restricted code execution via a separate sandbox service**.

**Highlights**
- Session-based auth + tier-gated routes (free/premium)
- Supabase (Postgres) for users and tiers
- OpenAI API integration (AI assistant)
- PayPal IPN verification flow for subscription upgrades
- Defensive controls: CSRF, rate limiting, input validation, CI-safe testing mode


## Screenshots
### Home
<img src="assets/screenshots/home.png" alt="Home page" width="500" />

### Learning page
<img src="assets/screenshots/learn.png" alt="Learn Page" width="500" />

### Chatgpt and Code execution
<img src="assets/screenshots/chatgpt_CodeExecution.png" alt="Chatgpt_Code execution output" width="500" />


## Security focus
Built with a security-first mindset: define trust boundaries, document threats, and implement practical controls.

Implemented controls:
- Password hashing + session-based auth
- CSRF protection (Flask-WTF)
- Rate limiting (Flask-Limiter) on high-risk endpoints
- Input validation and payload limits
- Secrets loaded from env vars; CI runs without production credentials

Security design notes live in `/docs` (overview, attack surface, sandbox risks).


## Architecture (request flow)
Browser  
→ Flask app (auth, lessons, AI proxy, payments, access control)  
→ Supabase (Postgres) for user/tier data  
→ OpenAI API for AI assistance  
→ PayPal IPN for payment notifications  
→ Sandbox service for executing user-submitted Python

**Trust boundaries**
- All user input is untrusted at route boundaries
- User code is forwarded to a separate sandbox service (not executed inside Flask)


## Threat model (summary)
Threats considered:
- Brute-force / credential stuffing → rate limits on auth-related routes
- CSRF on state-changing endpoints → CSRF protection (with documented exceptions)
- Abuse of expensive endpoints (AI / code exec) → rate limits + daily usage limits
- RCE risk from user-submitted code → sandbox boundary + layered safeguards
- Webhook spoofing → server-side PayPal IPN verification

Detailed security notes: `/docs/SECURITY_OVERVIEW.md`, `/docs/ATTACK_SURFACE.md`, `/docs/SANDBOX_SECURITY.md`.


## Security controls implemented
- Password hashing (Werkzeug) + session-based auth
- CSRF protection (Flask-WTF)
- Rate limiting (Flask-Limiter) on sensitive routes (auth, AI, code exec, IPN)
- Input validation + payload limits
- Secrets loaded via env vars; CI runs without production credentials


## User code execution (security note)
User-submitted Python code is **not executed inside the Flask process**.  
The backend forwards code to a **separate sandbox service**, with layered safeguards:

- Reject high-risk keywords/patterns (basic static checks)
- Limit code size
- Enforce a request timeout when calling the sandbox service

Trade-off: keyword filtering is not equivalent to full container/VM isolation.  
See `/docs/SANDBOX_SECURITY.md` for risks and planned improvements.


## Features
Learning platform
- Structured lesson content served from JSON (`/content`)
- Tier-gated learning routes

Integrations
- OpenAI API for AI assistance
- Supabase (Postgres) for user storage and tier state
- PayPal IPN verification flow for subscription upgrades

User code execution
- `/run_code` forwards code to an external sandbox service
- Keyword checks + code size limits + request timeout


## Tech stack
- **Backend:** Flask (Python 3.12)
- **DB:** Supabase (Postgres)
- **Auth:** Flask sessions + password hashing
- **Security:** Flask-WTF (CSRF), Flask-Limiter (rate limiting), Flask-CORS
- **AI:** OpenAI API
- **Payments:** PayPal IPN
- **CI:** GitHub Actions (runs pytest in CI-safe mode)


## Run locally
### 1. Start Redis (required for rate limiting)
In a separate terminal:
```bash
redis-server
```
### 1. 2. Set up and run the application
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3.12 app.py
```
Open: `http://127.0.0.1:5000`


## Environment variables
> Never commit real secrets. Add `password.env` to `.gitignore`.
This project loads environment variables from `password.env` in the project root (not committed).

Create `password.env` (example values only):
```env
SECRET_KEY="dev-only-change-me"
OPENAI_API_KEY="sk-example"
SUPABASE_URL="https://example.supabase.co"
SUPABASE_API_KEY="example_key"
MAIL_PASSWORD="gmail_app_password"
WEBHOOK_ID="example"
```


## Testing + CI
Run tests: `pytest`

Current tests focus on defensive behaviour (auth input validation, login-required gates, run_code filtering/limits).
CI runs pytest with TESTING=true so external services (Supabase/OpenAI) are not required.


## Project Structure
```bash
Flask-Learnpython/
├── .github/workflows
├── content/
├── docs/
├── static/
├── templates/
├── tests/
├── app.py
├── requirements.txt
├── robots.txt
├── sitemap.xml
└── Procfile
```


## Limitations & next steps
Limitations:
- Single-file Flask app (app.py)
- Sandbox protection includes keyword filtering + external execution boundary (not full container/VM isolation)
- Tests exist, but broader integration coverage (auth/payment flows) is still limited
- Rate limiting/storage is not designed for multi-instance deployments

Next steps:
- Account lockout / progressive delays after repeated failed logins
- Password strength policy + email verification
- Expand integration tests (auth, PayPal IPN flow, sandbox boundary)
- Strengthen sandbox isolation guarantees


## Author
Built by **Kong Yu Min**  
University of Glasgow  
Python | Backend | Security