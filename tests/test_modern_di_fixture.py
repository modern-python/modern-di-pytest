from modern_di_pytest import modern_di_fixture
from tests.sample import Dependencies, Repo, Service, Widget


# Fixture from a type (resolved via container.resolve).
service_by_type = modern_di_fixture(Service)

# Fixture from a Provider (resolved via container.resolve_provider).
service_by_provider = modern_di_fixture(Dependencies.service)

# Fixture pointing at the request-scope container.
widget = modern_di_fixture(Widget, container_fixture="di_request_container")

# Fixture with an explicit custom name.
renamed_repo = modern_di_fixture(Repo, name="my_repo")


def test_resolve_by_type(service_by_type: Service) -> None:
    assert isinstance(service_by_type, Service)
    assert isinstance(service_by_type.repo, Repo)


def test_resolve_by_provider(service_by_provider: Service) -> None:
    assert isinstance(service_by_provider, Service)


def test_resolve_from_request_container(widget: Widget) -> None:
    assert isinstance(widget, Widget)
    assert isinstance(widget.repo, Repo)


def test_fixture_with_custom_name(my_repo: Repo) -> None:
    assert isinstance(my_repo, Repo)
    assert my_repo.label == "real"
