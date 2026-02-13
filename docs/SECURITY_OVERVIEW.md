# Security Overview

## System Purpose
Flask-Learnpython is a web-based learning platform that allows authenticated users to:
- Execute Python code in a sandboxed environment
- Manage accounts and authentication
- Interact with learning content
- Process payments (PayPal integration)


## Assets to Protect
- User credentials (passwords, sessions)
- User-submitted code
- Execution environment (sandbox)
- Payment flow integrity
- Server resources (CPU, memory, filesystem)
- Secrets (API keys, database credentials)


## Trust Boundaries
- Browser ↔ Flask Web Server
- Flask Web Server ↔ External Sandbox Service
- Flask Web Server ↔ Database
- Flask Web Server ↔ PayPal IPN/Webhook
- Flask Web Server ↔ Sandbox Service (local service that runs code in Docker)


## Threat Actors
- Anonymous internet users (no authentication)
- Authenticated but malicious users
- Automated bots (brute force, scraping, DoS)
- Compromised third-party services (sandbox, PayPal)


## Threat Model (STRIDE)
### Spoofing
- Session hijacking via stolen cookies
- Fake PayPal IPN requests

### Tampering
- Modification of user-submitted code payloads
- Manipulation of request parameters

### Repudiation
- Users denying execution of malicious code
- Disputed payment events

### Information Disclosure
- Leakage of environment variables
- Access to other users’ data
- Sandbox escape revealing server filesystem

### Denial of Service
- Infinite loops in code execution
- High CPU/memory payloads
- Login brute force attacks

### Elevation of Privilege
- Sandbox breakout to host system
- Gaining admin-level access via logic bugs


## Controls mapping (where implemented)
- Auth + sessions: Flask routes + decorators
- Rate limiting: Flask-Limiter on auth/AI/code/IPN routes
- CSRF: Flask-WTF (with explicit exemptions documented where needed)
- Flask authenticates sandbox requests using X-SANDBOX-SECRET
- Sandbox executes code in short-lived Docker container with no network + resource limits + timeouts
- Payment integrity: PayPal IPN server-side verification before DB updates


## Existing Security Controls
- Password hashing (Werkzeug)
- CSRF protection (Flask-WTF)
- Rate limiting on sensitive routes
- Authentication required for code execution
- External sandbox service for isolation


## Assumptions & Known Risks
Assumptions:
- External sandbox service correctly enforces isolation
- HTTPS is used in deployment
- Environment variables are not leaked to the sandbox

Known Risks:
- Sandbox escape would compromise host system
- IPN/webhook spoofing if signature validation fails
- Resource exhaustion attacks may still succeed at scale
