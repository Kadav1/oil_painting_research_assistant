Additional consistency constraints:

- Use the same enum values across all schemas and vocab files.
- If a value appears in controlled_vocabulary.json, reuse it exactly in other files.
- Keep the distinction between:
  - source-level records
  - chunk-level records
  - field-level provenance
  - duplicate clusters
  - conflict records
  - review records
  clear and non-overlapping.
- Preserve the distinction between:
  - product-specific
  - case-specific
  - historically documented
  - well established
  - mixed evidence
  - uncertain
  in benchmark and answer-label structures where relevant.
- Make all schemas practical for later Python/Pydantic translation.
- Keep chunk and retrieval schemas compatible with ChromaDB metadata filtering.
