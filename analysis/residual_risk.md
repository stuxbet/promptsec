# Residual Risk

Even with layered controls, the defended prototype still has residual risk.

- Rule-based validation can miss novel attack phrasing that does not match the current heuristics.
- Source labels rely on synthetic metadata and do not solve provenance in a real enterprise deployment.
- The optional external model backend may behave differently from the deterministic mock backend.
- The approval gate is simulated, so operational review latency and analyst quality are not measured here.
- Retrieval is intentionally simple and does not model every enterprise search failure mode.

The repo treats these as documented limitations for a class project rather than unresolved implementation defects.
