"""Integration tests for ``expose``: real fixtures resolved through a container.

The pure discovery/collision rules live in ``test_collect_fixtures.py``;
request-scope lives in ``test_expose_request_scope.py`` (kept separate because
its ``request_widget`` fixture name would collide with the install below).
"""

import types

import pytest
from modern_di import Group, Scope, providers

from modern_di_pytest import expose, modern_di_fixture
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


def test_expose_with_no_groups_raises_type_error_before_finding_the_module() -> None:
    src = "from modern_di_pytest import expose\nexpose()\n"
    with pytest.raises(TypeError, match="at least one Group"):
        exec(compile(src, "<string>", "exec"), {})  # noqa: S102


def test_expose_rejects_provider_named_like_the_container_fixture() -> None:
    class Shadowing(Group):
        di_container = providers.Factory(scope=Scope.APP, creator=Repo)

    target = types.ModuleType("_target")
    with pytest.raises(ValueError, match=r"Shadowing.*'di_container'.*container_fixture"):
        expose(Dependencies, Shadowing, module=target)

    assert not hasattr(target, "di_container")
    assert not hasattr(target, "repo")


def test_expose_rejects_provider_named_like_a_custom_container_fixture() -> None:
    class Shadowing(Group):
        my_container = providers.Factory(scope=Scope.APP, creator=Repo)

    target = types.ModuleType("_target")
    with pytest.raises(ValueError, match=r"Shadowing.*'my_container'.*container_fixture"):
        expose(Shadowing, container_fixture="my_container", module=target)

    assert not hasattr(target, "my_container")


def test_expose_allows_provider_named_like_the_default_when_container_fixture_differs() -> None:
    class Named(Group):
        di_container = providers.Factory(scope=Scope.APP, creator=Repo)

    target = types.ModuleType("_target")
    expose(Named, container_fixture="my_container", module=target)

    assert hasattr(target, "di_container")


def test_expose_rejects_provider_named_like_a_fixture_in_the_module() -> None:
    target = types.ModuleType("_target")
    service = modern_di_fixture(Repo, name="service")
    vars(target)["service"] = service

    with pytest.raises(ValueError, match=r"'service'.*Dependencies.*already defines.*name="):
        expose(Dependencies, module=target)

    assert target.service is service
    assert not hasattr(target, "repo")
    assert not hasattr(target, "request_widget")


def test_expose_rejects_provider_named_like_a_non_fixture_attribute() -> None:
    target = types.ModuleType("_target")
    vars(target)["repo"] = types

    with pytest.raises(ValueError, match=r"'repo'.*Dependencies.*already defines"):
        expose(Dependencies, ExtraDependencies, module=target)

    assert target.repo is types
    assert not hasattr(target, "service")
    assert not hasattr(target, "extra_repo")


def test_expose_installs_alongside_unrelated_module_attributes() -> None:
    target = types.ModuleType("_target")
    vars(target)["Repo"] = Repo

    expose(Dependencies, module=target)

    assert target.Repo is Repo
    assert hasattr(target, "repo")
