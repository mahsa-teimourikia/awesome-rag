# Advanced 02 — GraphRAG: Relationship Retrieval and Provenance

**Level:** Advanced  
**Estimated time:** 4–5 hours<br>
**Notebook:** [`02_graphrag.ipynb`](02_graphrag.ipynb)  
**Prerequisite:** Corrective RAG and retrieval evaluation

---

## Why this lesson exists

Text retrieval is strongest when a small number of passages directly contains the answer.

Some questions instead depend on explicit relationships:

```text
Project Atlas
   ↓ depends_on
VectorDB-X
   ↓ supplied_by
Acme Systems
   ↓ governed_by
Regulation R-17
```

The notebook keeps this compact Atlas path as its entry point, then develops it
into a provenance-preserving, directed, weighted, authorization-aware retrieval
system. You will construct, break, measure, and repair the graph rather than
treating a shortest-path call as a complete GraphRAG implementation.

![Graph retrieval path](assets/graph-path.svg)

Graph-based retrieval can help when the relationship structure itself is the evidence.

It is not a universal replacement for chunk, lexical, or vector retrieval.

---

## Learning objectives

After this lesson you should be able to:

- model relationships as typed graph edges;
- validate structured extraction before graph mutation;
- evaluate entity-resolution false merges and false splits;
- explain why edge provenance matters;
- retrieve a bounded, directional, weighted multi-hop path;
- distinguish graph traversal from vector similarity;
- resolve aliases without silently merging ambiguous entities;
- preserve edge direction when relation semantics require it;
- compare a graph retriever with a text baseline on one labelled task set;
- detect stale facts and cross-tenant structural leakage;
- explain local vs global GraphRAG at a conceptual level;
- combine graph facts with supporting source text; and
- evaluate path correctness before answer fluency.

---

# Deep dive — GraphRAG theory, indexing, and retrieval

## Why graph retrieval exists

Vector retrieval represents semantic similarity well, but many enterprise questions are fundamentally relational:

```text
Which applications depend on the vulnerable library?
Which supplier supports the service owned by this business unit?
How is regulation R connected to control C and system S?
What themes dominate the corpus as a whole?
```

A knowledge graph represents entities and typed relationships explicitly. GraphRAG combines that structure with retrieval and generation so the system can retrieve **connections**, not merely similar passages.

The important distinction is:

```text
vector RAG: query → similar evidence
GraphRAG: query → entities/communities/paths → supporting evidence
```

Graph retrieval is most valuable when topology carries information that would otherwise require assembling many disconnected chunks.

## Graph data model

A minimal property-graph representation contains:

```text
Node:
  id
  type
  canonical_name
  aliases
  attributes
  provenance

Edge:
  id
  source_id
  relation_type
  target_id
  attributes
  provenance
```

Enterprise graphs also commonly need:

- tenant/security scope;
- valid-from / valid-to dates;
- confidence or extraction status;
- source document and source span;
- extraction pipeline version;
- human verification status.

Treat graph facts as derived data. If the source document changes, the graph needs a lineage-aware update strategy.

## The indexing pipeline

A GraphRAG indexing pipeline is substantially more expensive than ordinary chunk embedding.

```text
documents
   ↓
chunk / text-unit creation
   ↓
entity extraction
   ↓
relationship extraction
   ↓
entity resolution / deduplication
   ↓
graph construction
   ↓
community detection / summaries (optional)
   ↓
embeddings + indexes
```

The quality of every downstream graph query depends on these extraction stages. A sophisticated graph search cannot repair a graph that merged two different people or missed the relationship that matters.

## Entity resolution

Entity resolution is often the hardest practical problem.

You need to decide whether:

```text
"ACME"
"Acme Systems"
"Acme Systems Inc."
```

are the same entity, and whether an identical name in another geography or tenant is different.

Useful signals include:

- normalized names;
- aliases;
- entity type;
- neighboring relationships;
- identifiers from authoritative systems;
- tenant/domain context;
- temporal context.

False merges create fabricated paths. False splits make true paths unreachable. Measure both.

## Relationship extraction and semantics

Edges should use a controlled relation vocabulary where possible:

```text
OWNS
DEPENDS_ON
SUPPLIED_BY
LOCATED_IN
IMPLEMENTS_CONTROL
GOVERNED_BY
```

Free-form relation text is flexible but difficult to validate and query. Typed relations allow schema constraints and direction rules.

Direction matters. `A DEPENDS_ON B` does not mean `B DEPENDS_ON A`. Some relationships are symmetric; many are not.

## Graph traversal strategies

Basic graph retrieval can use:

