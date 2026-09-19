# `expose` installs into modules only

`expose()` both decides which providers become fixtures, by collecting each group's named providers,
rejecting an empty call and raising on a name two groups both claim, and installs them onto a
module. The decision half already lives in the private, pure `_collect_fixtures`; the recurring
proposal is to extract the install half too, wrapping the `name -> provider` mapping in a
`FixtureSet` exposing `.install(into=...)`. We will not, because a seam needs two adapters and the
only install targets are the caller's module, located via `inspect.stack()`, and an explicit
`module=`, both `types.ModuleType` - one adapter exercised with two instances. Deleting a
`FixtureSet` would bring back no complexity, since its `setattr` loop simply inlines, so the install
step stays that loop and the public surface stays at `expose` and `modern_di_fixture`. A genuinely
different install target, such as a pytest class namespace, is what would make the seam real.
