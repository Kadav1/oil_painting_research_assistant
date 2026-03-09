Additional alignment constraints:

- Treat the docs and schemas as canonical source-of-truth inputs.
- Reuse field names exactly as defined in the schema layer.
- Reuse enum values exactly as defined in controlled_vocabulary.json.
- If a documentation rule and a convenience shortcut conflict, follow the documentation rule.
- Keep product-specific, case-specific, historical, and general evidence distinct in code and retrieval logic.
- Ensure chunk metadata stored in ChromaDB remains compatible with documented filtering and approval rules.
- Retrieval traces, review records, conflict records, and duplicate cluster handling must all be represented in code, not only implied.
