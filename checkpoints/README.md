# checkpoints/

This project does not fine-tune or train any model. The defended pipeline wraps a
black-box LLM served over an OpenAI-compatible endpoint, so there are no model
weights to checkpoint.

This directory exists for repository-structure compliance and is intentionally empty.
If a future iteration adds adversarial fine-tuning (cf. Gemini paper §9), trained
adapter weights or LoRA checkpoints would be written here.
