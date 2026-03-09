You are a senior schema designer and knowledge-systems architect.

Help me create the schema and machine-readable files for the Oil Painting Research Assistant project in phases.

This is a provenance-aware, source-aware, ChromaDB-based RAG system for oil painting knowledge.

We will create the files in this order:

1. controlled_vocabulary.json
2. source_register_schema.json
3. chunk_schema.json
4. field_provenance_schema.json
5. duplicate_cluster_schema.json
6. conflict_record_schema.json
7. review_record_schema.json
8. approval_state_schema.json
9. context_package_schema.json
10. retrieval_trace_schema.json
11. answer_label_schema.json
12. material_alias_map.json
13. product_alias_map.json
14. material_ontology_v1.json
15. benchmark_template.json
16. benchmark_gold_set_v1.json

For each file:
- first explain its role briefly
- then write the JSON fully
- keep enum values consistent with earlier files
- keep the structure implementation-friendly
- do not write code
- do not use invalid JSON
- do not invent conflicting values

Start with:
vocab/controlled_vocabulary.json
