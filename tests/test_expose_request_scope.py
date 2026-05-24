from modern_di_pytest import expose
from tests.sample import Dependencies, Widget


# Generate every provider as a fixture, but resolved from the request container.
expose(Dependencies, container_fixture="di_request_container")


def test_request_widget_resolves(request_widget: Widget) -> None:
    assert isinstance(request_widget, Widget)
