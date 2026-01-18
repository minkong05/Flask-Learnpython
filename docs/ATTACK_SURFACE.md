# Attack Surface Analysis

This document enumerates all externally reachable entry points
into the Flask-Learnpython application and evaluates their
security risks and mitigations.

An attack surface includes:
- HTTP routes
- Authentication flows
- External service integrations
- Any user-controlled input that influences execution


## /register (POST)
### Description
Allows a new user to create an account.

### Inputs
- username
- email
- password

### Threats
- Brute-force account creation
- Weak password selection
- User enumeration
- Injection via input fields

### Existing Mitigations
- Password hashing
- CSRF protection

### Remaining Risks
- Weak password policy
- Lack of CAPTCHA


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
- Session fixation

### Existing Mitigations
- Password hashing verification
- Session-based authentication

### Remaining Risks
- CSRF disabled
- No rate-limiting on login
- No account lockout
- Session cookies not explicitly hardened


## /logout (GET)
### Description
Clears the user session.

### Inputs
- None

### Threats
- CSRF-based forced logout

### Existing Mitigations
- Login required

### Remaining Risks
- Logout performed via GET
- CSRF protection not enforced


## Content & Learning Routes
## /, /unlock, /phase/<int>, /stage/<int>, /learn, /learn2
### Description
Serve protected learning content based on subscription tier.

### Inputs
- URL parameters
- Query parameters (chp)

### Threats
- Insecure Direct Object Reference (IDOR)
- Authorization bypass via parameter tampering
- Content scraping

### Existing Mitigations
- Login required
- Tier-based authorization checks

### Remaining Risks
- Reliance on server-side enforcement only
- No explicit access logging or alerting


## /get_user_profile (GET)
### Description
Returns user profile data as JSON.

### Inputs
- Session-derived user email

### Threats
- Information disclosure
- Enumeration if session compromised

### Existing Mitigations
- Login required
- Server-side user lookup

### Remaining Risks
- No explicit output filtering
- No rate-limiting


## Password Reset Flow
## /reset (GET, POST)
### Description
Initiates password reset via email.

### Inputs
- email (form data)

### Threats
- User enumeration
- Email bombing
- Abuse of reset functionality

### Existing Mitigations
- Token-based reset flow
- Email ownership verification

### Remaining Risks
- No rate-limiting
- Clear feedback when email exists


## /reset/<token> (GET, POST)
### Description
Resets user password using time-limited token.

### Inputs
- reset token (URL)
- new_password
- confirm_password

### Threats
- Token brute-forcing
- Weak password reuse

### Existing Mitigations
- Signed, time-limited token (15 min)
- Password hashing

### Remaining Risks
- No password strength policy
- No token reuse invalidation


## Chat & AI Integration
## /chatgpt (POST)
### Description
Processes user queries and forwards them to OpenAI API.

### Inputs
- User-controlled message text (JSON)

### Threats
- Prompt injection
- Abuse leading to cost exhaustion
- Denial of service via repeated queries
- Injection into rendered HTML

### Existing Mitigations
- Login required
- Daily usage limit per user
- Message length restriction

### Remaining Risks
- CSRF disabled
- No global rate-limiting
- Output rendered as HTML

## Code Execution (CRITICAL)
## /run_code (POST)
### Description
Accepts user-submitted Python code and forwards it to an external sandbox service for execution.

### Inputs
- Python source code (JSON body)

### Threats
- Remote Code Execution (RCE)
- Sandbox escape
- Infinite loops / resource exhaustion
- Logic bypass via obfuscation
- Abuse of external sandbox service

### Existing Mitigations
- Authentication required
- Blacklist-based keyword filtering
- Code length restriction
- Execution performed in external sandbox

### Assumptions
- Sandbox enforces strict CPU, memory, and filesystem isolation
- No access to environment variables
- Network access restricted

### Remaining Risks
- Blacklist bypass via encoding or dynamic imports
- Sandbox vulnerabilities
- No per-user execution rate-limit
- Blind trust in third-party sandbox


## Payment & Webhooks
## /paypal/ipn (POST)
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
- Server-side IPN verification with PayPal
- Payment status validation
- Idempotent order handling

### Remaining Risks
- CSRF disabled (expected but dangerous if misconfigured)
- No explicit replay detection
- No signature-based verification


## Static & File Serving
## /<filename>
### Description
Serves files from application root.

### Inputs
- URL path parameter

### Threats
- Path traversal
- Sensitive file exposure

### Existing Mitigations
- Flask send_from_directory

### Remaining Risks
- Serving root directory increases attack surface
- No allowlist of file types

## /sitemap.xml
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
