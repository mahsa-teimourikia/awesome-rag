"""Stateful agentic RAG routing with explicit tool approval."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Route(str, Enum):
    RETRIEVE = "retrieve"
    TOOL = "tool"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, str]
    requires_approval: bool = True


@dataclass
class AgentState:
    question: str
    route: Route | None = None
    tool_call: ToolCall | None = None
    approved: bool = False
    trace: list[str] = field(default_factory=list)


def plan(question: str) -> AgentState:
    state = AgentState(question)
    lowered = question.lower()
    if any(word in lowered for word in ("delete", "refund", "send", "change")):
        state.route = Route.TOOL
        state.tool_call = ToolCall("account_action", {"request": question})
        state.trace.append("planned-tool-call:approval-required")
    elif any(word in lowered for word in ("who", "what", "how", "why")):
        state.route = Route.RETRIEVE
        state.trace.append("planned-retrieval")
    else:
        state.route = Route.ESCALATE
        state.trace.append("planned-escalation:ambiguous")
    return state


def authorize_tool(state: AgentState, approved: bool) -> AgentState:
    if state.route != Route.TOOL or state.tool_call is None:
        raise ValueError("state does not contain an actionable tool call")
    state.approved = approved
    state.trace.append("tool-approved" if approved else "tool-denied")
    return state


def execute(state: AgentState) -> str:
    if state.route == Route.RETRIEVE:
        state.trace.append("retrieval-executed")
        return "retrieve-evidence"
    if state.route == Route.TOOL:
        if not state.approved:
            state.trace.append("tool-blocked:approval-missing")
            return "human-approval-required"
        state.trace.append("tool-executed:receipt-required")
        return "tool-executed-with-receipt"
    state.trace.append("escalated")
    return "human-escalation"
