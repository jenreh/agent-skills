---
name: runic-ogm
description: |
  Expert guide for runic.ogm — a SQLModel-style, graph-native Python OGM for
  Cypher databases (FalkorDB, Neo4j, Memgraph, ArcadeDB, Apache AGE). Use
  whenever the user defines graph models (Node/Edge), maps fields, declares
  relationships, writes graph queries/traversals, or does session/repository
  CRUD with runic. Invoke for any code that imports from `runic.ogm`, uses
  `Node`, `Edge`, `Field`, `Relation`, `Session`, `Repository`, `select()`, or
  the query builder, and for any "how do I model/query this graph in runic"
  task. This is the OGM skill; for schema migrations use the `runic-migrate`
  skill instead.
metadata:
  jenreh.registry/id: "jenreh:jenreh-graphdb"
  jenreh.registry/kind: "local"
  jenreh.registry/version: "0.1.0"
  jenreh.registry/source-marketplace: "jenreh/agent-skills"
  jenreh.registry/source-commit: "43748cbfd1e10079f1c194be5f68b1de59dc359b"
  jenreh.registry/source-license: "MIT"
  jenreh.registry/source-path: "plugins/jenreh-graphdb/skills/runic-ogm"
  jenreh.registry/source-digest: "d8c13373ec31456074d4d923e3de2b9f7b14af0d22ba45ec0edeeaebdaa75660"
  jenreh.registry/risk-tier: "standard"
  jenreh.registry/data-classification: "internal"
  jenreh.registry/supported-channels: "beta,stable"
---

# runic.ogm — Graph OGM for Cypher Databases

`runic.ogm` is a lightweight, SQLModel-inspired OGM for property-graph
databases. You declare nodes and edges as typed Python classes, then create,
read, relate, and query them through a `Session` — without hand-writing Cypher.
It targets **FalkorDB** first and also runs on **Neo4j, Memgraph, ArcadeDB, and
Apache AGE** through a pluggable driver layer.

Three pillars, each with a runnable example and a reference:

| Pillar | What it covers | Start here |
|---|---|---|
| **Mapping** | `Node`/`Edge` classes, `Field()`, defaults, PK, indexes, native types | [examples/mapping.py](examples/mapping.py) |
| **Relations** | `Relation()`, lazy/eager loading, edge models, `relate()`, polymorphism | [examples/relations.py](examples/relations.py) |
| **Query builder** | `select()`, filters, traversal, aggregation, search | [examples/query_builder.py](examples/query_builder.py) |

For the full API surface (every `Field`/`Relation` parameter, all `Session`,
`Repository`, and `QueryBuilder` methods, drivers, exceptions) read
[references/api-reference.md](references/api-reference.md). For task-oriented
recipes and gotchas read [references/cookbook.md](references/cookbook.md).

> The snippets omit the `# type: ignore` comments the repo's examples carry
> (`Field()` returns `Any`, which confuses some type checkers). Add them only if
> your checker complains.

---

## Quick start

> **Import everything from `runic.ogm`**, never from `runic.ogm.orm.*`.
> `Session`, `Repository`, `select` and their methods are runic's own API, not
> SQLAlchemy's.

```python
from runic.ogm import (
    Field, Node, Edge, Relation,
    Session, AsyncSession,
    Repository,
    select,
    count, avg, sum_,
)
from runic.ogm.driver.factory import create_driver

class User(Node, labels=["User"]):
    id: str = Field(primary_key=True)
    name: str
    email: str = Field(unique=True)
    active: bool = True

driver = create_driver("falkordb", host="localhost", port=6379, graph="app")

with Session(driver) as session:
    session.add(User(id="u1", name="Alice", email="alice@example.com"))
    session.commit()

    alice = session.get(User, "u1")     # read by primary key
    alice.name = "Alice B."             # mutation marks the entity dirty
    session.commit()                    # flushes the SET automatically

driver.close()
```

For tests without a server, use embedded FalkorDB (redislite): see the
cookbook's "Testing" section.

---

## Mapping: defining models

A **Node** is a vertex; declare it with a `labels` list. An **Edge** is a
relationship *property* model; declare it with a `type` string.

