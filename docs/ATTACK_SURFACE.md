# Attack Surface Analysis

This document enumerates externally reachable entry points into the Flask-LearnPython application and evaluates their security risks and mitigations.

An attack surface includes:
- HTTP routes
- Authentication flows
- External service integrations
- Any user-controlled input that influences execution


## /register (GET, POST)
### Description
Allows a new user to create an account.

### Inputs
- username
- email
- password

### Threats
- Automated account creation / abuse
- Weak password selection
- User enumeration
- Injection via input fields

### Existing Mitigations
- Password hashing for stored credentials
- CSRF protection enabled globally (ensure JSON auth endpoints handle CSRF correctly)
- Rate limiting on registration to reduce automated abuse

### Remaining Risks
- Weak password policy (no minimum length/complexity rules)
- Lack of CAPTCHA / bot defence
- Potential user enumeration depending on error messaging


## /login (GET, POST)
### Description
Authenticates a user and establishes a session.

### Inputs
- email
- password (JSON body)

### Threats
- Credential stuffing
- Brute-force login attempts
- User enumeration via response messages
- Session fixation / session hijacking

### Existing Mitigations
- Password hashing verification
- Session-based authentication
- Rate limiting on login attempts to reduce brute force / credential stuffing

### Remaining Risks
- No account lockout / progressive delay after repeated failures
- Session cookies are not explicitly hardened via config (e.g., Secure/HttpOnly/SameSite)
- If CSRF is enabled globally, JSON-based auth routes require careful handling (either provide CSRF tokens or explicitly document exemptions)


## /logout (GET)
### Description
Clears the user session.

### Inputs
- None

### Threats
- CSRF-based forced logout

### Existing Mitigations
- Login required (prevents unauthenticated triggering)

### Remaining Risks
- Logout is performed via GET (should be POST)
- CSRF protection is not enforced on logout, enabling forced logout via cross-site requests


## Content & Learning Routes
### /, /unlock, /phase/<int>, /stage/<int>, /learn, /learn2
### Description
Serve protected learning content based on subscription tier.

### Inputs
- URL parameters
- Query parameters (e.g., `chp`)

### Threats
- Authorisation bypass via parameter tampering
- Content scraping
- Insecure direct object reference (IDOR) style issues (if access checks are incorrect)

### Existing Mitigations
- Login required
- Tier-based authorisation checks on protected routes

### Remaining Risks
- Reliance on server-side enforcement only (no additional monitoring/alerting)
- No explicit access logging or alerting for suspicious scraping patterns


## /get_user_profile (GET)
### Description
Returns user profile data as JSON.

### Inputs
- Session-derived user email

### Threats
- Information disclosure
- Enumeration if a session is compromised

### Existing Mitigations
- Login required
- Server-side user lookup (session email → DB query)
- Default rate limits apply via global limiter configuration

### Remaining Risks
- Ensure only intended fields are returned (avoid accidental disclosure of internal fields)
- If endpoint becomes a target, consider tighter per-route rate limits


## Password Reset Flow
### /reset (GET, POST)
### Description
Initiates password reset via email.

### Inputs
- email (form data)

### Threats
- User enumeration
- Email bombing / abuse of reset flow

### Existing Mitigations
- Signed, time-limited token reset flow
- Rate limiting on reset request to reduce email bombing

### Remaining Risks
- User enumeration risk: the UI may give different feedback depending on whether the email exists
- No password strength policy (weak passwords may be set during reset)
- Token reuse invalidation is not implemented (token remains valid until expiry)


### /reset/&lt;token&gt; (GET, POST)
### Description
Resets user password using a time-limited token.

### Inputs
- reset token (URL)
- new_password
- confirm_password

### Threats
- Token guessing (low probability but worth considering)
- Weak password reuse

### Existing Mitigations
- Signed, time-limited token (e.g., 15 minutes)
- Password hashing on update
- Rate limiting on token route to reduce automated guessing

### Remaining Risks
- No password strength policy
- No token reuse invalidation (token remains valid until expiry)


## Chat & AI Integration
### /chatgpt (POST)
### Description
Processes user queries and forwards them to the OpenAI API.

### Inputs
- message text (JSON)

### Threats
- Prompt injection (content integrity risk)
- Abuse leading to cost exhaustion
- Denial-of-service via repeated queries
- Injection into rendered HTML (if output is rendered unsafely)

### Existing Mitigations
- Login required
- Rate limiting on AI endpoint to reduce abuse/cost exhaustion
- Daily usage limit per user
- Message length restriction
- CI/testing mode disables external API calls (prevents secret exposure in CI)

### Remaining Risks
- Output is rendered as HTML; ensure safe rendering rules to reduce XSS risk
- Prompt injection can manipulate responses (content integrity rather than server compromise)
- Cost-exhaustion is reduced by rate limits and daily quotas, but still possible at scale


## Code Execution (CRITICAL)
### /run_code (POST)

### Description
Accepts user-submitted Python code and executes it inside a **separate local sandbox service** that runs each execution in a **per-run Docker container** (OS-level isolation).

### Inputs
- Python source code (JSON body)

### Threats
- Remote Code Execution (RCE) attempts
- Sandbox escape (container escape / misconfiguration)
- Infinite loops / resource exhaustion
- Abuse at scale (cost / CPU exhaustion)

### Existing Mitigations
- Authentication required
- Rate limiting on code execution requests
- Code length restriction
- Sandbox request authenticated via `X-SANDBOX-SECRET`
- Per-run Docker container with:
  - `--network=none`
  - strict CPU/memory/PID limits
  - enforced execution timeout / termination

### Trust dependency
Security relies on correct Docker runtime configuration and host hardening:
- no privileged containers
- no unsafe volume mounts
- no host networking
- Docker daemon secured

### Remaining Risks
- Containers share the host kernel; kernel vulnerabilities can enable escape
- Flask-side request timeouts must be paired with **reliable container termination**


## Payment & Webhooks
### /paypal/ipn (POST)
### Description
Receives PayPal Instant Payment Notifications and updates order records.

### Inputs
- PayPal IPN POST data

### Threats
- Spoofed webhook requests
- Replay attacks
- Tampered payment status
- Duplicate transaction processing

### Existing Mitigations
- Server-side IPN post-back verification with PayPal (`cmd=_notify-validate`)
- Payment status validation
- Idempotent order handling (insert/update by order_id)
- Rate limiting on webhook endpoint to reduce flooding

### Remaining Risks
- CSRF is exempted (expected for server-to-server webhooks); misconfiguration would be dangerous without verification
- No explicit replay detection beyond idempotent DB updates
- Ensure the verification endpoint matches the environment (sandbox vs production)
- Ensure audit logging for payment status changes


## Static & File Serving
### /<filename>
### Description
Serves files from application root.

### Inputs
- URL path parameter

### Threats
- Path traversal
- Sensitive file exposure

### Existing Mitigations
- Flask `send_from_directory`

### Remaining Risks
- Serving files from the application root increases attack surface and raises the risk of sensitive file exposure
- No allowlist of allowed filenames/types (recommend restricting to a small allowlist such as robots.txt/favicon.ico)


### /sitemap.xml
### Description
Serves sitemap XML.

### Inputs
- None

### Threats
- Information disclosure
- File read errors

### Existing Mitigations
- Explicit file existence checks

### Remaining Risks
- Minimal (low impact)


## Summary of High-Risk Attack Surfaces
### Critical
- /run_code
- /paypal/ipn

### High
- /login
- /register
- /chatgpt
- /reset

### Medium
- Content routes with tier enforcement
- /get_user_profile (depends on returned fields and monitoring)