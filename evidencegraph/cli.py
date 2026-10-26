"""CLI: ingest, load, query, evaluate, export --jsonld, retrieve --bm25. No model API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from baselines.bm25 import retrieve as bm25_retrieve
from evaluation.score import dump_score, score_item
from graph.query import query_claim
from graph.store import (
    ClaimStore,
    PACKAGE_ROOT,
    iter_claims,
    load_document,
    to_jsonld,
)
from ingest.resolve import LicenseRefused, ResolutionError, resolve


def _store(path: str | None) -> ClaimStore:
    root = Path(path) if path else Path.cwd() / ".evidencegraph_store"
    return ClaimStore(root)


def cmd_ingest(args: argparse.Namespace) -> int:
    try:
        record = resolve(
            args.doi,
            license_check=bool(args.license_check),
            store_dir=Path(args.store) if args.store else None,
        )
    except LicenseRefused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ResolutionError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(record, indent=2, default=str))
    return 0


def cmd_load(args: argparse.Namespace) -> int:
    store = _store(args.store)
    loaded = store.load_path(Path(args.path))
    print(json.dumps({"loaded": [c["claim_id"] for c in loaded]}, indent=2))
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    store = _store(args.store)
    record = query_claim(store, args.claim, show_scope=bool(args.show_scope))
    if record is None:
        print(f"unknown claim: {args.claim}", file=sys.stderr)
        return 1
    print(json.dumps(record, indent=2, default=str))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    if not args.jsonld:
        print("export requires --jsonld", file=sys.stderr)
        return 2
    document = load_document(Path(args.item))
    payload = [to_jsonld(claim) for claim in iter_claims(document)]
    printed = payload[0] if len(payload) == 1 else payload
    print(json.dumps(printed, indent=2, default=str))
    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    if not args.bm25:
        print("retrieve requires --bm25", file=sys.stderr)
        return 2
    hits = bm25_retrieve(args.query, k=int(args.k))
    print(json.dumps({"arm": "B0", "query": args.query, "hits": hits}, indent=2))
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    item = load_document(Path(args.item))
    pred = load_document(Path(args.pred))
    score = score_item(item, pred, arm=args.arm)
    print(json.dumps(score, indent=2))
    if args.out:
        dump_score(score, Path(args.out))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evidencegraph",
        description="Bind and score published claims. Not an evidence-graph product.",
    )
    parser.add_argument(
        "--store",
        default=None,
        help="Local YAML store directory (default: ./.evidencegraph_store)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="Resolve DOI/PMCID; refuse if not OA")
    p_ingest.add_argument("--doi", required=True)
    p_ingest.add_argument("--license-check", action="store_true")
    p_ingest.set_defaults(func=cmd_ingest)

    p_load = sub.add_parser("load", help="Load a hand-authored claim or gold item")
    p_load.add_argument("path")
    p_load.set_defaults(func=cmd_load)

    p_query = sub.add_parser("query", help="Read a stored claim; no model")
    p_query.add_argument("--claim", required=True)
    p_query.add_argument("--show-scope", action="store_true")
    p_query.set_defaults(func=cmd_query)

    p_eval = sub.add_parser("evaluate", help="Score a prediction against a gold item")
    p_eval.add_argument("--item", required=True)
    p_eval.add_argument("--pred", required=True)
    p_eval.add_argument("--arm", default="B6")
    p_eval.add_argument("--out", default=None)
    p_eval.set_defaults(func=cmd_evaluate)

    p_export = sub.add_parser("export", help="JSON-LD dump of a gold item or claim")
    p_export.add_argument("--jsonld", action="store_true")
    p_export.add_argument("--item", required=True, help="Path to a gold item or claim YAML")
    p_export.set_defaults(func=cmd_export)

    p_ret = sub.add_parser("retrieve", help="B0 BM25 over permitted fixture spans")
    p_ret.add_argument("--bm25", action="store_true")
    p_ret.add_argument("--query", required=True)
    p_ret.add_argument("--k", default=10, type=int)
    p_ret.set_defaults(func=cmd_retrieve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


def package_root() -> Path:
    return PACKAGE_ROOT


if __name__ == "__main__":
    sys.exit(main())
