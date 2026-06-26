# 1. `expose` installs into modules only; no `FixtureSet` install seam

Date: 2026-06-26

## Status

Accepted

## Context

`expose()` does two things: it **decides** which providers become fixtures
(discovery, the skip-non-Provider rule, cross-group collision detection) and it
**installs** the resulting fixtures by `setattr`-ing them onto a module.

The decision half was extracted into the private, pure
`_collect_fixtures(*groups) -> dict[str, AbstractProvider]` (see the
`modern_di_pytest/factory.py` seam). That captured the durable value: the rules
are now testable through a return value, and the test suite collapsed
accordingly.

A recurring follow-up suggestion is to also extract the *install* half — wrap
the `name -> provider` mapping in a `FixtureSet` object exposing
`.install(into=...)`, turning the install target into a seam:

```python
fixtures = collect_fixtures(Dependencies, Auth)   # a FixtureSet
fixtures.install(into=module)
```

The architectural test for introducing a seam is **one adapter = hypothetical
seam, two = real one**. We examined the install targets that actually exist:

- the **caller's module** (default, located via `inspect.stack()`), and
- an **explicit module** passed as `module=`.

Both are `types.ModuleType` — the *same* adapter type exercised with two
instances, not two different adapters. There is no concrete non-module install
target (a pytest class namespace, a programmatic/inspection consumer, a
modern-di ecosystem integration), now or clearly coming. The library is, and is
expected to remain, a conftest-level adapter that installs fixtures into
modules.

## Decision

`expose()` installs into modules only. We will **not** introduce a `FixtureSet`
(or equivalent installer) seam. The install step stays as a plain `setattr`
loop inside `expose()`, over the mapping returned by `_collect_fixtures`.

## Consequences

- The public surface stays at two symbols (`expose`, `modern_di_fixture`); the
  decision lives behind the private `_collect_fixtures`.
- A `FixtureSet` would fail the deletion test: delete it and no complexity
  reappears — the `setattr` loop simply inlines back into `expose()`. It would
  add an interface without adding behaviour.
- If a real second install target ever appears (two genuinely different
  adapters at the install point), revisit this decision: at that moment the
  seam becomes real and a `FixtureSet` earns its keep. Until then, this ADR
  exists so architecture reviews don't re-propose the split.
