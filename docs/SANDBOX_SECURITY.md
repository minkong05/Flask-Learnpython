# Sandbox Security Analysis
This document analyses the security risks of executing user-submitted Python code
and explains why multiple defensive layers are required, even when a sandbox is used.


## What stronger isolation means
A robust sandbox enforces isolation at the runtime level (e.g., container/VM boundaries), including:
- CPU/memory limits
- filesystem isolation
- network restrictions
- process termination guarantees


## Why Blacklist Filtering Is Unsafe
Blacklist-based filtering relies on matching specific keywords such as
`import os` or `exec`. This approach is unsafe because Python provides many
ways to perform the same operation without using those exact strings.

Attackers can bypass blacklists by:
- Using dynamic imports such as `__import__`
- Obfuscating keywords with Unicode or string concatenation
- Using alternative built-in functions not explicitly blocked
- Abusing language features that are difficult to enumerate exhaustively

Because it is impossible to block every dangerous pattern, blacklist filtering
cannot be relied upon for secure code execution.


## Resource Exhaustion
The HTTP request timeout only limits how long the Flask server waits
for a response from the sandbox service. It does not terminate user
code execution inside the sandbox and therefore does not prevent
resource exhaustion such as infinite loops or excessive CPU usage.


## Example bypass categories (high level)
Attackers may attempt to bypass keyword filters using:
- dynamic language features
- obfuscation (encoding, concatenation, alternate syntax)
- alternative APIs that achieve similar effects

Because these patterns are difficult to enumerate exhaustively, keyword filtering should be treated as a *helper*, not the primary security boundary.
