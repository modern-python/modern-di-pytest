import inspect
import types
import typing

import pytest
from modern_di.group import Group
from modern_di.providers.abstract import AbstractProvider


T = typing.TypeVar("T")

_PytestScope = typing.Literal["function", "class", "module", "package", "session"]


def modern_di_fixture(
    dependency: type[T] | AbstractProvider[T],
    *,
    container_fixture: str = "di_container",
    name: str | None = None,
    pytest_scope: _PytestScope = "function",
) -> typing.Any:  # noqa: ANN401
    """Turn a modern-di dependency into a pytest fixture.

    Args:
        dependency: A type or a Provider, resolved via
            ``container.resolve_dependency``.
        container_fixture: Name of the pytest fixture that yields the container
            to resolve from. Defaults to ``"di_container"``. Use a child
            container fixture (e.g. ``"di_request_container"``) to resolve at a
            deeper scope.
        name: Optional pytest fixture name. Defaults to the assigned variable
            name in the conftest.
        pytest_scope: pytest fixture scope (``"function"`` by default).

    Returns:
        A pytest fixture object. Assign it to a module-level name and pytest
        will collect it.

    Example::

        user_service = modern_di_fixture(UserService)


        def test_listing(user_service):
            assert user_service.list_users() == []

    """

    @pytest.fixture(name=name, scope=pytest_scope)
    def _fixture(request: pytest.FixtureRequest) -> typing.Any:  # noqa: ANN401
        container = request.getfixturevalue(container_fixture)
        return container.resolve_dependency(dependency)

    return _fixture


def _collect_fixtures(*groups: type[Group]) -> dict[str, AbstractProvider[typing.Any]]:
    """Decide which Providers to expose and under what names.

    Pure: walks each group's attributes, keeps the ``AbstractProvider``s, skips
    everything else, and returns a ``name -> provider`` mapping. Raises before
    returning anything so callers never act on a partial result:

    - ``TypeError`` if no groups are given.
    - ``ValueError`` if a name is claimed by more than one group.
    """
    if not groups:
        msg = "expose() requires at least one Group."
        raise TypeError(msg)

    providers: dict[str, AbstractProvider[typing.Any]] = {}
    source: dict[str, type[Group]] = {}
    for group in groups:
        for attr_name, attr_value in vars(group).items():
            if not isinstance(attr_value, AbstractProvider):
                continue
            if attr_name in source:
                prior = source[attr_name]
                msg = (
                    f"expose() cannot register {attr_name!r} from "
                    f"{group.__name__}: already provided by {prior.__name__}."
                )
                raise ValueError(msg)
            source[attr_name] = group
            providers[attr_name] = attr_value
    return providers


def expose(
    *groups: type[Group],
    container_fixture: str = "di_container",
    pytest_scope: _PytestScope = "function",
    module: types.ModuleType | None = None,
) -> None:
    """Register one pytest fixture per Provider across one or more groups.

    Each generated fixture is named after the class attribute it came from.

    Args:
        *groups: One or more ``Group`` subclasses whose class attributes are
            Providers. Attribute names must be unique across all groups; a
            duplicate raises ``ValueError``.
        container_fixture: Name of the pytest fixture yielding the container.
        pytest_scope: pytest fixture scope applied to every generated fixture.
        module: Module to inject fixtures into. Defaults to the caller's module
            (located via ``inspect.stack()``).

    Example (in ``conftest.py``)::

        from modern_di_pytest import expose
        from app.ioc import Auth, Billing, Dependencies

        expose(Dependencies, Auth, Billing)

    Every Provider class attribute on each group becomes a pytest fixture
    named after that attribute. Non-Provider class attributes are skipped.

    """
    # Resolve the full set of fixtures (and surface any error) before touching
    # the module, so a collision leaves the target untouched.
    providers = _collect_fixtures(*groups)

    if module is None:
        frame = inspect.stack()[1].frame
        module = inspect.getmodule(frame)
    if module is None:
        msg = "expose() could not determine the caller module; pass module=... explicitly."
        raise RuntimeError(msg)

    for attr_name, provider in providers.items():
        fixture = modern_di_fixture(
            provider,
            container_fixture=container_fixture,
            name=attr_name,
            pytest_scope=pytest_scope,
        )
        setattr(module, attr_name, fixture)
