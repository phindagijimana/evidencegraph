# EvidenceGraph

Binds a claim to scoped evidence. Incomparable atlas or cohort is **Qualifies**, not Contradicts. Missing code is Unknown.

EVI already owns the name. Extraction is not gold. Not a paper-agent.

## Go

```bash
pip install git+https://github.com/phindagijimana/evidencegraph.git
evidencegraph load evaluation/items/I003.yaml
```

```python
from evidencegraph import load, ingest
load("I003.yaml", store="./store")
```

Python 3.11+. Network off by default. Optional `--network --source europepmc|crossref` still stores metadata only when a local OA record exists. Optional `--live-license` may look up a Crossref / Europe PMC license when no local record exists; it still refuses non-OA and never stores full text. Pilot DOIs are fixtures unless a real OA license was recorded from Crossref.

Optional agent transport (load / ingest only): `python -m evidencegraph.mcp`

```bash
pytest tests
```

[Methods](docs/EvidenceGraph_Methods.md) · Apache-2.0
