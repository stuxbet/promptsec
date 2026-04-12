# Risk Matrix

| Threat | Likelihood | Impact | Baseline Exposure | Defended Control |
| --- | --- | --- | --- | --- |
| Instruction override in retrieved email | High | High | Merged prompt may follow hidden instruction | Prompt separation plus validation and review |
| Data exfiltration request in document | Medium | High | Baseline may echo confidential tokens | Output validation plus refusal |
| Tool misuse request | Medium | Medium | Baseline may simulate export or command actions | Tool allowlist blocks unsupported actions |
| Summary poisoning | Medium | Medium | Baseline may repeat attacker narrative | Source labeling and route-to-review |
| Approval bypass in outbound draft | Medium | High | Baseline may claim approval exists | Approval gate and policy review |
