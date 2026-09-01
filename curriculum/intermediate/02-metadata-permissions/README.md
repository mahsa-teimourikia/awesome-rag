# Intermediate 02 — Metadata and Permissions: Secure the Retrieval Boundary

**Level:** Intermediate  
**Estimated time:** 3–4 hours
**Notebook:** [`02_metadata_permissions.ipynb`](02_metadata_permissions.ipynb)  
**Prerequisite:** [Retrieval Strategies](../01-retrieval-strategies/README.md)

---

## Why this lesson exists

Retrieval quality is irrelevant if the retriever is allowed to search data the caller must not see.

The notebook demonstrates the core principle correctly:

> **authorization belongs in the search constraint, before retrieved text reaches the model.**

Or, as the course's central rule states:

> **Authorization defines the candidate evidence space before generation.**

It builds a multi-tenant Chroma collection and compares naive search with a trusted, policy-derived candidate-eligibility filter. The exercise remains intentionally local and inspectable: identity providers, policy engines, and enterprise IAM are represented by clear Python interfaces rather than mocked infrastructure.

![Authorization boundary](assets/authorization-boundary.svg)

---

## Learning objectives

After this lesson you should be able to:

- distinguish relevance metadata from security metadata;
- enforce tenant isolation before generation;
- build metadata filters from authenticated identity claims;
- explain why prompt instructions are not access controls;
- identify leakage paths beyond the final answer;
- reason about RBAC and attribute-based filters;
- preserve authorization metadata through chunking;
- reject or quarantine documents with invalid security metadata;
- combine tenant, classification, project, and lifecycle eligibility;
- design negative tests for cross-tenant retrieval;
- understand freshness/version metadata as a retrieval constraint; and
- design tenant-safe cache keys and minimal audit records.

---

## 1. Metadata categories

### Relevance metadata

Examples:

```text
product
document_type
language
date
region
```

These help retrieval narrow the search space.

### Security metadata

Examples:

```text
tenant_id
classification
required_role
project_id
```

These determine whether content may become a candidate.

### Lifecycle metadata

Examples:

```text
version
valid_from
valid_to
is_deleted
superseded_by
```

These determine whether evidence is current and eligible.

![Metadata categories](assets/metadata-categories.svg)

---

## 2. What the notebook implements

The original four-document demonstration is expanded into a synthetic corpus of roughly thirty chunks across Acme, Globex, and NovaTech. It deliberately contains public, internal, and restricted material; overlapping text; project boundaries; active, expired, superseded, future, and deleted records; and invalid records that must be quarantined.

A representative chunk looks like:

```python
metadata={
    "document_id": "acme-checkout-runbook",
    "chunk_id": "acme-checkout-runbook#approval",
    "source": "acme_runbook.md",
    "tenant_id": "acme",
    "classification": "internal",
    "project_id": "checkout",
    "valid_from": "2026-01-01",
    "valid_to": None,
    "is_deleted": False,
}
```

The lab first makes the failure visible:

```python
unsafe_results = search_without_authorization(vectorstore, question)
```

It then makes every trusted decision inspectable:

```python
principal
    ↓
build_authorization_filter(principal, now)
    ↓
authorized_search(vectorstore, query, principal)
    ↓
validate_results(results, principal)
```

The query never supplies tenant, role, clearance, or project membership. The policy function derives candidate eligibility from the authenticated principal.

This is the correct teaching sequence because it makes the leak visible before showing the control.

---

## 3. Current Chroma integration

Install the repository environment, or install the focused dependencies directly:

```bash
pip install langchain-chroma langchain-core chromadb
```

The executable notebook uses the dedicated integration:

```python
from langchain_chroma import Chroma
```

For repeatable offline execution, the lesson supplies a small deterministic token-hashing embedding implementation. It is a teaching substitute for a production embedding model, not a quality benchmark. The authorization policy is independent of the embedding provider.

---

## 4. Authorization must precede retrieval

Safe order:

```text
authenticated principal
        ↓
trusted identity attributes
        ↓
authorization policy
        ↓
retrieval eligibility filter
        ↓
authorized candidate retrieval
        ↓
ranking
        ↓
context
        ↓
generation
```

Unsafe order:

```text
retrieve everything
        ↓
send to model
        ↓
ask model to hide restricted content
```

Once restricted content enters a prompt, trace, cache, or intermediate model call, the boundary has already failed.

Authorization constraints must be enforced by the retrieval or storage layer as part of candidate eligibility, before unauthorized content enters model-visible or application-visible intermediate state. This is an architectural requirement, not a claim that every vector backend executes filters identically. Verify the deployed backend's filtering semantics, approximate-nearest-neighbor behavior, recall, and performance under realistic filters.

---

## 5. Leakage paths

Unauthorized content can leak through:

- retrieved text;
- generated paraphrases;
- citation IDs;
- retrieval traces;
- logs;
- caches;
- debugging UIs;
- evaluation exports;
- timing and result-count behavior.

A good security test checks the entire evidence path, not only the final response string.

