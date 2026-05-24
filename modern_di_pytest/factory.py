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
        dependency: A type (resolved via ``container.resolve``) or a Provider
            (resolved via ``container.resolve_provider``).
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
        if isinstance(dependency, AbstractProvider):
            return container.resolve_provider(dependency)
        return container.resolve(dependency)

    return _fixture


def expose(
    group: type[Group],
    *,
    container_fixture: str = "di_container",
    pytest_scope: _PytestScope = "function",
    module: types.ModuleType | None = None,
) -> None:
    """Register one pytest fixture per Provider in ``group``.

    Each generated fixture is named after the class attribute it came from.

    Args:
        group: A ``Group`` subclass whose class attributes are Providers.
        container_fixture: Name of the pytest fixture yielding the container.
        pytest_scope: pytest fixture scope applied to every generated fixture.
        module: Module to inject fixtures into. Defaults to the caller's module
            (located via ``inspect.stack()``).

    Example (in ``conftest.py``)::

        from modern_di_pytest import expose
        from app.ioc import Dependencies

        expose(Dependencies)

    Every ``Dependencies.<attr>`` that is a Provider becomes a pytest fixture
    named ``<attr>``. Non-Provider class attributes are skipped.

    """
    if module is None:
        frame = inspect.stack()[1].frame
        module = inspect.getmodule(frame)
    if module is None:
        msg = "expose() could not determine the caller module; pass module=... explicitly."
        raise RuntimeError(msg)

    for attr_name, attr_value in vars(group).items():
        if isinstance(attr_value, AbstractProvider):
            fixture = modern_di_fixture(
                attr_value,
                container_fixture=container_fixture,
                name=attr_name,
                pytest_scope=pytest_scope,
            )
            setattr(module, attr_name, fixture)
