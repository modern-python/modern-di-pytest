import types

import modern_di_pytest


def test_public_surface_is_exactly_expose_and_modern_di_fixture() -> None:
    """INVARIANT: the package exports exactly ``expose`` and ``modern_di_fixture``.

    Broken by promoting a helper to a public name, in ``__all__`` or as an unprefixed
    binding in ``__init__`` -- the latter is public whether or not it was meant to be.
    Two symbols are the whole semver contract of an adapter this thin, and being thin is
    the point: every name added here is one a major release has to keep working, and the
    surface is the only place that cost is visible before it is paid.
    """
    public = sorted(
        name
        for name, value in vars(modern_di_pytest).items()
        if not name.startswith("_") and not isinstance(value, types.ModuleType)
    )

    assert public == ["expose", "modern_di_fixture"]
    assert modern_di_pytest.__all__ == public