---

## 6. Build filters from trusted claims

The notebook models an authenticated principal separately from the query:

```python
principal = {
    "user_id": "user-123",
    "tenant_id": "acme",
    "roles": ["support"],
    "clearance": "internal",
    "projects": ["checkout"],
}
```

In production, these values must originate from verified authentication, identity, and authorization systems. The user query can express intent, but it cannot mutate the principal. Therefore `"Search Globex documents"` does not change `principal["tenant_id"]`.

The notebook centralizes policy construction:

```python
def build_authorization_filter(principal, now):
    # validate the principal, apply RBAC and ABAC, and return a trusted filter
    ...
```

Application call sites do not assemble ad hoc security filters. Centralization reduces drift between endpoints and makes the policy version testable and auditable.

---

## 7. RBAC, ABAC, and relationship-aware access

| Model | Good for |
|---|---|
| RBAC | stable roles such as support/admin |
| ABAC | tenant, classification, region, purpose, time |
| ReBAC | ownership, project membership, sharing relationships |

Enterprise RAG often uses multiple dimensions:

```text
tenant == caller.tenant
AND classification <= caller.clearance
AND project_id IN caller.projects
AND valid_now == true
```

### RBAC in this lesson

RBAC controls a capability ceiling. For example, the fictional `admin` role may consider restricted evidence, while `support` is capped at internal evidence. A role check alone does not establish tenant or project scope.

### ABAC in this lesson

ABAC combines subject, resource, and environment attributes:

```text
tenant_id == principal.tenant_id
AND classification <= principal.clearance
AND classification <= role ceiling
AND project_id IN {"shared", *principal.projects}
AND document is currently valid
```

Classification order is defined once for this fictional organization:

```python
CLASSIFICATION_RANK = {
    "public": 0,
    "internal": 1,
    "restricted": 2,
}
```

This ordering is an example policy, not a universal standard. The lab derives Chroma's explicit `$in` values from it instead of scattering classification lists across retrieval calls.

### ReBAC beyond this lab

Project membership is represented as an attribute in the notebook. A mature relationship-aware system may instead evaluate resource ownership, group membership, sharing relationships, and delegated access through an external authorization service.

---

## 8. Freshness is also a filter

A user may be authorized to read a document that is no longer valid.

Useful fields include:

```text
valid_from
valid_to
superseded_by
is_deleted
version
```

A current-policy query should not retrieve superseded content unless the application explicitly asks for historical evidence.

The notebook derives a simple lifecycle state in Python before indexing and then includes `lifecycle_status == "current"` in candidate eligibility. This keeps the temporal lesson readable when a backend's date-comparison syntax is cumbersome:

```text
security eligibility
        +
lifecycle eligibility
        =
candidate eligibility
```

This preprocessing approach requires lifecycle status to be recomputed when time or source versions change. Production systems may enforce time validity at query time, periodically re-index it, or use a storage layer with native temporal predicates. Remember: **authorized does not mean currently valid**.

---

## 9. Cache isolation

Dangerous:

```python
cache_key = hash(query)
```

Safer:

```python
cache_key = build_cache_key(
    query=query,
    principal=principal,
    policy_version=POLICY_VERSION,
    index_version=INDEX_VERSION,
)
```

If authorization-relevant dimensions are absent from a cache key, retrieval can be correct while the cache still leaks another tenant's result.

A cached result also becomes suspect when roles, clearance, project membership, policy version, index version, or document validity changes. The lab demonstrates the key shape; it does not attempt to implement a production invalidation service.

---

## 10. Negative-path tests

Test:

```text
Acme support → Acme internal allowed
Acme support → Globex public denied
Acme support → Acme restricted denied
Acme checkout member → Acme checkout allowed
Acme checkout member → Acme pricing denied
NovaTech admin → NovaTech restricted allowed
NovaTech admin → Acme restricted denied
Expired, superseded, future, or deleted document → denied for a current query
Missing tenant or classification → rejected before indexing
Same text in two tenants → only the authorized tenant is eligible
```

The strongest test is not "the expected document appears."

It is:

> **the forbidden document cannot appear anywhere in the retrieval path.**

The notebook treats these as hard security metrics:

```text
forbidden retrieval count       = 0
cross-tenant leakage count      = 0
classification violations       = 0
project-scope violations        = 0
lifecycle violations            = 0
```

This differs from relevance evaluation, where gradual quality trade-offs may be acceptable:

```text
authorization: Can this evidence be considered?
relevance:     How useful is this eligible evidence?
```

Relevance is measured only inside the authorized candidate space.

---

## 11. Fail closed at ingestion and retrieval

Security filtering is only as trustworthy as the metadata being filtered. The executable lab validates required fields, controlled values, dates, and chunk identity before indexing. Records with missing tenant or classification are quarantined rather than defaulted to public.

```text
unknown classification
missing tenant
invalid policy state
        ↓
do not retrieve
```

