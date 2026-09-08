# Agent Guidance

## Prime Invariants

- Answer first; act only on an explicit go for the named scope. A plan, report, or spec is not a go.
- No code change without an approved plan. Non-shipped bookkeeping needs none; when unsure, treat it as code.
- Commit slices with records. Branch work is incomplete until merged into main and its branch deleted. Push policy: `.agents/push-policy.md`.
- Only repo files are durable memory. Under context pressure, re-read this file; hand off before judgment degrades.

## Repo-Specific Guidance

@.agents/repo-guidance.md

The more specific rule wins. Flag a contradiction you cannot reconcile.

## Invariants

- Record durable facts, decisions, and open questions in `.agents/`, understandable without chat; label unverified inferences as assumptions.
- One canonical location per truth; pointers over copies. `.agents/state.md` is the single current-state entry point, kept current by the working agent as work lands.
- Never bypass a failed check, guard, ignore rule, or refusal without proving it is not load-bearing. Otherwise stop or ask.
- Escalate on stalled progress, never duration: after 2–3 attempts with no verifiable progress, report the obstacle and proposed next action.
- Keep this file portable; repo-specific rules live in `.agents/`. Refresh-governed artifacts are toolkit-owned. Never edit installed copies; route changes to the toolkit. Exclude those copies from repo lint/format scope; refresh restores divergence. Seeded policy files (`.agents/push-policy.md`) are repo-owned and editable.

## Session Startup

Read this file, `.agents/repo-guidance.md`, and `.agents/state.md` before changing anything. Check clone freshness with `git ls-remote` against the local ref before trusting recorded state; if unreachable, proceed with a caveat. Hook trust requires explaining the hooks and an explicit go.

## Source of Truth

Human request → this file and `.agents/repo-guidance.md` → `.agents/state.md`, `.agents/decisions.md`, approved playbooks → code, tests, and CI as evidence → other docs. Fix the lower source on disagreement, or ask.

## Operator Requests

Read `.agents/playbooks/<name>.md` at invocation; it defines the procedure.

- `catchup` — re-ground and report; no other work until the owner responds.
- `handoff` — fast state snapshot.
- `decision` — record a settled decision in `.agents/decisions.md`; update affected guidance.
- `plan` — draft or update a durable plan.
- `playbook <name>` — run it; report if missing.
- `toolkit` — list owner verbs, one plain line each.

## Owner Gates

Ask one unsettled decision: context, action, consequence, recommendation. Approval remains valid within its scope; silence authorizes nothing.

## Verification

Self-review is forbidden unless explicitly requested by the owner.

Run the entry point in `.agents/repo-guidance.md` before claiming completion; docs-only changes need `git diff --check` unless they affect behavior. Prove a new test bites: revert the fix, watch it fail, restore. State any check not run.

## Git Safety

Merges, deletion, history rewrites (amend, rebase, squash, force-push), and outward-facing actions require explicit authority for those actions. One finding per commit. Verify content reached main with `git diff` before deleting a branch; ancestry alone is insufficient. Branch setup and closeout: `.agents/playbooks/git.md`.

## Final Response

Lead with the result. While work remains, name its pending step and one proposed action; never report incomplete work as done.
