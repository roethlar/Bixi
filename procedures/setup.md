# Greenfield setup procedure (`new-project` agent phase)

You were launched in a brand-new repo by `tools/new-project.py`. The shipped
governance set is already installed and **staged, uncommitted**. You own the
judgment files, three setup questions, and the first commit. This is the
greenfield path — for a repo with existing governance to migrate, use
`procedures/bootstrap.md` instead.

Work plainly and briefly. The owner is not an engineer.

## Step 0 — Ground

Read `AGENTS.md` (Prime Invariants in full) and this procedure. Check what
exists: `git -C <repo> status` — the shipped set should be staged, the tree
otherwise empty or near-empty. If the kickoff prompt carried a project hint,
that is the owner's description of the project; treat it as the answer to
Step 1 and only confirm it.

## Step 1 — What is this project

- Hint given: confirm it in one sentence ("a markdown todo CLI, right?") and
  proceed on a yes.
- No hint: ask "what are we building?" in plain words. This is a conversation
  opener, not a form — one short exchange, then move on.

Record the answer as the project summary you will write into
`.agents/repo-guidance.md`. Do not interrogate for details you do not need
yet; the repo will accumulate truth as work happens.

## Step 2 — Draft the judgment files

Draft these from their templates (`templates/state.template.md`,
`templates/decisions.template.md`, `templates/repo-guidance.template.md`,
`templates/push-policy.template.md` in the toolkit) into `.agents/`, keeping
each file short:

- `.agents/repo-guidance.md` — the project summary from Step 1, the reading
  order, and a Verification section. If no verification command can exist
  yet (no code), say so explicitly ("none yet — record one once the project
  has code"); do not invent one.
- `.agents/state.md` — `## Now`: project just created by new-project, setup
  in progress. `## Next`: the first real work item from Step 1.
- `.agents/decisions.md` — the stock header; no entries yet.
- `.agents/push-policy.md` — seeded at the default; Step 3 sets its marker
  from the owner's answer.

## Step 3 — The config question

Ask it, never pre-selected (the owner's reply is the only valid source):

**Push policy** — present the four standardized options with the default
marked: 1 `always`, 2 `operators`, 3 `docs`, 4 `ask` (default). Set the
`<!-- push-policy: N -->` marker line in `.agents/push-policy.md` to the
owner's choice.

## Step 4 — One scoped commit

Commit the staged shipped set **plus** the four judgment drafts as ONE
scoped commit: `git add` exactly those paths (never `git add -A`, never
`git add -f`). Suggested message: "new-project: governance install +
judgment files (push-policy: N)". Push per the push policy
the owner just chose (default `ask`: ask once, name the remotes — a fresh
repo may have none; offer to add one, do not configure one unasked).

## Step 5 — Report

Close in plain English, bottom line first: the project is set up and
working; what you asked and what the owner chose; the first next thing to
build (from Step 1); and that `toolkit` lists what the owner can say in
this repo.
