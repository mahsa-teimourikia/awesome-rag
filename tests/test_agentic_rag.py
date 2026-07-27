from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))
from examples.advanced.agentic_rag import Route, authorize_tool, execute, plan


def test_knowledge_question_routes_to_retrieval():
    state = plan("How does the API work?")
    assert state.route == Route.RETRIEVE
    assert execute(state) == "retrieve-evidence"


def test_action_requires_approval_before_execution():
    state = plan("Refund my invoice")
    assert state.route == Route.TOOL
    assert execute(state) == "human-approval-required"
    authorize_tool(state, True)
    assert execute(state) == "tool-executed-with-receipt"


def test_denied_action_is_blocked_and_traced():
    state = plan("Delete my account")
    authorize_tool(state, False)
    assert execute(state) == "human-approval-required"
    assert "tool-denied" in state.trace