Security metadata must also survive preprocessing. The notebook chunks a restricted parent document and asserts that every child inherits `tenant_id`, `classification`, `project_id`, and document identity.

Some information should not enter a RAG index at all. Credentials, passwords, API keys, private keys, and access tokens belong in secret-management systems—not in a corpus protected only by metadata.

> Some data should not enter the RAG index at all. Authorization controls do not replace data-minimization and secret-management practices.

---

## 12. Audit the decision, not the sensitive content

The lab emits a minimal audit event containing:

```text
principal_id
tenant_id
policy_version
query_id
trusted filter
retrieved document IDs
```

It intentionally avoids logging retrieved document text. These fields help answer which principal, policy, and candidate scope produced a result without reproducing sensitive evidence in telemetry.

If a forbidden identifier or metadata record reaches a retrieval trace, debugging UI, cache, or evaluation export, security has already failed—even if no LLM was invoked and the final answer hides it.

---

## 13. Isolation architecture choices

Metadata filtering is one design, not the only enterprise isolation boundary.

| Pattern | Advantages | Trade-offs / when to consider |
|---|---|---|
| Shared index + trusted filters | Operational simplicity; efficient for many small tenants | Requires rigorous metadata validation, backend semantics, negative tests, and cache isolation |
| Namespaces or tenant-specific collections | Clearer logical boundary; easier tenant-level operations | More collections and routing complexity; backend-specific guarantees |
| Tenant-specific indexes/services | Stronger blast-radius isolation | Higher operational cost and capacity overhead |
| Database row-level security | Authorization close to structured records | Requires correct database policy and a retrieval architecture that preserves it |
| Physical data isolation | Strongest boundary for highly regulated workloads | Highest infrastructure and operational complexity |

Choose based on risk, regulatory obligations, tenant count, scale, backend guarantees, and operational capacity. Do not assume a metadata filter provides the same boundary as physical isolation.

---

## 14. Production policy-engine extension

The teaching function can later be replaced by an external policy decision point:

```text
application identity
        ↓
OPA / Cedar / custom authorization service
        ↓
allowed retrieval scope
        ↓
retrieval enforcement point
```

Authentication still happens outside the policy engine, and the retrieval service must enforce—not merely display—the returned scope. Version policy decisions and include that version in tests, caches, and audit evidence. The lab uses `POLICY_VERSION = "2026-01"` to make this traceability visible.

---

## 15. Authorization is not prompt-injection defense

Authorization answers whether a principal may retrieve a document. Prompt-injection defense addresses whether authorized but malicious content can manipulate downstream model behavior. A user may legitimately retrieve a poisoned document; that does not make its embedded instructions trustworthy.

```text
authorization ≠ prompt-injection defense
```

This course keeps generation minimal and forwards content-origin, instruction/data separation, tool-policy, and indirect-injection defenses to dedicated RAG security and red-team material.

---

## 16. Exercises

1. Add a `region` attribute to principals and resources, then extend the ABAC policy and negative tests.
2. Add a historical-policy search mode without weakening the default current-only policy.
3. Compare shared-index filtering with two tenant-specific Chroma collections and document the operational trade-off.
4. Add a role or project membership change and identify which cache entries must be invalidated.
5. Express the teaching policy as OPA Rego or Cedar pseudocode, keeping Chroma as the enforcement point.
6. Benchmark relevance inside the eligible candidate space at `k = 1, 3, 5` without merging relevance and authorization metrics.

---

## 17. Checkpoint

1. Why is post-generation filtering too late?
2. What metadata is security-critical?
3. Why must security metadata come from trusted ingestion/identity systems?
4. What is the difference between RBAC and ABAC?
5. Why does freshness belong in retrieval policy?
6. How can a cache violate authorization even when retrieval is correct?
7. What negative test proves tenant isolation?
8. Why should missing security metadata fail closed?
9. Why must authorization metrics remain separate from relevance metrics?

---

## What comes next

### [Intermediate 03 — Query Planning and Reranking](../03-query-reranking/README.md)

Once the candidate space is authorized, improve ranking within that safe candidate space.

---

## References

- LangChain — [Chroma integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma)
- Chroma — [Metadata filtering](https://docs.trychroma.com/docs/querying-collections/metadata-filtering) and [`where` filter reference](https://docs.trychroma.com/reference/where-filter)
- Qdrant — [Filtering](https://qdrant.tech/documentation/search/filtering/) and [multitenancy patterns](https://qdrant.tech/documentation/tutorials/multiple-partitions/)
- PostgreSQL — [Row security policies](https://www.postgresql.org/docs/17/ddl-rowsecurity.html)
- Open Policy Agent — [Policy decisions and deployment](https://www.openpolicyagent.org/docs)
- AWS Verified Permissions — [Cedar-based authorization](https://docs.aws.amazon.com/verifiedpermissions/latest/userguide/what-is-avp.html)
- OWASP — [Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- NIST — [AI RMF Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)

---

## Key takeaway

**Authorization is a deterministic retrieval constraint, not a prompt instruction.**
