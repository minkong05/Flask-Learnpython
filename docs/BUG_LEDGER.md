## 🔴 BUG-001 — In-Memory Rate Limiting (Auth Bypass)

**Status** Fixed
**Severity:** Critical  
**Category:** Security / Abuse Prevention  
**Files:** app.py  
**Component:** Login, Chat endpoints  

### Description
Rate limiting uses a process-local Python dict, which fails under:

- multi-worker deployments  
- restarts  
- distributed attacks  

### Root Cause
Security control implemented without shared state.

### Impact
- Brute-force login attacks succeed  
- Chat/API abuse unbounded  
- OWASP A07 (Identification & Auth Failures)  

### Reproduction
1. Run app with 2 workers  
2. Alternate requests  
3. Rate limit never triggers  

### Priority
🚨 **Immediate**


## 🔴 BUG-002 — Python Sandbox Is Not OS-Isolated (RCE)
**Severity:** Critical  
**Category:** Security / Remote Code Execution  
**Files:** python-sandbox/*  

### Description
Sandbox relies on Python-level restrictions only.

### Root Cause
Python is not a safe sandbox language.

### Impact
- Full server compromise  
- Secret exfiltration  
- Filesystem access  

### Reproduction
Use known `__subclasses__` or object graph traversal exploits.

### Priority
🚨 **Immediate**



## 🟠 BUG-003 — Session Identity Fallback to IP
**Severity:** High  
**Category:** Authentication  
**Files:** app.py  

### Description
This line is dangerous:
`session.get(‘user_id’, request.remote_addr)`

### Root Cause
Identity and rate-limit keys conflated.

### Impact
- Session confusion  
- NAT collisions  
- Authorization ambiguity  

### Priority
**High**



## 🟠 BUG-004 — Missing Global Error Handling
**Severity:** High  
**Category:** Stability / Info Leak  

### Description
Unhandled exceptions can:

- crash requests  
- leak stack traces  
- break UX  

### Impact
- Security info disclosure  
- Poor reliability  


## 🟡 BUG-005 — No Centralized Security Headers
**Severity:** Medium  
**Category:** Security Hardening  

### Missing
- Content-Security-Policy  
- X-Frame-Options  
- Strict-Transport-Security  

### Impact
- XSS risk  
- Clickjacking  
- Downgrade attacks  


## 🟡 BUG-006 — Secrets Validation Missing
**Severity:** Medium  
**Category:** Configuration  

### Description
App assumes env vars exist.

### Impact
- Crashes at runtime  
- Silent misconfigurations  


## 🟡 BUG-007 — Logging Is Not Structured or Centralized
**Severity:** Medium  
**Category:** Observability  

### Impact
- Security incidents invisible  
- Hard to debug abuse  


## 🟢 BUG-008 — Test Coverage Gaps in Security Paths
**Severity:** Low  
**Category:** Testing  

### Missing Tests
- Sandbox escape attempts  
- Auth edge cases  
- Rate-limit exhaustion  