```python
from datetime import datetime
from enum import StrEnum
from runic.ogm import Edge, Field, Node, Vector, GeoLocation

class Status(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"

class Article(Node, labels=["Article"]):
    id: str = Field(primary_key=True)        # explicit PK
    title: str                               # bare annotation → required field
    summary: str | None = None               # optional → defaults to None
    status: Status                            # Enum → EnumConverter auto-applied
    published_at: datetime | None = None      # datetime → DatetimeConverter auto
    country: str = Field(interned=True)        # intern() dedup (FalkorDB)
    embedding: Vector | None = None           # vecf32() vector (FalkorDB)
    origin: GeoLocation | None = None         # point() geo (FalkorDB)
    views: int = Field(default=0)

class Authored(Edge, type="AUTHORED"):       # edge property model
    at: datetime
    primary: bool = Field(default=False)
```

**Field declaration — two equivalent styles.** A bare annotation
(`title: str`) is auto-promoted to a `Field`. Use the explicit `Field(...)` form
only when you need options: `primary_key`, `unique`, `index`, `index_type`,
`default`, `default_factory`, `converter`, `interned`, `generated`. See the full
parameter table in [references/api-reference.md](references/api-reference.md).

**Best practices for mapping:**

- **Pick the primary key deliberately.** `Field(primary_key=True)` is explicit
  and clearest. A field named `id` is treated as the PK by convention if none is
  marked. For DB-generated identifiers use `Field(generated=True)`.
- **Constructors are keyword-only.** Always `Article(id="a1", title="…")`, never
  positional. Unknown kwargs and missing required fields raise `TypeError`.
- **Let auto-converters work.** `datetime`, `Enum`, `Vector`, and `GeoLocation`
  fields get the right `TypeConverter` automatically — don't pass `converter=`
  for these. Explicit `converter=` always wins if you need custom behavior.
- **Native types are FalkorDB-specific.** `Vector` (`vecf32`), `GeoLocation`
  (`point`), and `interned=True` (`intern`) are wrapped only on FalkorDB; other
  backends store the raw value. See [examples/native_types.py](examples/native_types.py).
- **Indexes:** `Field(index=True)` for a range index, `Field(unique=True)` for a
  uniqueness constraint, `Field(index_type="FULLTEXT")` / `="VECTOR"` to back
  search. The declarations live on the model; actual index *creation* is done by
  `runic.migrate`'s `IndexManager` (see the `runic-migrate` skill).

**Polymorphism** uses multi-label nodes that share a `primary_label`
(`class City(Location, labels=["Location", "City"], primary_label="Location")`).
A query on the base class returns each row as its concrete subtype. Full
example: [examples/polymorphism.py](examples/polymorphism.py).

---

## Relations: connecting nodes

Declare a relationship with `Relation()`. `relationship`, `direction`, and
`target` are required; `edge_model` attaches a property model.

```python
from runic.ogm import Node, Relation

class User(Node, labels=["User"]):
    id: str = Field(primary_key=True)
    name: str
    # single related node
    manager: "User | None" = Relation(
        relationship="REPORTS_TO", direction="OUTGOING", target="User"
    )
    # collection, with edge properties
    articles: list["Article"] = Relation(
        relationship="AUTHORED", direction="OUTGOING",
        target="Article", edge_model="Authored",
    )
    # symmetric / undirected
    contacts: list["User"] = Relation(
        relationship="KNOWS", direction="BOTH", target="User"
    )
```

**Reading relationships — lazy vs eager:**

```python
# Lazy (default): first attribute access runs a query. Needs a live session.
user = session.get(User, "u1")
for a in user.articles:        # triggers the load here
    ...

# Eager: fetch alongside the parent in one query — no later round-trips.
user = session.get(User, "u1", fetch=["articles"])
```

**Mutating relationships** — use `relate()` / `unrelate()` instead of raw
Cypher. `relate()` uses MERGE semantics: it is idempotent and **re-calling
`relate()` with `edge=EdgeModel(...)` UPDATES the edge properties in place** —
no need for `unrelate()` + `relate()` just to update edge properties.
Pass the class-level descriptor for type safety:

```python
session.relate(user, User.articles, article,
               edge=Authored(at=datetime.now(UTC), primary=True))
# re-calling updates the edge in place — idempotent:
session.relate(user, User.articles, article,
               edge=Authored(at=datetime.now(UTC), primary=False))
session.unrelate(user, User.articles, article)   # remove the relationship
```

