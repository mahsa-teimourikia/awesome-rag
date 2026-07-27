from datetime import datetime, timedelta, timezone

from examples.advanced.operations import Budget, Trace, freshness_status, health_status, within_budget


def test_trace_records_events_and_budget():
    trace = Trace("q", "retrieve")
    trace.record("retrieval-complete")
    trace.latency_ms, trace.cost_usd = 100, 0.01
    assert trace.events == ["retrieval-complete"]
    assert within_budget(trace, Budget(200, 0.02))
    assert not within_budget(trace, Budget(50, 0.02))


def test_freshness_status():
    now = datetime.now(timezone.utc)
    assert freshness_status(now - timedelta(hours=1), now, 24) == "fresh"
    assert freshness_status(now - timedelta(hours=25), now, 24) == "stale"


def test_health_status_separates_readiness_and_corpus():
    assert health_status(index_ready=True, evaluator_ready=True, corpus_fresh=False) == {"ready": "ok", "corpus": "stale"}
    assert health_status(index_ready=False, evaluator_ready=True, corpus_fresh=True)["ready"] == "not-ready"
