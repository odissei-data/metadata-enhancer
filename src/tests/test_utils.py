import utils


def test_frequency_table_download_has_timeout(monkeypatch):
    calls = []

    class Response:
        text = "h\n"

        def raise_for_status(self):
            calls.append("checked")

    def fake_get(url, **kwargs):
        calls.append(kwargs)
        return Response()

    monkeypatch.setattr(utils.requests, "get", fake_get)
    utils.load_tsv_from_github_raw("http://example.invalid/table.tsv")
    assert calls == [{"timeout": 60}, "checked"]
