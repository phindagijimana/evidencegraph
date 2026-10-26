# Extraction (not in v0)

Span-anchored extraction is later. v0 claims are hand-entered YAML under `evaluation/items/`.

**Extraction is never gold (E5).** `extraction.origin.tag_machine_extracted` forces `origin: machine_extracted` and `extraction_is_gold: false`. Machine-generated edges stay marked until expert adjudication. The public export distinguishes origin. There are no extractor outputs in this tree.
