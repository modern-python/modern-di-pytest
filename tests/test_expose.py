import sys

from modern_di_pytest import expose
from tests.sample import Dependencies, Repo, Service


expose(Dependencies)


def test_expose_generates_repo_fixture(repo: Repo) -> None:
    assert isinstance(repo, Repo)
    assert repo.label == "real"


def test_expose_generates_service_fixture(service: Service) -> None:
    assert isinstance(service, Service)
    assert isinstance(service.repo, Repo)


def test_expose_skips_non_provider_attributes() -> None:
    this_module = sys.modules[__name__]

    assert not hasattr(this_module, "not_a_provider")
    assert not hasattr(this_module, "_hidden_int")
