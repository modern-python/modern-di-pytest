"""Tests for the pure decision behind ``expose``: ``_collect_fixtures``.

These exercise the discovery, skip, and collision rules directly through the
seam's return value — no module installation, no throwaway modules.
"""

import pytest
from modern_di import Group, Scope, providers

from modern_di_pytest.factory import _collect_fixtures
from tests.sample import Dependencies, ExtraDependencies, InheritingDependencies


def test_collects_providers_by_name() -> None:
    collected = _collect_fixtures(Dependencies)

    assert set(collected) == {"repo", "service", "request_widget"}
    assert collected["repo"] is Dependencies.repo
    assert collected["service"] is Dependencies.service


def test_collects_providers_inherited_from_a_parent_group() -> None:
    """INVARIANT: a provider inherited from a parent Group becomes a fixture.

    Discovering providers by walking ``vars(group)`` breaks this: ``vars`` sees only
    the class's own body, so an inherited provider silently gets no fixture while the
    container — which walks the full MRO — still registers and resolves it.
    """
    collected = _collect_fixtures(InheritingDependencies)

    assert set(collected) == {"repo", "service", "request_widget", "own_repo"}
    assert collected["repo"] is Dependencies.repo


def test_skips_non_provider_attributes() -> None:
    collected = _collect_fixtures(Dependencies)

    assert "not_a_provider" not in collected
    assert "_hidden_int" not in collected


def test_collects_across_multiple_groups() -> None:
    collected = _collect_fixtures(Dependencies, ExtraDependencies)

    assert "extra_repo" in collected
    assert collected["extra_repo"] is ExtraDependencies.extra_repo


def test_raises_on_duplicate_name_across_groups() -> None:
    class Colliding(Group):
        repo = providers.Factory(scope=Scope.APP, creator=object)

    with pytest.raises(ValueError, match=r"'repo'.*Colliding.*Dependencies"):
        _collect_fixtures(Dependencies, Colliding)


def test_raises_when_called_with_no_groups() -> None:
    with pytest.raises(TypeError, match="at least one Group"):
        _collect_fixtures()
