import typing

import modern_di
import pytest

from tests.sample import Dependencies, ExtraDependencies


@pytest.fixture
def di_container() -> typing.Iterator[modern_di.Container]:
    with modern_di.Container(groups=[Dependencies, ExtraDependencies], validate=True) as container:
        yield container


@pytest.fixture
def di_request_container(
    di_container: modern_di.Container,
) -> typing.Iterator[modern_di.Container]:
    with di_container.build_child_container(scope=modern_di.Scope.REQUEST) as container:
        yield container
