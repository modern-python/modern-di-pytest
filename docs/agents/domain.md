# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the
codebase. This repo is **single-context**.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root: what this package is, and the glossary.
- **`docs/adr/`**: read the decision records that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest
creating them upfront. The `/domain-modeling` skill creates them lazily when terms or decisions
actually get resolved.

## File structure

```
/
├── CONTEXT.md
├── docs/adr/
│   └── 0001-….md
├── modern_di_pytest/   ← the whole implementation, one module
└── tests/
```

There is no `CONTEXT-MAP.md` and no per-package `CONTEXT.md`: one repo, one context. There is also
no `architecture/` and no `planning/` — the present is the source, and what must stay true is a test
whose docstring opens `INVARIANT:`.

## Use the glossary's vocabulary

When your output names a domain concept (an issue title, a refactor proposal, a hypothesis, a test
name), use the term as defined in `CONTEXT.md`, and honor its `_Avoid_:` lines — those synonyms are
rejected on purpose. Write `install` and not `inject` or `register`.

This package is a thin adapter over `modern-di`, so most domain terms are that project's, not this
one's: `Container`, `Provider`, `Group`, `Scope`, `Resolution`, `Override`. Its `CONTEXT.md` is the
upstream authority; do not redefine a term here that `modern-di` already defines.

If the concept you need is in neither, that's a signal: either you're inventing language the project
doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Where a new fact goes

Run the admission check in `AGENTS.md` before writing anything down. In short: derivable from
`modern_di_pytest/` → don't write it; enforceable → a named test with an `INVARIANT:` docstring; a
user needs it → `README.md`; a rejected alternative → an ADR under `docs/adr/`, with its revisit
trigger; real work you are not doing now → a GitHub issue. Nothing else gets written.

## Link style inside `docs/`

The files under `docs/` are read on GitHub, and CI runs an offline link check over every Markdown
file in the repo. Between files inside `docs/`, use a plain relative `.md` link — from one ADR to
another, that is `[ADR-NNNN](NNNN-slug.md)`.

## Flag ADR conflicts

If your output contradicts an existing decision record, surface it explicitly rather than silently
overriding:

> _Contradicts ADR-NNNN (its title), but worth reopening because…_

A decision's **Revisit trigger** names the concrete signal that should reopen it. If that signal has
fired, say so.
