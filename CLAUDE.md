# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `just` and `uv`. See `Justfile` for the source of truth.

- `just install` — `uv lock --upgrade` then `uv sync --all-extras --frozen --group lint`
- `just lint` — runs `eof-fixer`, `ruff format`, `ruff check --fix`, then `ty check` (writes)
- `just lint-ci` — same checks in non-mutating mode (`--check`, `--no-fix`)
- `just test` — `uv run --no-sync pytest` (forwards extra args; `addopts` already adds `--cov=. --cov-report term-missing`)
- `just test-branch` — `pytest --cov-branch`
- Run a single test: `just test tests/test_expose.py::test_expose_generates_repo_fixture` (or `-k <expr>`)
- Type checker is `ty`; suppress with `# ty: ignore` (not `# type: ignore`)

## Architecture

This package is a thin pytest adapter over [`modern-di`](https://github.com/modern-python/modern-di). All implementation lives in `modern_di_pytest/factory.py` and exposes exactly two public symbols:

- `modern_di_fixture(dependency, *, container_fixture="di_container", name=None, pytest_scope="function")` — wraps a single type or `AbstractProvider` in a `@pytest.fixture`. At fixture time it calls `request.getfixturevalue(container_fixture)`, then dispatches: `AbstractProvider` → `container.resolve_provider(...)`, otherwise `container.resolve(...)`.
- `expose(group, *, container_fixture="di_container", pytest_scope="function", module=None)` — iterates `vars(group)`, and for each attribute that is an `AbstractProvider` instance, builds a `modern_di_fixture` and `setattr`s it onto the target module under the attribute's name. Non-Provider attributes (strings, ints, underscored, etc.) are silently skipped. When `module` is omitted, the caller's module is located via `inspect.stack()[1]` — `expose` therefore only works when called from module scope of a `conftest.py` / test module, not from inside a function.

Key contract: this package does **not** own the container. The user defines a `di_container` pytest fixture (any scope) that yields a `modern_di.Container`. Child-scoped containers (e.g. `REQUEST`) are accessed by passing a different `container_fixture=` name — see `tests/conftest.py` for the `di_container` / `di_request_container` pattern. Overrides are not re-implemented here; users call `Container.override()` / `reset_override()` directly.

`tests/sample.py` is the reference fixture model: a `Group` subclass holding `providers.Factory` instances at `APP` and `REQUEST` scopes, plus deliberately non-Provider attributes to exercise the skip path in `expose`.
