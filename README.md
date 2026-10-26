# EvidenceGraph

Binds a published claim to scoped evidence. Incomparable cohort or atlas is **Qualifies**, not Contradicts. Missing code is `unknown_not_assessed`.

EVI already owns the name “Evidence Graphs.” This repo is a binding/scoring protocol, not a new graph product. Extraction is not gold.

## Install

```bash
pip install -e .
```

Python 3.11+. Network off by default. No restricted full text.

## Use

```bash
evidencegraph load evaluation/items/I003.yaml
evidencegraph query --claim I003 --show-scope
evidencegraph export --jsonld --item evaluation/items/I001.yaml
evidencegraph retrieve --bm25 --query "hippocampal asymmetry" --k 5
evidencegraph ingest --doi 10.9999/restricted-mock --license-check
```

Pilot items are fixtures (`10.9999/eg.fixture.*`), not journal articles.

## Tests

```bash
pytest tests
```

## Docs

- [Methods](docs/EvidenceGraph_Methods.md) (E1–E5)
- [Literature map](docs/EvidenceGraph_Literature_Map.md)
- [Handbook](annotations/handbook.md)

Apache-2.0.
