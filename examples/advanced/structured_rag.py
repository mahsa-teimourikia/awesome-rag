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


def filter_rows(rows: list[TableRow], **filters: Any) -> list[TableRow]:
    return [row for row in rows if all(row.values.get(key) == value for key, value in filters.items())]


def summarize_rows(rows: list[TableRow], column: str) -> dict[str, Any]:
    values = [row.values[column] for row in rows if isinstance(row.values.get(column), (int, float))]
    if not values:
        return {"count": 0, "source_ids": [row.row_id for row in rows]}
    return {"count": len(values), "sum": sum(values), "average": sum(values) / len(values), "source_ids": [row.row_id for row in rows]}


def assets_for_query(assets: list[MediaAsset], modality: str | None = None) -> list[MediaAsset]:
    return [asset for asset in assets if modality is None or asset.modality == modality]
