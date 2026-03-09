Additional consistency constraints:

- Use the same enum names and status names across all policy documents.
- If a workflow stage or approval state is introduced in one file, reuse it consistently in the others.
- Keep the distinction between:
  - extracted
  - rule_inferred
  - model_suggested
  - manual_reviewed
  - manual_overridden
  explicit everywhere it matters.
- Preserve the distinction between:
  - product-specific
  - case-specific
  - historically documented
  - well established
  - mixed evidence
  - uncertain
  across retrieval, conflict handling, and answer labeling.
- Make all policies compatible with a ChromaDB-based hybrid retrieval architecture.
