"""Shared, inspectable contracts and deterministic metrics for Intermediate 04.

The notebooks intentionally keep these primitives small.  Evaluation platforms can
store and visualize the results, but they do not replace the dataset contract or the
metric definitions used by a release decision.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


DATA_DIR = Path(__file__).resolve().parent / "data"


class CorpusChunk(BaseModel):
    document_id: str
    chunk_id: str
    source: str
    section: str
    tenant_id: str
    classification: Literal["public", "internal", "restricted"]
    status: Literal["current", "expired", "superseded"] = "current"
    text: str


class EvalCase(BaseModel):
    case_id: str
    query: str
    answerable: bool
    expected_document_ids: list[str] = Field(default_factory=list)
    required_evidence_ids: list[str] = Field(default_factory=list)
    relevant_evidence_ids: list[str] = Field(default_factory=list)
    reference_answer: str | None = None
    slice: str
    risk: Literal["low", "medium", "high", "critical"]
    corpus_version: str
    index_version: str
    review_status: Literal["synthetic_unreviewed", "reviewed", "approved"]
    reviewer_rationale: str = ""

    @model_validator(mode="after")
    def validate_answerability(self) -> "EvalCase":
        if self.answerable and not self.required_evidence_ids:
            raise ValueError("answerable cases require at least one required evidence ID")
        if self.answerable and not self.expected_document_ids:
            raise ValueError("answerable cases require at least one expected document ID")
        if self.answerable and not self.reference_answer:
            raise ValueError("answerable cases require a reference answer")
        if not self.answerable and self.required_evidence_ids:
            raise ValueError("unanswerable cases cannot have required evidence IDs")
        if not self.answerable and self.reference_answer:
            raise ValueError("unanswerable cases must not provide a reference answer")
        missing = set(self.required_evidence_ids) - set(self.relevant_evidence_ids)
        if missing:
            raise ValueError(f"required evidence must also be relevant: {sorted(missing)}")
        return self


class JudgeResult(BaseModel):
    label: Literal["pass", "fail"]
    score: float = Field(ge=0.0, le=1.0)
    reason: str
    failure_type: str | None = None


class TraceEvent(BaseModel):
    trace_id: str
    query_id: str
    stage: Literal[
        "retrieval", "reranking", "context", "generation", "validation", "rendering"
    ]
    mode: Literal["metadata_only", "sampled_redacted", "full_debug"]
    timestamp_ms: int
    duration_ms: float = Field(ge=0)
    model: str | None = None
    prompt_version: str | None = None
    index_version: str
    policy_version: str
    chunk_ids: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    decision: str | None = None
    candidate_count: int | None = None
    token_count: int | None = None
    estimated_cost_usd: float | None = None
    status: Literal["ok", "warning", "error"] = "ok"
    error_class: str | None = None
    content_sample: str | None = None

    @model_validator(mode="after")
    def enforce_privacy_mode(self) -> "TraceEvent":
        if self.mode == "metadata_only" and self.content_sample is not None:
            raise ValueError("metadata-only traces must not contain content")
        return self


def load_json(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def load_corpus() -> list[CorpusChunk]:
    return [CorpusChunk.model_validate(row) for row in load_json("evaluation_corpus.json")]


def load_cases(name: str = "evaluation_golden.json") -> list[EvalCase]:
    return [EvalCase.model_validate(row) for row in load_json(name)]


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top = retrieved[:k]
    return sum(item in relevant for item in top) / k if k else 0.0


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    return sum(item in relevant for item in retrieved[:k]) / len(relevant) if relevant else 1.0


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    return next((1.0 / rank for rank, item in enumerate(retrieved, 1) if item in relevant), 0.0)


def ndcg_at_k(retrieved: list[str], relevance: dict[str, int], k: int) -> float:
    def dcg(grades: list[int]) -> float:
        return sum((2**grade - 1) / math.log2(rank + 1) for rank, grade in enumerate(grades, 1))

    actual = dcg([relevance.get(item, 0) for item in retrieved[:k]])
    ideal = dcg(sorted(relevance.values(), reverse=True)[:k])
    return actual / ideal if ideal else 1.0


def evidence_completeness(retrieved: list[str], required: set[str]) -> float:
    return sum(item in retrieved for item in required) / len(required) if required else 1.0


def confusion_counts(actual: list[str], predicted: list[str]) -> dict[str, int]:
    return dict(Counter(f"actual={a}|predicted={p}" for a, p in zip(actual, predicted, strict=True)))


def accuracy(actual: list[str], predicted: list[str]) -> float:
    return sum(a == p for a, p in zip(actual, predicted, strict=True)) / len(actual)


def cohen_kappa(actual: list[str], predicted: list[str]) -> float:
    labels = sorted(set(actual) | set(predicted))
    observed = accuracy(actual, predicted)
    expected = sum(
        (actual.count(label) / len(actual)) * (predicted.count(label) / len(predicted))
        for label in labels
    )
    return (observed - expected) / (1 - expected) if expected < 1 else 1.0


def validate_dataset(cases: list[EvalCase], corpus: list[CorpusChunk]) -> list[str]:
    errors: list[str] = []
    corpus_ids = {chunk.chunk_id for chunk in corpus}
    document_ids = {chunk.document_id for chunk in corpus}
    case_ids = [case.case_id for case in cases]
    duplicates = [key for key, count in Counter(case_ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate case IDs: {duplicates}")
    for case in cases:
        unknown = set(case.relevant_evidence_ids) - corpus_ids
        if unknown:
            errors.append(f"{case.case_id}: unknown evidence IDs {sorted(unknown)}")
        unknown_documents = set(case.expected_document_ids) - document_ids
        if unknown_documents:
            errors.append(f"{case.case_id}: unknown document IDs {sorted(unknown_documents)}")
        derived_documents = {
            chunk.document_id for chunk in corpus if chunk.chunk_id in case.relevant_evidence_ids
        }
        if set(case.expected_document_ids) != derived_documents:
            errors.append(
                f"{case.case_id}: document IDs do not match relevant chunk provenance"
            )
    return errors
