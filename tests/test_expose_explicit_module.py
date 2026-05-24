import sys

import pytest

from modern_di_pytest import expose
from tests.sample import Dependencies, Repo


# Use the explicit `module=` form rather than letting expose() inspect the
# call stack. This proves the introspection path is optional.
expose(Dependencies, module=sys.modules[__name__])


def test_repo_via_explicit_module(repo: Repo) -> None:
    assert isinstance(repo, Repo)


def test_expose_raises_when_module_cannot_be_determined() -> None:
    """expose() called from exec() has no module; it should raise RuntimeError."""
    src = "from modern_di_pytest import expose\nfrom tests.sample import Dependencies\nexpose(Dependencies)\n"
    # exec'd code has no module per inspect.getmodule, which forces the
    # RuntimeError branch in expose().
    with pytest.raises(RuntimeError, match="could not determine the caller module"):
        exec(compile(src, "<string>", "exec"), {})  # noqa: S102
