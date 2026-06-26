# Architecture

The living truth about what `modern-di-pytest` does **now** — one file per
capability, plain prose, no frontmatter (dated by git history). The *why* and
the history live in [`planning/changes/`](../planning/changes/); this directory
holds only the current contract.

## Promotion rule

When a change alters a capability's behavior, the matching
`architecture/<capability>.md` is hand-edited **in the same PR** as the code, so
the doc rides in the same diff and is reviewed with it — never as a separate
post-merge step.

No capability files exist yet. Add one the first time a change touches a
capability worth recording as living truth (e.g. `architecture/expose.md` for
fixture exposure, `architecture/fixtures.md` for `modern_di_fixture`).
