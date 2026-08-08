from pathlib import Path
from src.enterprise_rag.corpus import load_corpus, chunk_documents
from src.enterprise_rag.retrieval import retrieve, hybrid_retrieve
from src.enterprise_rag.generation import answer_with_citations
from src.enterprise_rag.advanced import graph_answer, route
from src.enterprise_rag.evaluation import evaluate_case

def corpus():
    return chunk_documents(load_corpus(Path('data/enterprise')))

def test_exact_identifier_retrieval_and_citation():
    hits = hybrid_retrieve('What does AX-774-B mean?', corpus(), top_k=3)
    assert any('error_codes.csv' in c.document_id for c, _ in hits)
    answer = answer_with_citations('What does AX-774-B mean?', hits)
    assert answer['supported'] and answer['citations']

def test_graph_multihop_answer():
    result = graph_answer('Project Atlas supplier regulation')
    assert 'Acme Systems' in result['answer']
    assert 'Regulation R-17' in result['answer']

def test_evaluation_maps_chunks_to_documents():
    hits = retrieve('What increased by 14%?', corpus(), top_k=5)
    scores = evaluate_case([c.id for c, _ in hits], ['finance/q2_2025.md'])
    assert scores['recall@5'] == 1.0

def test_router_selects_graph_for_multihop():
    assert route('Who supplies Project Atlas technology and what regulation applies?') == 'graph'
