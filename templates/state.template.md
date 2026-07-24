# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries; the `drift` operator's
hygiene pass rotates landed or superseded entries verbatim to
`docs/history/state-archive.md` (create it on first use) — never summarize
them away, never let them pile up here. Write-time rules: volatile facts
(CI state, counts) carry `as of <commit>`; push status is never recorded
here — git owns it, and unpushed work is mentioned in the moment it
matters, never written down; a count or enumeration another file owns is
pointed to, never copied; machine-specific
facts (local toolchains, host layout, per-clone posture) go to the tracked
`.agents/machines.md`, keyed by machine and dated — never here.

## Now

- <Current active work, if any.>

## Next

- <The next useful action or "None recorded".>

## Blockers

- <Open blockers or "None recorded". Re-verify each parked item's recorded
  basis at every handoff; a falsified basis moves here with the new evidence.>

## Verification

- See `.agents/repo-guidance.md` (Verification) — the canonical home for the
  verification command. Record here only a deviation active right now.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`

## Unrecorded Repo Memory

- <Important facts, decisions, invariants, verification rules, non-goals, or open
  questions that still need a durable home, or "None known".>
