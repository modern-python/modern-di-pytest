import dataclasses

from modern_di import Group, Scope, providers


@dataclasses.dataclass
class Repo:
    label: str = "real"


@dataclasses.dataclass
class Service:
    repo: Repo


@dataclasses.dataclass
class Widget:
    repo: Repo


class Dependencies(Group):
    repo = providers.Factory(scope=Scope.APP, creator=Repo)
    service = providers.Factory(scope=Scope.APP, creator=Service)
    request_widget = providers.Factory(scope=Scope.REQUEST, creator=Widget)

    not_a_provider = "string literal, not a provider"
    _hidden_int = 7
