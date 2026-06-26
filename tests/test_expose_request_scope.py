from modern_di_pytest import expose
from tests.sample import Dependencies, Widget


# Kept as its own module: this installs a `request_widget` fixture whose name
# collides with the one in test_expose.py, so the two configurations cannot
# share a module. Also exercises the module-introspection path at REQUEST scope.
expose(Dependencies, container_fixture="di_request_container")


def test_request_widget_resolves(request_widget: Widget) -> None:
    assert isinstance(request_widget, Widget)
