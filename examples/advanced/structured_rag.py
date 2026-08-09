"""Typed structured and multimodal evidence retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TableRow:
    row_id: str
    values: dict[str, Any]
    source: str


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    modality: str
    caption: str
    source: str


@dataclass(frozen=True)
class OcrRegion:
    """Text extracted from a bounded visual region, not an unlocated string."""

    region_id: str
    asset_id: str
    page: int
    bbox: tuple[int, int, int, int]
    text: str
    confidence: float
    source: str


@dataclass(frozen=True)
class EvidenceCitation:
    evidence_id: str
    modality: str
    source: str
    locator: str


def filter_rows(rows: list[TableRow], **filters: Any) -> list[TableRow]:
    return [row for row in rows if all(row.values.get(key) == value for key, value in filters.items())]


def summarize_rows(rows: list[TableRow], column: str) -> dict[str, Any]:
    values = [row.values[column] for row in rows if isinstance(row.values.get(column), (int, float))]
    if not values:
        return {"count": 0, "source_ids": [row.row_id for row in rows]}
    return {"count": len(values), "sum": sum(values), "average": sum(values) / len(values), "source_ids": [row.row_id for row in rows]}


def assets_for_query(assets: list[MediaAsset], modality: str | None = None) -> list[MediaAsset]:
    return [asset for asset in assets if modality is None or asset.modality == modality]


def validate_table_rows(rows: list[TableRow], required_columns: set[str]) -> list[str]:
    """Return deterministic schema errors before an aggregation is attempted."""

    errors: list[str] = []
    for row in rows:
        missing = sorted(required_columns - set(row.values))
        if missing:
            errors.append(f"{row.row_id}: missing {', '.join(missing)}")
    return errors


def aggregate_with_citations(rows: list[TableRow], column: str) -> tuple[dict[str, Any], tuple[EvidenceCitation, ...]]:
    """Aggregate typed values and return row-level citations for the calculation."""

    summary = summarize_rows(rows, column)
    citations = tuple(EvidenceCitation(row.row_id, "table", row.source, f"row={row.row_id}") for row in rows)
    return summary, citations


def search_ocr_regions(query: str, regions: list[OcrRegion], *, min_confidence: float = 0.8) -> list[OcrRegion]:
    """Find OCR evidence while excluding low-confidence text from answer context."""

    terms = {term.lower() for term in query.split() if len(term) > 2}
    return sorted(
        [region for region in regions if region.confidence >= min_confidence and terms & {term.lower() for term in region.text.split()}],
        key=lambda region: (-region.confidence, region.region_id),
    )


def citations_for_regions(regions: list[OcrRegion]) -> tuple[EvidenceCitation, ...]:
    return tuple(
        EvidenceCitation(region.region_id, "ocr", region.source, f"page={region.page};bbox={region.bbox}")
        for region in regions
    )


def citations_are_known(citations: tuple[EvidenceCitation, ...], *, row_ids: set[str], region_ids: set[str]) -> bool:
    """Verify each citation points to an evidence object emitted by this request."""

    return all(
        citation.evidence_id in (row_ids if citation.modality == "table" else region_ids if citation.modality == "ocr" else set())
        for citation in citations
    )