- one-hop neighborhood expansion;
- bounded k-hop traversal;
- shortest path;
- weighted path search;
- relation-constrained traversal;
- personalized PageRank or centrality-based expansion;
- subgraph retrieval seeded by vector search.

The best traversal depends on the question. Shortest path is not automatically the most meaningful path. A two-hop path through a generic hub may be less useful than a three-hop path through semantically precise relationships.

## Microsoft GraphRAG architecture

Microsoft GraphRAG popularized a broader graph-based RAG architecture that includes entity/relationship extraction, community detection, community reports, and multiple query modes.

Current GraphRAG distinguishes:

### Local Search

Entity-focused retrieval that combines graph data with related source text. Use it when the question is anchored around specific entities and their neighborhood.

### Global Search

Corpus-level search over community reports using a map-reduce style process. Use it for questions about dominant themes, patterns, or the dataset as a whole.

### DRIFT Search

A search mode that combines community-level context with iterative local exploration, broadening the starting context and generating follow-up investigation.

### Basic Search

A vector-RAG baseline useful for comparing whether graph structure actually adds value.

This taxonomy is important: "GraphRAG" is not synonymous with `shortest_path()`.

## Communities and hierarchical summarization

Large graphs can be partitioned into communities—groups of densely connected entities. Community summaries create a hierarchy:

```text
raw text
  ↓
entities + relations
  ↓
communities
  ↓
community reports
  ↓
corpus-level retrieval
```

This is useful for global questions because retrieving individual entities may never expose the overall pattern. The trade-off is indexing cost and summary drift: every generated community report is another derived artifact that must be versioned and evaluated.

## Hybrid graph + vector retrieval

Many production designs use vector retrieval to seed graph exploration:

```text
query
  ↓
retrieve relevant chunks/entities by embedding
  ↓
resolve seed entities
  ↓
expand allowed relationships
  ↓
retrieve source passages for graph facts
  ↓
rank combined evidence
```

This avoids requiring the query to exactly match graph entity names while still exploiting explicit relationships.

## Provenance architecture

A graph edge should never become an uncited fact simply because it is stored in a graph database.

Maintain:

```text
edge → extraction record → source span → source version
```

For generated answers, cite the underlying source evidence, not merely the graph node ID. The graph is an index over evidence, not necessarily the authoritative source itself.

## Security and multi-tenancy

Graph authorization is subtle because traversal can reveal sensitive structure even when node content is hidden. Controls may need to apply to:

- nodes;
- edges;
- properties;
- traversal rules;
- community summaries.

A path should be valid only if every traversed fact is visible in the requester's authorization scope. Precomputed community summaries are especially important to review because they can blend facts from multiple scopes.

## Cost model

GraphRAG shifts cost toward indexing:

```text
entity extraction
relationship extraction
entity resolution
community detection
community summarization
embeddings
```

Query cost can also be high for global/map-reduce modes. Evaluate whether graph-specific question classes justify that cost. For many FAQ or direct lookup workloads, hybrid text retrieval remains simpler and cheaper.

## Evaluation

Evaluate the graph before the answer:

- entity extraction precision/recall;
- entity-resolution false merge/split rate;
- relation extraction accuracy;
- path recall;
- path precision;
- source-provenance coverage;
- graph freshness;
- unauthorized path exposure;
- answer claim support.

Create separate benchmark groups for entity lookup, relationship questions, multi-hop questions, and global/corpus-level questions. GraphRAG should outperform the text baseline specifically where graph structure is expected to matter.

## When not to use GraphRAG

Avoid GraphRAG when:

- questions are mostly direct passage lookups;
- relationships are sparse or unreliable;
- entity resolution cannot be made trustworthy;
- the corpus changes too rapidly for the indexing cost;
- authorization boundaries make graph-derived summaries unsafe;
- a simpler hybrid retriever already meets quality targets.

GraphRAG is a specialized retrieval architecture, not the next mandatory stage after vector RAG.

---

# Guided lab — from extracted facts to defensible paths

The notebook is a self-contained investigation of the fictional **Atlas Commerce**
estate. Its central question remains:

```text
How is Project Atlas connected to Regulation R-17?
```

The answer is useful only when every relationship in the path is directionally
valid, current, visible to the requester, and traceable to an exact source span.

![Fact anatomy](assets/fact-anatomy.svg)

## 1. Establish typed graph contracts

The lab separates source records, canonical entities, extracted relations, query
entities, traversed edges, evidence records, and grounded answers. A relation is
not accepted merely because a model produced plausible JSON. It must pass
deterministic validation:

