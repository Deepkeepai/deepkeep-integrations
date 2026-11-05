# Security Policy

## Reporting a Vulnerability

Please report suspected vulnerabilities privately through your normal DeepKeep security contact or by opening a private security advisory in the repository, if enabled.

Do not include real DeepKeep API keys, Open WebUI credentials, chat logs, or customer data in public issues.

## Operational Notes

- The Open WebUI function runs as arbitrary Python inside the Open WebUI server process.
- Store DeepKeep credentials in Open WebUI Valves, not in source code.
- Enable Open WebUI valve encryption where available for better secret-at-rest protection.
- Test new releases in a non-production Open WebUI instance before enabling globally.
- Use `FAIL_MODE=fail_closed` for mandatory enforcement and `FAIL_MODE=fail_open` only when availability is preferred over enforcement.
