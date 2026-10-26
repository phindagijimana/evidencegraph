# EvidenceGraph

Binds a claim to scoped evidence. Incomparable atlas or cohort is **Qualifies**, not Contradicts. Missing code is Unknown.

EVI already owns the name. Extraction is not gold. Not a paper-agent.

## Go

```bash
git clone https://github.com/phindagijimana/evidencegraph.git
cd evidencegraph && pip install -e .
evidencegraph load evaluation/items/I003.yaml
evidencegraph ingest --doi 10.9999/restricted-mock --license-check
```

Python 3.11+. Network off. No restricted full text. Pilot DOIs are fixtures, not journal articles.

```bash
pytest tests
```

[Methods](docs/EvidenceGraph_Methods.md) · Apache-2.0
