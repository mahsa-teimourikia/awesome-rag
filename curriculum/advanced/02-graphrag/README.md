# Advanced 02 — GraphRAG: Relationship Retrieval and Provenance

**Level:** Advanced  
**Estimated time:** 2–3 hours  
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
   ↓ must_comply_with
Regulation R-17
```

The notebook demonstrates this with:

1. a manual fact graph containing provenance; and
2. a NetworkX directed graph with a shortest-path query.

![Graph retrieval path](assets/graph-path.svg)

Graph-based retrieval can help when the relationship structure itself is the evidence.

It is not a universal replacement for chunk, lexical, or vector retrieval.

---

## Learning objectives

After this lesson you should be able to:

- model relationships as typed graph edges;
- explain why edge provenance matters;
- retrieve a bounded multi-hop path;
- distinguish graph traversal from vector similarity;
- recognize entity-resolution failures;
- preserve edge direction when relation semantics require it;
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

# Notebook companion

The sections below connect the theory above to the executable notebook, identify deliberate simplifications, and highlight production gaps.

# 1. What the notebook actually implements

The folder contains only:

```text
README.md
02_graphrag.ipynb
```

There is no `lab.py`, and the notebook is not named `graph_rag.ipynb`.

The manual section defines:

```python
Fact(id, subject, predicate, object, source)
```

which is a good teaching representation because each relationship retains a source.

The NetworkX section then creates a `DiGraph` with relationship labels.

---

# 2. A graph fact needs provenance

A useful relationship record is more than:

```text
A → B
```

Prefer:

```text
fact_id
subject_id
relation_type
object_id
source_document_id
source_span
source_version
tenant
validity
extraction_version
```

![Fact anatomy](assets/fact-anatomy.svg)

Without provenance, a generated relationship claim cannot be reliably audited or retracted.

---

# 3. Entity resolution is a first-class problem

These may refer to the same entity:

```text
Acme Systems
Acme Systems Inc.
ACME
```

Or they may not.

Graph quality depends heavily on:

- canonical IDs;
- aliases;
- tenant scope;
- entity type;
- merge/split decisions.

A wrong merge creates false paths.

A missed merge breaks valid paths.

---

# 4. Direction matters

The notebook finds the shortest path using:

```python
G.to_undirected()
```

This is a useful way to demonstrate connectivity, but it is a **teaching simplification**.

For directional predicates such as:

```text
SUPPLIED_BY
OWNS
DEPENDS_ON
MUST_COMPLY_WITH
```

turning the graph undirected can permit paths that are connected but semantically invalid.

Production traversal should preserve direction rules or explicitly define which relations are safely traversable in reverse.

---

# 5. Notebook provenance limitation

The manual `Fact` objects contain `source`.

The later NetworkX triplets are:

```python
(subject, relation, target)
```

and the edge only stores:

```python
label=relation
```

So the NetworkX section **drops source provenance**.

That is an important limitation.

A better edge would include:

```python
G.add_edge(
    subject,
    target,
    relation=relation,
    source="vendor_list.csv",
    fact_id="f2",
)
```

Then path context can carry citations.

---

# 6. Local GraphRAG

Microsoft GraphRAG's current query engine distinguishes several search modes.

**Local Search** combines knowledge-graph data with related raw text chunks for entity-focused questions.

That general architecture is close to the kind of question in this notebook:

```text
How is Project Atlas connected to R-17?
```

Current Microsoft GraphRAG also provides **Global Search**, **DRIFT Search**, and a basic vector-RAG comparison path.

Those features are not implemented in this notebook.

---

# 7. Global and DRIFT search are different problems

### Global Search

Uses generated community reports in a map-reduce workflow for corpus-level questions such as:

```text
What are the major themes across the dataset?
```

### DRIFT Search

Combines community-level context with iterative local exploration.

Do not present "GraphRAG" as one traversal algorithm.

Different question shapes need different graph retrieval modes.

---

# 8. Hybrid graph + text retrieval

A practical architecture often looks like:

```text
query
  ↓
semantic/lexical seed retrieval
  ↓
resolve entities
  ↓
bounded graph expansion
  ↓
supporting source passages
  ↓
answer with fact + text provenance
```

![Hybrid graph retrieval](assets/hybrid-graph-text.svg)

The graph explains connections.

The source passages provide human-verifiable evidence.

---

# 9. Bound graph traversal

Unbounded graph expansion creates:

- irrelevant context;
- high-degree hub explosions;
- leakage across access boundaries;
- latency;
- difficult citations.

Control:

```text
max hops
max facts
allowed relation types
tenant filter
minimum confidence
time budget
```

---

# 10. Evaluation

Evaluate graph stages separately:

| Stage | Measure |
|---|---|
| Entity extraction | precision / recall |
| Entity resolution | merge/split error |
| Relation extraction | relation correctness |
| Path retrieval | path recall / precision |
| Provenance | source coverage |
| Answer | claim-to-fact support |
| Security | unauthorized node/edge exposure |
| Operations | traversal latency / fan-out |

A fluent multi-hop answer does not prove the graph path is valid.

---

# 11. Exercises

1. Add source metadata to every NetworkX edge.
2. Remove `to_undirected()` and define valid directional traversal.
3. Add aliases for `Acme Systems Inc`.
4. Add a same-named entity in another tenant.
5. Introduce a high-degree hub and enforce a fact budget.
6. Compare graph retrieval to dense text retrieval on relationship vs lookup questions.
7. Produce a cited path where each edge maps back to a source.

---

# 12. Checkpoint

1. When does a graph add value over passage retrieval?
2. Why is relation provenance important?
3. What can go wrong during entity resolution?
4. Why can undirected traversal be semantically unsafe?
5. What provenance does the current NetworkX section lose?
6. What is Microsoft GraphRAG Local Search?
7. How does Global Search differ?
8. Why should graph traversal be bounded?

---

## What comes next

### [Advanced 03 — Agentic RAG](../03-agentic-rag/README.md)

Move from a bounded graph query to runtime tool selection while retaining explicit permission boundaries.

---

## References

- Edge et al. — [From Local to Global: A Graph RAG Approach](https://arxiv.org/abs/2404.16130)
- Microsoft GraphRAG — [Query overview](https://microsoft.github.io/graphrag/query/overview/)
- Microsoft GraphRAG — [Local Search](https://microsoft.github.io/graphrag/query/local_search/)
- Microsoft GraphRAG — [Global Search](https://microsoft.github.io/graphrag/query/global_search/)
- Microsoft GraphRAG — [DRIFT Search](https://microsoft.github.io/graphrag/query/drift_search/)
- NetworkX — [Documentation](https://networkx.org/documentation/stable/)

---
- Microsoft GraphRAG — [Query engine overview](https://microsoft.github.io/graphrag/query/overview/)
- Microsoft GraphRAG — [Prompt tuning](https://microsoft.github.io/graphrag/prompt_tuning/overview/)

## Key takeaway

**GraphRAG is valuable when relationships are the retrieval problem. A graph path is only trustworthy when its entities, directions, and source-backed edges are trustworthy.**
