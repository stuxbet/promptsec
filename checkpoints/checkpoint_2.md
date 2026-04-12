# Checkpoint 2

## Threat Model Progress
- Identified indirect prompt injection as the primary threat
- Defined trust levels and sensitivity labels for synthetic content
- Documented attack categories: override, exfiltration, tool misuse, poisoning, approval bypass

## Dataset Plan
- 35 synthetic content items
- At least 20 evaluation scenarios with benign, malicious, and edge coverage
- JSON fixture generation through `seed-data`

## Baseline Progress
- Vulnerable merged-prompt pipeline implemented
- Simulated broad tool permissions preserved for comparison