```text
structured extraction
        ↓
relation vocabulary + endpoint-type rules
        ↓
tenant + source-span + source-version + source-authority checks
        ↓
accepted edge or quarantine
```

The default path uses a frozen extraction fixture so the notebook runs without
credentials. An optional cell demonstrates current schema-constrained extraction
with LangChain and `ChatOpenAI.with_structured_output(...)`. The same validation
boundary applies to both.

## 2. Build a corpus large enough to fail meaningfully

The scenario contains 26 source records, 34 canonical entities, and 39
source-backed relations across projects, services, databases, suppliers,
controls, regulations, owners, regions, and a generic platform hub. It includes:

- aliases such as `Acme Systems Inc.`;
- same-name entities in different tenants;
- parallel relations between the same node pair;
- current and historical source versions;
- a high-degree hub that creates a misleading short path; and
- malformed extraction candidates that must be quarantined.

This is still synthetic and inspectable, but it is no longer a three-edge happy
path.

## 3. Treat entity resolution as measured graph construction

Resolution uses normalized aliases together with entity type and tenant scope.
Ambiguous names produce an explicit clarification state instead of an arbitrary
node choice. The lab injects both major failure modes:

| Failure | Graph consequence |
|---|---|
| False merge | unrelated nodes become connected and fabricate a path |
| False split | a legitimate path becomes unreachable |

The exercise reports whether each deliberately injected false-merge and
false-split failure was detected; these single examples are outcomes, not rates.
In a real system, authoritative IDs, review queues, and domain-specific match
features should supplement string normalization.

## 4. Preserve direction and provenance in a `MultiDiGraph`

The graph uses NetworkX `MultiDiGraph`, not a simple undirected graph. This
retains parallel edges and stores source document, source span, source version,
tenant, confidence, status, validity, and extraction version on every edge.

The original manual Atlas trace remains in the lab, now as structured evidence.
The notebook also deliberately calls `to_undirected()` to show the failure:

```text
Analyst A ──OWNS── Shared Service ──OWNS── Analyst C
```

Connectivity does not establish that Analyst A owns Analyst C. Reverse traversal
is allowed only when a relation has an explicitly modelled reverse meaning.

## 5. Retrieve a bounded, weighted, relation-aware path

The educational retriever exposes the mechanics frameworks often hide:

```text
query
  ↓
resolve source and target entities
  ↓
apply tenant, status, validity, and relation eligibility
  ↓
weighted directional traversal
  ↓
max-hop and returned-path-fact budgets
  + a separate candidate-edge evaluation budget
  ↓
path trace + terminal reason
```

Shortest does not always mean best. The lab adds a two-hop route through a
generic enterprise-platform hub and a three-hop supplier/compliance route.
Weights and allowed-relation policy select the semantically meaningful path. A
separate hub experiment shows how bounded expansion controls fan-out.

## 6. Seed the graph from text, then hydrate source evidence

A graph query should not require users to type exact canonical node names. The
notebook uses a small BM25 baseline to retrieve source records, extracts candidate
entity seeds, resolves them, and then traverses the graph.

![Hybrid graph retrieval](assets/hybrid-graph-text.svg)

Retrieved graph edges are hydrated back into request-local evidence records:

```text
path edge
  → source record
  → exact source span
  → evidence ID
  → cited answer
```

A deterministic renderer is used by default. Optional live generation receives
only validated evidence, and a citation validator rejects unknown evidence IDs.

## 7. Reconcile versions and isolate tenants

Graph facts are derived data. The notebook replaces a source version, removes
facts derived from the old version, passes every replacement through the same
validation boundary used at initial ingestion, and rebuilds the graph. It also
injects a relation with a valid `Project DEPENDS_ON Service` shape but cross-tenant
endpoints, demonstrating that tenant validation and traversal scope both prevent
exposure.

Do not confuse a missing visible path with proof that no relationship exists:

- the fact may never have been extracted;
- entity resolution may have split the entity;
- the source may be stale or unavailable;
- the path may be outside the principal's scope; or
- the traversal budget may be too small.

## 8. Evaluate the graph before answer style

The lab uses one 22-case dataset for a graph retriever and a text baseline. Cases
cover direct, two-hop, and three-hop paths; direction; aliases; ambiguity; hubs;
no-path outcomes; historical versions; ownership semantics; and cross-tenant
requests.

It reports:

| Layer | Measures |
|---|---|
| Extraction | entity and relation precision / recall |
| Resolution | lookup accuracy plus injected false-merge/false-split outcomes |
| Retrieval | positive-case exact-path accuracy, edge precision, edge recall |
| Provenance | source-backed edge coverage over non-empty, generation-eligible paths |
| Security | unauthorized node and edge count |
| Baseline comparison | graph vs BM25 support completeness by question type |

