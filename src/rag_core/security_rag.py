"""Deterministic tenant-isolation and indirect-prompt-injection controls for RAG."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


TOKEN = re.compile(r"[a-z0-9]+")
INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "reveal system prompt",
    "send all records",
    "bypass authorization",
)


@dataclass(frozen=True)
class Principal:
    user_id: str
    tenant_id: str
    roles: frozenset[str]


@dataclass(frozen=True)
class SecureEvidence:
    evidence_id: str
    tenant_id: str
    classification: str
    text: str
    source: str


@dataclass(frozen=True)
class SecurityDecision:
    allowed: bool
    reason: str
    evidence_ids: tuple[str, ...] = ()


@dataclass
class SecurityTrace:
    events: list[str] = field(default_factory=list)


def tokenize(text: str) -> set[str]:
    return set(TOKEN.findall(text.lower()))


def is_authorized(principal: Principal, evidence: SecureEvidence) -> bool:
    """Apply tenant and classification checks before content is ranked or exposed."""

    return evidence.tenant_id == principal.tenant_id and evidence.classification in principal.roles


def inspect_untrusted_content(text: str) -> SecurityDecision:
    """Detect a small deterministic set of injection signals for the teaching lab.

    This is not a replacement for layered content safety controls; it makes the
    trust-boundary decision testable without a model call.
    """

    lowered = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lowered:
            return SecurityDecision(False, f"untrusted-instruction:{pattern}")
    return SecurityDecision(True, "no-known-injection-signal")


def secure_retrieve(principal: Principal, query: str, corpus: list[SecureEvidence], *, top_k: int = 3, trace: SecurityTrace | None = None) -> list[SecureEvidence]:
    """Authorize, inspect, then rank evidence. Unsafe or foreign evidence never reaches context."""

    trace = trace or SecurityTrace()
    authorized = [item for item in corpus if is_authorized(principal, item)]
    trace.events.append(f"authorization:allowed={len(authorized)};denied={len(corpus) - len(authorized)}")
    safe: list[SecureEvidence] = []
    for item in authorized:
        decision = inspect_untrusted_content(item.text)
        if decision.allowed:
            safe.append(item)
        else:
            trace.events.append(f"quarantined:{item.evidence_id}:{decision.reason}")
    terms = tokenize(query)
    ranked = sorted(safe, key=lambda item: (-len(terms & tokenize(item.text)), item.evidence_id))
    selected = [item for item in ranked if terms & tokenize(item.text)][:top_k]
    trace.events.append(f"retrieval:selected={','.join(item.evidence_id for item in selected) or 'none'}")
    return selected


def build_untrusted_context(evidence: list[SecureEvidence]) -> str:
    """Label retrieved text as data so prompt construction preserves the boundary."""

    return "\n\n".join(
        f"<untrusted_document id={item.evidence_id} source={item.source}>\n{item.text}\n</untrusted_document>"
        for item in evidence
    )


def decide_response(evidence: list[SecureEvidence], trace: SecurityTrace) -> SecurityDecision:
    if not evidence:
        trace.events.append("response:abstain:no-authorized-safe-evidence")
        return SecurityDecision(False, "no-authorized-safe-evidence")
    trace.events.append("response:answer-from-authorized-evidence")
    return SecurityDecision(True, "authorized-safe-evidence", tuple(item.evidence_id for item in evidence))
