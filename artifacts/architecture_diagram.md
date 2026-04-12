# Architecture Diagram

```mermaid
flowchart LR
    U[Student User] --> C[CLI]
    C --> A1[Baseline Assistant]
    C --> A2[Defended Assistant]
    A1 --> R[Retrieval Layer]
    A2 --> R
    R --> D[Synthetic Emails And Docs]
    A1 --> M[Model Backend]
    A2 --> M
    A2 --> P[Policy Layer]
    A2 --> V[Output Validators]
    A2 --> H[Approval Gate]
    A1 --> T[Simulated Tools]
    A2 --> T
    C --> E[Evaluation Harness]
    E --> O[Evidence Outputs]
```

The baseline path keeps the pipeline intentionally flat. The defended path inserts policy, validation, and approval checks between model output and simulated tool execution.
