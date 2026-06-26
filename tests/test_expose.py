"""Integration tests for ``expose``: real fixtures resolved through a container.

The pure discovery/collision rules live in ``test_collect_fixtures.py``;
request-scope lives in ``test_expose_request_scope.py`` (kept separate because
its ``request_widget`` fixture name would collide with the install below).
"""

import types

import pytest
from modern_di import Group, Scope, providers

from modern_di_pytest import expose
from tests.sample import Dependencies, ExtraDependencies, Repo, Service


# Default usage: introspect the caller module and install every provider across
# both groups (no name collisions between them).
expose(Dependencies, ExtraDependencies)


def test_expose_resolves_repo(repo: Repo) -> None:
    assert isinstance(repo, Repo)
    assert repo.label == "real"


def test_expose_resolves_service(service: Service) -> None:
    assert isinstance(service, Service)
    assert isinstance(service.repo, Repo)


def test_expose_resolves_fixture_from_second_group(extra_repo: Repo) -> None:
    assert isinstance(extra_repo, Repo)


def test_expose_installs_into_explicit_module() -> None:
    """``module=`` routes fixture installation to the given module."""
    target = types.ModuleType("_target")

    expose(Dependencies, module=target)

    assert hasattr(target, "repo")
    assert hasattr(target, "service")


def test_expose_leaves_module_untouched_on_collision() -> None:
    """A collision raises before any fixture is installed (atomicity)."""

    class Colliding(Group):
        repo = providers.Factory(scope=Scope.APP, creator=Repo)

    target = types.ModuleType("_target")
    with pytest.raises(ValueError, match="'repo'"):
        expose(Dependencies, Colliding, module=target)

    # None of Dependencies' providers should have been installed, even though
    # Dependencies is processed before the colliding Colliding group.
    assert not hasattr(target, "repo")
    assert not hasattr(target, "service")
    assert not hasattr(target, "request_widget")


def test_expose_raises_when_module_cannot_be_determined() -> None:
    """expose() called from exec() has no caller module; it should raise."""
    src = "from modern_di_pytest import expose\nfrom tests.sample import Dependencies\nexpose(Dependencies)\n"
    # exec'd code has no module per inspect.getmodule, which forces the
    # RuntimeError branch in expose().
    with pytest.raises(RuntimeError, match="could not determine the caller module"):
        exec(compile(src, "<string>", "exec"), {})  # noqa: S102
