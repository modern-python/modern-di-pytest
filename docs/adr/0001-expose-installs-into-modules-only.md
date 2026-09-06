# `expose` installs into modules only; no `FixtureSet` install seam

**Decision:** `expose()` installs fixtures into modules only; we will not introduce a `FixtureSet`
(or equivalent installer) seam.

`expose()` does two things: it **decides** which providers become fixtures (discovery, the
skip-non-Provider rule, cross-group collision detection) and it **installs** the resulting fixtures
onto a module. The decision half was extracted into the private, pure `_collect_fixtures`, which
captured the durable value — the rules became testable through a return value, and the test suite
collapsed accordingly.

The recurring follow-up is to extract the *install* half too: wrap the `name -> provider` mapping in
a `FixtureSet` exposing `.install(into=...)`, turning the install target into a seam.

The architectural test for introducing a seam is **one adapter = hypothetical seam, two = real
one**. The install targets that actually exist are the caller's module (default, located via
`inspect.stack()`) and an explicit module passed as `module=`. Both are `types.ModuleType` — the
*same* adapter type exercised with two instances, not two adapters. There is no concrete non-module
install target — a pytest class namespace, a programmatic consumer, an ecosystem integration —
now or clearly coming. The library is, and is expected to remain, a conftest-level adapter that
installs fixtures into modules.

So a `FixtureSet` would fail the deletion test: delete it and no complexity reappears, because the
`setattr` loop simply inlines back into `expose()`. It would add an interface without adding
behaviour. The install step stays a plain `setattr` loop over the mapping `_collect_fixtures`
returns, and the public surface stays at two symbols.

**Revisit trigger:** a real second install target appears — two genuinely different adapters at the
install point, such as installing onto a pytest test-class namespace, or handing the mapping to a
programmatic consumer. At that moment the seam becomes real and a `FixtureSet` earns its keep.
