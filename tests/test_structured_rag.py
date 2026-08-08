from examples.advanced.structured_rag import (
    MediaAsset, OcrRegion, TableRow, aggregate_with_citations, assets_for_query,
    citations_are_known, citations_for_regions, filter_rows, search_ocr_regions,
    summarize_rows, validate_table_rows,
)


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


def test_table_aggregation_has_row_level_citations_and_schema_validation():
    summary, citations = aggregate_with_citations(filter_rows(ROWS, team="Acme"), "tickets")
    assert summary["sum"] == 24
    assert [citation.locator for citation in citations] == ["row=r1", "row=r2"]
    assert validate_table_rows(ROWS, {"team", "tickets"}) == []
    assert "missing currency" in validate_table_rows(ROWS, {"currency"})[0]


def test_ocr_search_filters_low_confidence_and_preserves_visual_locator():
    regions = [
        OcrRegion("r1", "dashboard", 1, (80, 290, 760, 45), "Validate Northwind migration", 0.98, "dashboard.svg"),
        OcrRegion("r2", "dashboard", 1, (80, 200, 260, 55), "Northwind migration", 0.42, "dashboard.svg"),
    ]
    hits = search_ocr_regions("Validate Northwind migration", regions)
    citations = citations_for_regions(hits)
    assert [hit.region_id for hit in hits] == ["r1"]
    assert "page=1" in citations[0].locator
    assert citations_are_known(citations, row_ids=set(), region_ids={"r1"})
