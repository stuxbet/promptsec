# Permission Matrix

| Capability | Baseline | Defended | Notes |
| --- | --- | --- | --- |
| Read synthetic emails | Allowed | Allowed | Simulated only |
| Search synthetic docs | Allowed | Allowed | Simulated only |
| Draft email text | Allowed | Allowed with review for sensitive external drafts | No real send |
| Flag item for review | Allowed | Allowed | Simulated queue only |
| Send external email | Simulated broad allowance | Blocked | Never reaches a real external system |
| Export data | Simulated broad allowance | Blocked | Used only to demonstrate unsafe baseline behavior |
| Run shell command | Simulated broad allowance | Blocked | No actual command execution |
| Network side effects | Disallowed by design | Disallowed by design | Optional LLM backend is isolated behind config |
