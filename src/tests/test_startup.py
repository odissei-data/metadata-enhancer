import importlib
import sys

import pytest
from fastapi.testclient import TestClient

URLS = ["GITHUB_RAW_URL", "ELSST_FUSEKI_URL", "VARIABLE_FUSEKI_URL",
        "CBS_VOCAB_URL", "ELSST_VOCAB_URL"]


def load_main(monkeypatch, cbs_table):
    for name in URLS:
        monkeypatch.setenv(name, "http://example.invalid")
    monkeypatch.setattr("utils.load_tsv_from_github_raw", lambda url: {"a": "1"})
    monkeypatch.setattr("api.fuseki.create_table_terms", lambda url, query: cbs_table)
    monkeypatch.setattr("api.skosmos.create_table_concepts_skosmos",
                        lambda *args, **kwargs: {"a": "1"})
    sys.modules.pop("main", None)
    return importlib.import_module("main")


def test_start_fails_on_an_empty_table(monkeypatch):
    with pytest.raises(RuntimeError):
        load_main(monkeypatch, {})


def test_health(monkeypatch):
    main = load_main(monkeypatch, {"a": "1"})
    response = TestClient(main.app).get("/health").json()
    assert response == {"status": "ok", "version": main.get_version(),
                        "image": main.get_image()}
