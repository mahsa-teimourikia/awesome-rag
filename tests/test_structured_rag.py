from examples.advanced.structured_rag import MediaAsset, TableRow, assets_for_query, filter_rows, summarize_rows


ROWS = [TableRow("r1", {"team": "Acme", "tickets": 10}, "support.csv#1"), TableRow("r2", {"team": "Acme", "tickets": 14}, "support.csv#2"), TableRow("r3", {"team": "Globex", "tickets": 8}, "support.csv#3")]


def test_rows_filter_and_aggregate_with_provenance():
    result = summarize_rows(filter_rows(ROWS, team="Acme"), "tickets")
    assert result["sum"] == 24
    assert result["source_ids"] == ["r1", "r2"]


def test_empty_numeric_summary_is_explicit():
    assert summarize_rows(filter_rows(ROWS, team="None"), "tickets")["count"] == 0


def test_modality_filter():
    assets = [MediaAsset("i", "image", "diagram", "a.png"), MediaAsset("o", "ocr", "table", "b.pdf")]
    assert [asset.asset_id for asset in assets_for_query(assets, "ocr")] == ["o"]