**Best practices for relations:**

- **Default to lazy; reach for `fetch=` when you know you need the data**,
  especially in loops (avoids N+1) or before detaching an entity.
- **Async has no lazy loading.** In `AsyncSession`, accessing an unloaded
  relation raises `LazyLoadError`, so use `await session.get(Cls, pk, fetch=[...])`.
  Session methods and bound builders are coroutines there. See
  [examples/async_session.py](examples/async_session.py).
- **Detached entities raise `DetachedEntityError`** on lazy access. After the
  session closes or you `expunge()`, the data is gone — fetch eagerly first.
- **Mirror two-sided relationships** by declaring the same `relationship` type
  with `OUTGOING` on one class and `INCOMING` on the other; both views read the
  same edges. Use `direction="BOTH"` for genuinely undirected links.
- **Edge properties** belong on an `Edge` model named to match the `type`; read
  them with `all_with_edges()` (below). Full example:
  [examples/relations.py](examples/relations.py).

---

## Query builder: reading the graph

Build statements with `select(Cls)` (session-independent) and run them through
the session. Filters come from comparing class-level field descriptors.

```python
from runic.ogm import select

# list of entities
users = session.scalars(
    select(User).where(User.active == True).order_by(User.name).limit(20)
)

# one-or-none
alice = session.scalar(select(User).where(User.email == "alice@example.com"))

# count
n = session.count(select(User).where(User.active == True))
```

**Execution methods** (session takes a `select(...)` statement):

| Method | Returns |
|---|---|
| `session.scalars(stmt)` | `list[Entity]` |
| `session.scalar(stmt)` | `Entity \| None` |
| `session.count(stmt)` | `int` |
| `session.all_rows(stmt)` | `list[dict]` — for `project()` / `aggregate()` |
| `session.all_with_edges(stmt)` | `list[tuple]` — node/edge/node rows |

`session.query(Cls)` returns a session-*bound* builder with terminal methods on
it instead: `.all()`, `.one()`, `.count()`, `.all_rows()`, `.all_with_edges()`.
Both styles are equivalent; `select()` is preferred for composable statements.

**Filtering** — descriptor operators produce filter expressions:

```python
select(Product).where(Product.price > 100)
select(Product).where(Product.name.contains("Graph"))
select(Product).where(Product.sku.is_null())
select(Product).where(Product.id.in_(["p1", "p2"]))
# Boolean composition — parenthesize each operand:
select(Product).where((Product.category == "books") & (Product.active == True))
select(Product).where((Product.a == 1) | (Product.b == 2))
select(Product).where(~(Product.active == True))
```

Operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `.contains()`, `.startswith()`,
`.endswith()`, `.matches()` (regex), `.is_null()`, `.is_not_null()`, `.in_()`,
`.not_in_()`. Multiple `.where()` calls are AND-combined. Refinements:
`.order_by(field, desc=True)`, `.limit(n)`, `.skip(n)`, `.distinct()`.

**Projection & aggregation** return rows (dicts), read via `all_rows()`:

```python
from runic.ogm import avg, count, sum_

rows = session.all_rows(select(Product).project(Product.name, Product.price))
# keys are "n.name", "n.price"

summary = session.all_rows(
    select(Order).where(Order.status == "done").aggregate(
        count("*").as_("total"),
        sum_(Order.amount).as_("revenue"),
        avg(Order.amount).as_("avg"),
    )
)
# group by a FIELD — pass "alias.property" (default node alias is "n"):
per_city = session.all_rows(
    select(User).aggregate(count("*").as_("n_users"), group_by="n.city")
)
# → [{"n.city": "Berlin", "n_users": 3}, {"n.city": "Paris", "n_users": 2}, ...]

# group by the whole node — pass the bare alias (handy after a traversal):
per_user = session.all_rows(
    select(User).alias("u").traverse(User.orders).aggregate(
        sum_(Order.amount).as_("revenue"), group_by="u"
    )
)
```

Helpers: `count`, `avg`, `sum_`, `min_`, `max_`, `collect` (each with
`.as_()`; `count`/`collect` accept `distinct=True`).

**Traversal** — alias nodes, hop across relationships, filter by alias:

