# modern-di-pytest

A pytest adapter over [`modern-di`](https://github.com/modern-python/modern-di): it turns
providers declared on a `Group` into pytest fixtures, one per provider, resolved through a
container the test suite owns.

## Language

A term is listed only when there is a synonym to reject, or a meaning subtle enough that code and
docs must agree on it. General programming vocabulary does not belong here, however heavily this
package uses it.

The domain terms are `modern-di`'s — `Container`, `Provider`, `Group`, `Scope`, `Resolution`,
`Override`. That project's `CONTEXT.md` is the authority for all of them; nothing here redefines
one. The three below are this package's own.

**Install**:
Binding a generated fixture onto a module as a module-level attribute, which is what makes pytest
collect it. `expose()` installs; `modern_di_fixture()` returns a fixture the caller assigns itself.
_Avoid_: inject, register — both have been used for this in the same breath as `install`, and
`inject` additionally collides with the DI sense of injection, which is `modern-di`'s word for
passing a resolved value into a callable.

**Generated fixture**:
A pytest fixture this package builds from a provider or a type. It resolves at fixture time, never
at import time.

**Container fixture**:
The user's own pytest fixture yielding the `modern_di.Container` a generated fixture resolves
from — named by `container_fixture=`, defaulting to `di_container`. This package never defines one;
pointing a fixture at a child scope means naming a different container fixture, not a different
package API.