Unauthorized exposure is a hard failure, not a relevance trade-off. Answer
fluency is evaluated only after the path and its provenance pass.
Graph relation recall and text source-document recall remain visible diagnostic
proxies, but they are not treated as numerically identical metrics. The primary
comparison asks the same binary question of both systems: were all required
source-backed facts available?

## 9. Map the lab to current GraphRAG systems

The implementation is deliberately transparent and local. It teaches the
primitives behind entity-focused graph retrieval, not the full Microsoft GraphRAG
stack.

| Query mode | Purpose | Implemented here? |
|---|---|---|
| Local Search | entity neighborhood plus supporting text | educational analogue |
| Global Search | map-reduce over community reports | conceptual only |
| DRIFT Search | community context plus iterative local exploration | conceptual only |
| Basic Search | vector/text comparison path | BM25 teaching baseline |

Community detection, community report generation, distributed graph storage,
production graph authorization, learned reranking, and incremental extraction
orchestration remain production upgrades rather than simulated notebook claims.

## Production decision points

Before adopting GraphRAG, decide and test:

- which question classes genuinely require topology;
- whether relation extraction and entity resolution meet release thresholds;
- how source changes retract or supersede graph facts;
- whether access control applies to nodes, edges, properties, and summaries;
- how traversal fan-out, latency, and cost are bounded;
- whether a property graph, RDF store, or simpler relational model fits the data;
- how graph and text evidence are ranked together; and
- how an operator can replay a path from answer to source version.

NetworkX is suitable for this transparent lab. Production candidates include
Neo4j and other graph databases, cloud graph services, RDF stores, or a
domain-specific relational representation. Benchmark the deployed backend's
traversal, authorization, update, and operational behavior rather than assuming
the teaching implementation transfers unchanged.

## Exercises

1. Add a relation type with an explicit reverse meaning and update the schema.
2. Tune hub penalties without damaging recall on legitimate platform questions.
3. Add a second ambiguous `Atlas` entity and design a clarification response.
4. Replace BM25 seeding with embeddings while keeping the same evaluation set.
5. Add confidence thresholds and measure precision/recall changes.
6. Implement source deletion and verify that every derived edge is retracted.
7. Add a community summary, then test it for stale and cross-tenant facts.
8. Extend the path evaluator with ordered-node and source-span correctness.

## Checkpoint

1. Why is schema-constrained extraction still untrusted input?
2. How do false merges and false splits affect reachability differently?
3. Why is an undirected shortest path not a semantic proof?
4. When can a longer weighted path be preferable to a shorter path?
5. What must be retained to retract a fact after a source update?
6. Why can a graph leak information before any answer is generated?
7. What does Local Search solve that Global Search does not?
8. Which metrics must pass before an answer-quality evaluation is meaningful?

---

## What comes next

### [Advanced 03 — Agentic RAG](../03-agentic-rag/README.md)

Move from a bounded graph query to runtime tool selection while retaining explicit permission boundaries.

---

## References

- Edge et al. — [From Local to Global: A Graph RAG Approach](https://arxiv.org/abs/2404.16130)
- Microsoft GraphRAG — [Indexing architecture](https://microsoft.github.io/graphrag/index/overview/)
- Microsoft GraphRAG — [Query overview](https://microsoft.github.io/graphrag/query/overview/)
- Microsoft GraphRAG — [Local Search](https://microsoft.github.io/graphrag/query/local_search/)
- Microsoft GraphRAG — [Global Search](https://microsoft.github.io/graphrag/query/global_search/)
- Microsoft GraphRAG — [DRIFT Search](https://microsoft.github.io/graphrag/query/drift_search/)
- NetworkX — [`MultiDiGraph`](https://networkx.org/documentation/stable/reference/classes/multidigraph.html)
- NetworkX — [Shortest paths](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html)
- LangChain — [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- LangChain — [`LLMGraphTransformer` API reference](https://reference.langchain.com/python/langchain-neo4j/graph_transformers/llm/LLMGraphTransformer)
- Neo4j — [Operations and access control](https://neo4j.com/docs/operations-manual/current/authentication-authorization/)
- Microsoft GraphRAG — [Prompt tuning](https://microsoft.github.io/graphrag/prompt_tuning/overview/)

## Key takeaway

**GraphRAG is valuable when relationships are the retrieval problem. A graph path is only trustworthy when its entities, directions, and source-backed edges are trustworthy.**