```python
# Alice's active friends-of-friends who authored a post
posts = session.scalars(
    select(User).alias("u").where(User.id == "alice")
    .traverse(User.friends).alias("f")
    .where(User.active == True, on="f")
    .traverse(User.authored).alias("post")
    .return_target("post")
)
```

- `.traverse(Cls.rel, edge_alias="e", optional=True)` — one hop. `optional=True`
  (default) is a left join; `optional=False` is a required (inner) join.
- **When filtering on an edge property, use `optional=False`** — an
  `OPTIONAL MATCH` + `WHERE` nullifies non-matching rows instead of dropping
  them.
- `.repeat(Cls.rel, min_hops=1, max_hops=3)` — variable-length path.
- `.with_("alias")` — pipeline stages. `.return_target("alias")`,
  `.return_nodes(...)`, `.return_edge("e")` — choose result columns.
- Filter on an aliased node or edge with `.where(expr, on="alias")`.

**Edge properties** come back via `all_with_edges()`:

```python
rows = session.all_with_edges(
    select(User).alias("u").where(User.id == "alice")
    .traverse(User.rated_movies, edge_alias="r").alias("m")
    .where(Rated.score >= 9.0, on="r")
    .return_nodes("u", "m").return_edge("r")
)
for user, edge, movie in rows:    # (User, Rated, Movie) tuples
    ...
```

**Search:** `session.fulltext_search(Article, query="...")` and
`session.vector_search(Article, field=Article.embedding, vector=[...], k=3)`
return builders (`.where()`, `.limit()`, `.all()`). Both need a pre-created index;
setup per backend is in the cookbook's "Fulltext & vector search" section.

**Inspect without executing:** `cypher, params = select(...).build()`. Reach for
this when debugging a query or explaining what runic generates.

---

## Sessions & repositories

- **Lifecycle:** use `with Session(driver) as session:`. `add()` / `add_all()`
  stage inserts; `delete()` stages removals. `flush()` writes pending changes
  without ending the logical transaction; `commit()` flushes then clears
  tracking; `rollback()` discards pending state.
  Setting any attribute on a loaded entity marks it dirty for the next commit.
- **Identity map:** within one session, `get()` returns the same instance for a
  given `(type, pk)`. `rollback()` discards pending state; `expire()`/`refresh()`
  re-read from the graph; `expunge()` detaches.
- **Repository** wraps a session + model for collection reads:
  `Repository(session, User).find_all(skip=0, limit=50)`, `.find_all_by_ids(ids)`,
  `.count()`, `.exists(pk)`. Pagination is offset-based via `skip`/`limit` (there
  is no `Page` object).
- **Custom repositories** subclass `Repository[T]` and add methods using
  `self.query()` (the bound builder) or the raw-Cypher helpers:
  - `self.cypher(q, params, returns=Cls)` — maps rows to entities
  - `self.cypher(q, params, returns=int)` — maps to a scalar; `write=True` for mutations
  - `self.cypher_one(q, params, returns=int)` — first mapped row; use for single scalars
  - `self.cypher_raw(q, params)` — returns `GraphResult` with `.columns` (list of names) and `.rows` (list of value lists)

  A worked `ArticleRepository` is in the cookbook's "Custom repositories & raw
  Cypher" section.

---

## Key rules

- Prefer `relate()`/`unrelate()` and the query builder over raw Cypher; drop to
  `session.execute()` / `repo.cypher()` only for what the builder can't express.
- Use `fetch=[...]` to avoid N+1 in loops and **always** in async code.
- `optional=False` whenever you filter on a traversed edge's properties.
- `Vector`, `GeoLocation`, and `interned` are **FalkorDB-only** native types;
  on other backends the raw value is stored. **Fulltext and vector search also
  work on Neo4j and Memgraph** but require pre-created named indexes (see
  cookbook multi-backend table); they are absent on ArcadeDB and Apache AGE.
- **Multi-backend driver params differ.** FalkorDB uses `graph=` (the graph
  name); Neo4j/Memgraph/ArcadeDB use `database=`, `username=`, `password=`.
  Neo4j defaults to `encrypted=True`. Models and queries are unchanged across
  backends (api-reference "Drivers & factory").
- Indexes are *declared* on models but *created* by `runic.migrate` — keep
  schema changes in migrations, not application code.
