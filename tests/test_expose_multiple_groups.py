from modern_di_pytest import expose
from tests.sample import Dependencies, ExtraDependencies, Repo


expose(Dependencies, ExtraDependencies)


def test_first_group_fixture(repo: Repo) -> None:
    assert isinstance(repo, Repo)


def test_second_group_fixture(extra_repo: Repo) -> None:
    assert isinstance(extra_repo, Repo)
