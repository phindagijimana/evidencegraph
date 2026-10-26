"""License-aware ingest: mocked non-OA DOI is refused. No restricted full text."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from ingest.resolve import LicenseRefused, ResolutionError, resolve

RESTRICTED_DOI = "10.9999/restricted-mock"
OA_DOI = "10.9999/eg.fixture.surgical-hs"
SECRET = "SECRET RESTRICTED FULL TEXT DO NOT STORE"


def test_mocked_non_oa_doi_is_refused(tmp_path):
    with pytest.raises(LicenseRefused, match="not redistributable"):
        resolve(
            RESTRICTED_DOI,
            license_check=True,
            store_dir=tmp_path,
            metadata={
                "doi": RESTRICTED_DOI,
                "license": "all-rights-reserved",
                "is_oa": False,
                "full_text": SECRET,
            },
        )
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert SECRET not in path.read_text(encoding="utf-8", errors="ignore")


def test_manifest_non_oa_is_refused():
    with pytest.raises(LicenseRefused):
        resolve(RESTRICTED_DOI, license_check=True)


def test_oa_fixture_is_permitted_without_full_text():
    record = resolve(OA_DOI, license_check=True)
    assert record["oa_permitted"] is True
    assert record["full_text"] is None
    assert record["license"] == "CC-BY-4.0"


def test_unknown_doi_does_not_hit_network():
    with pytest.raises(ResolutionError, match="network is off"):
        resolve("10.1234/not-in-manifest", license_check=True)


def test_cli_ingest_non_oa_exits_nonzero():
    root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidencegraph.cli",
            "ingest",
            "--doi",
            RESTRICTED_DOI,
            "--license-check",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "not redistributable" in proc.stderr
