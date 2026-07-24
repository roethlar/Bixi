# Governance remediation procedure (interactive, owner-driven)

You were launched by `tools/refresh.py` as an **interactive** governance
remediation session in this repo. It found hygiene findings that need
judgment — they are listed in your kickoff prompt. The owner is present.
This session is a conversation the owner drives: **you ask, the owner
decides, you apply.** You do not remediate on your own authority, and the
session does not end until the owner ends it.

## Per-finding flow

For each finding, one at a time, present in plain English:

1. **The finding** — the file, the line, what the lint flagged, quoted.
2. **The evidence** — what the repo actually shows (does the path exist?
   was it deleted? what does git history say? is the prose still true?).
3. **The options with a recommendation** — e.g. update the reference to
   `<new path>`, mark the mention historical with a lint-allow marker,
   archive the closed decision, or something else you see. One
   recommendation with its reason.
4. **Ask how to remediate it.** Apply exactly what the owner rules —
   "yes", "no", "do the other thing", "leave it". A ruling you do not
   understand gets one clarifying question, not a guess.

Never batch the findings. Never fix ahead of a ruling.

## Scope — hard boundaries

- You may touch **governance records only**: `.agents/*.md`, governance
  `docs/`, and repo-owned files the findings name. Refresh-installed
  artifacts (playbooks, skills, wrappers, shims, hooks) are toolkit-owned:
  never edit them; a wrong reference inside one is reported to the owner,
  not fixed.
- Never touch product code, tests, or anything the findings did not name.
- If a finding needs a product change or a decision above your pay grade,
  say so and let the owner decide whether it becomes an Open Decision in
  `.agents/decisions.md`.

## When every finding has a ruling

1. Apply the rulings. Verify each fix holds (the reference resolves, the
   entry moved, the marker is on the same line).
2. Ask the owner before committing: propose ONE scoped commit of exactly
   the files you changed (never `-A`, never `-f`) with the message
   `governance remediation: <one-line summary>`, and push per the repo's
   `.agents/push-policy.md` (if it says `ask`, ask).
3. The session ends when the owner says so — not before.
