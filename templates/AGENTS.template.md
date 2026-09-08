# Agent Guidance

## Prime Invariants

- Answer briefly; act only on an explicit go for its named scope. A plan, report, or spec alone is not a go.
- Code changes need an approved approach; a short proposal suffices. Write a plan document only when requested.
- Commit slices with records. Branch work is incomplete until merged into main and its branch deleted. Push policy: `.agents/push-policy.md`.
- Repo files are durable memory. Restore missing context before judgment degrades; hand off when needed.

## Repo-Specific Guidance

@.agents/repo-guidance.md

The more specific rule wins. Flag a contradiction you cannot reconcile.

## Invariants

- Record durable facts, decisions and open questions once in `.agents/`, understandable without chat; label assumptions. Use pointers over copies.
- `.agents/state.md` is the current-state entry point, kept current by the working agent as work lands.
- Reuse valid evidence, reads and results. Extra tool/model calls must resolve material uncertainty; formatting never justifies a model retry. Delegate only when authorized and useful.
- Never bypass a failed check, guard, ignore rule or refusal without proving it is not load-bearing. Otherwise stop or ask.
- After 2–3 attempts without verifiable progress, report the obstacle and next action.
- Keep this file portable; repo-specific rules live in `.agents/`. Refresh-governed artifacts are toolkit-owned. Route changes to toolkit sources; exclude installed copies from repo edits/lint. Seeded policy files (`.agents/push-policy.md`) are repo-owned and editable.

## Session Startup

Load this file, `.agents/repo-guidance.md` and `.agents/state.md` only where missing or stale in context. Before trusting recorded state, compare local refs with `git ls-remote`; reuse a current check and caveat unreachable remotes. Hook trust needs an explanation and explicit authority.

## Source of Truth

Human request → this file and repo guidance → state, decisions and approved playbooks → code/tests/CI evidence → other docs. Fix the lower source on disagreement, or ask. Read archives only for relevant historical evidence.

## Operator Requests

Read the requested `.agents/playbooks/<name>.md` if not already current in context; report if missing.

- `catchup` — re-ground, tidy relevant records and report.
- `handoff` — save current state.
- `decision` — record a settled decision and update affected guidance.
- `plan` — draft or update a durable plan.
- `playbook <name>` — run it.
- `toolkit` — list owner verbs.

## Owner Gates

Ask only for an unsettled decision, with context, consequence and recommendation. Existing approval stands within scope; silence authorizes nothing.

## Verification

Self-review is forbidden unless explicitly requested by the owner.

Run required repo verification; docs-only changes need `git diff --check` unless they affect behavior. A new regression guard must detect the failure and pass with the fix; reuse that proof on unchanged code. Report material checks not run.

## Git Safety

Merges, deletion, history rewrites and outward-facing actions require explicit authority; reuse it once given. One finding per commit. Verify content reached main with `git diff` before deleting its work branch. Setup/closeout: `.agents/playbooks/git.md`.

## Final Response

Lead with the result. Name remaining work and its next action; never report incomplete work as done.
