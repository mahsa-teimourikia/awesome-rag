"""Bounded agentic RAG controller with deterministic tool boundaries."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

class Route(str, Enum): RETRIEVE="retrieve"; TOOL="tool"; ESCALATE="escalate"; ABSTAIN="abstain"
class Permission(str, Enum): READ="read"; PROPOSE="propose"; EXECUTE="execute"

@dataclass(frozen=True)
class ToolCall:
    name: str; arguments: dict[str,str]; requires_approval: bool=True; permission: Permission=Permission.EXECUTE
@dataclass(frozen=True)
class ToolReceipt:
    tool: str; request_id: str; status: str; evidence: str
@dataclass
class AgentState:
    question: str; route: Route|None=None; tool_call: ToolCall|None=None; approved: bool=False; turns:int=0; max_turns:int=4; trace:list[str]=field(default_factory=list); receipt:ToolReceipt|None=None

READ_TOOLS={"service_status", "search_runbooks"}; ACTION_WORDS=("delete","refund","send","change","restart","rollback")
def plan(question:str)->AgentState:
    s=AgentState(question); q=question.lower()
    if any(w in q for w in ACTION_WORDS):
        s.route=Route.TOOL; s.tool_call=ToolCall("account_action",{"request":question}); s.trace.append("planned-tool-call:approval-required")
    elif any(w in q for w in ("who","what","how","why","status","runbook")):
        s.route=Route.RETRIEVE; s.trace.append("planned-retrieval")
    else: s.route=Route.ESCALATE; s.trace.append("planned-escalation:ambiguous")
    s.turns=1; return s
def authorize_tool(state:AgentState, approved:bool)->AgentState:
    if state.route!=Route.TOOL or not state.tool_call: raise ValueError("state does not contain an actionable tool call")
    state.approved=approved; state.trace.append("tool-approved" if approved else "tool-denied"); return state
def execute(state:AgentState)->str:
    if state.turns>state.max_turns: state.route=Route.ABSTAIN; state.trace.append("stopped:turn-budget"); return "turn-budget-exhausted"
    if state.route==Route.RETRIEVE: state.trace.append("retrieval-executed"); return "retrieve-evidence"
    if state.route==Route.TOOL:
        if not state.approved: state.trace.append("tool-blocked:approval-missing"); return "human-approval-required"
        state.receipt=ToolReceipt(state.tool_call.name,"req-001","simulated-success","side-effect-receipt"); state.trace.append("tool-executed:receipt-required"); return "tool-executed-with-receipt"
    state.trace.append("escalated"); return "human-escalation"
def safe_tool_request(name:str, arguments:dict[str,str], *, user_permission:Permission)->ToolCall:
    if name in READ_TOOLS: return ToolCall(name,arguments,False,Permission.READ)
    if user_permission!=Permission.EXECUTE: raise PermissionError("tool requires execute permission")
    if not arguments or any(not value.strip() for value in arguments.values()): raise ValueError("tool arguments must be non-empty")
    return ToolCall(name,arguments,True,Permission.EXECUTE)
