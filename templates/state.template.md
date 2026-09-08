# Agent State

Keep only live work here; archive historical entries verbatim under
`docs/history/state-archive.md`. The `catchup` sweep performs hygiene;
`handoff` only snapshots. Use canonical pointers instead of copied counts.
Stamp volatile facts `as of <commit>`. Check push status live in git,
never store it here. Put machine facts in `.agents/machines.md`, keyed
by machine and dated.

## Now

- <Task, work branch, verified head, and stage: in progress / verified /
  awaiting merge / awaiting deletion. Completion follows the git playbook;
  do not archive work with pending integration or cleanup.>

## Next

- <Next useful action or "None recorded".>

## Blockers

- <Live blockers or "None recorded"; cite evidence for changed assumptions.>

## Verification

- See `.agents/repo-guidance.md` (Verification). Record only a currently
  active deviation here.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`

## Unrecorded Repo Memory

- <Durable facts or questions still needing a home, or "None known".>
