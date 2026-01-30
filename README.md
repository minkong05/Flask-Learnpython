![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Flask](https://img.shields.io/badge/flask-web%20framework-lightgrey)
![CI](https://github.com/minkong05/Flask-Learnpython/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)


# Flask-LearnPython
Flask-LearnPython is an interactive learning platform designed to help users learn Python through structured lessons, examples, and AI assistance.
The application focuses on:
- clean backend architecture
- secure user authentication
- controlled execution of user-submitted Python code
- real integrations (AI, payments, database)

## Security Focus

This project was intentionally built with a **security-first mindset**, reflecting
real-world DevSecOps and application security concerns.

Security design decisions include:

- Authentication and session handling with hashed passwords
- CSRF protection and defensive input validation
- Rate limiting and abuse prevention mechanisms
- Secure handling of secrets via environment variables
- CI-safe design with external services disabled during automated testing
- Documented threat modeling and attack surface analysis (see `/docs`)
- Sandboxed execution of user-submitted Python code with layered defenses

The application is designed not just to function, but to be **analyzed, attacked,
and defended** as part of learning secure software development.


## Overview
Flask-LearnPython is a full-stack web application built with Flask that provides an interactive platform for learning Python.  
The application combines structured learning content, AI-assisted explanations, and a secure Python execution sandbox to create a practical learning environment.

The project focuses on real-world backend engineering concepts, including user authentication, tier-based access control, secure handling of user-submitted code, and integration with external services such as OpenAI, Supabase, and PayPal.


## Features
### User Authentication
- Login / logout
- Session-based authentication
- Tier-based access control (free vs premium)

### AI Learning Assistant
- AI-powered explanations and help
- Integrated via OpenAI API
  
### Secure Python Sandbox
- Executes user Python code in a restricted environment
- Prevents unsafe operations
- Designed with security in mind
  
### Payment Integration
- PayPal integration for premium access
- Tier upgrade logic
  
### Security
- CSRF protection
- Input validation
- Secure session handling
  
### Web Application
- Flask backend
- HTML templates + static assets
- SEO support (robots.txt, sitemap)


## Tech Stack
**Backend**
- Python
- Flask
- Flask-CORS
- Flask-WTF (CSRF)
- Flask-Mail

**Database**
- Supabase (PostgreSQL)

**Authentication & Security**
- Flask sessions
- Werkzeug password hashing
- CSRF protection
- Decorator-based access control
- Rate limiting & daily usage limits

**AI**
- OpenAI API (ChatGPT)

**Payments**
- PayPal IPN (Instant Payment Notification)


## Requirements
- Python 3.12
- pip
- Virtual environment recommended


## Installation
```bash
git clone https://github.com/minkong05/Flask-Learnpython.git
cd Flask-Learnpython
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```


## Environment Variables
Create a .env file in the project root.

### Example (.env.example):
- `SECRET_KEY=your_flask_secret_key`
- `OPENAI_API_KEY=your_openai_api_key`
- `SUPABASE_URL=your_supabase_project_url`
- `SUPABASE_API_KEY=your_supabase_service_key`
- `MAIL_PASSWORD=your_gmail_app_password`
- `WEBHOOK_ID=your_webhook_id`


## Running the App
`python3.12 app.py`
then open
`http://127.0.0.1:5000`

## Secure Python Sandbox (Design Note)
User-submitted Python code is executed in a restricted environment:
- No filesystem access
- No OS-level commands
- Limited built-ins
- Execution time controlled
This prevents malicious code execution while still allowing educational experimentation.


## Project Structure
```bash
Flask-Learnpython/
├── .github/workflows
├── content
├── docs
│   ├── ATTACK_SURFACE.md
│   ├── SANDBOX_SECURITY.md
│   └── SECURITY_OVERVIEW.md
├── python-sandbox
├── scripts
├── static
├── templates
├── tests
├── app.py
├── requirements.txt
├── README.md
├── robots.txt
├── sitemap.xml
└── Procfile
```

## Security Documentation
Detailed security analysis is available in `/docs`:

- **Security Overview** – system assets, trust boundaries, STRIDE threats
- **Attack Surface Analysis** – route-level threat identification
- **Sandbox Security Analysis** – risks of user-submitted code execution

## Security Testing
This project includes attacker-style security tests covering:
- Authentication failure paths
- Abuse and rate-limit scenarios
- Code execution input validation
- Denial-of-service prevention checks

Tests are written using pytest and focus on defensive behavior,
not just functional correctness.


## CI & Testing
This project includes a GitHub Actions CI pipeline that runs on every push and pull request.

The pipeline performs:
- Python syntax validation
- Automated security-focused tests using pytest
- CI-safe execution where external services (Supabase, OpenAI) are disabled

During CI runs, the application detects the `TESTING=true` environment variable and:
- Prevents outbound API calls
- Disables database access
- Ensures tests run deterministically without secrets

This design reflects real-world DevSecOps practices, where applications must be testable
in isolated environments without relying on production credentials.



## Limitations
- The application is currently implemented as a single-file Flask app (`app.py`), which can become harder to maintain as the project grows.
- The secure Python code execution sandbox relies on keyword blacklisting and an external execution service, which is not as robust as container-based isolation.
- Automated tests are not yet implemented for routes, authentication, or API integrations.
- The rate limiting and daily usage limits are stored in memory or database logic and are not designed for distributed or multi-instance deployments.
- Secrets such as the Flask secret key are partially generated at runtime and should be managed more securely in a production environment.
- The application assumes a single-instance deployment and does not include horizontal scaling support.


## Future Improvements
- Limit login attempts (e.g. lock the account or temporarily block login after 5 failed attempts) to prevent brute-force attacks.
- Add email verification during registration to ensure users register with a valid email address.
- Improve password security by enforcing stronger password rules (minimum length, symbols, numbers).
- Add automatic logout after a period of inactivity to improve session security.
- Add basic automated tests to check login, registration, and protected routes.
- Improve error handling and logging to make debugging easier in production.


## Author
Built by **Kong Yu Min**  
University of Glasgow  
Python | Backend | Security-focused Learning Platform
