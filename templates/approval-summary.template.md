# Bootstrap Approval Summary

<Altitude: everything above the Existing Governance Inventory must fit on one
screen - short paragraphs, no exhaustive detail; the inventory is the only
section that may run long. For migration runs, include the inventory inline;
never just point at another file.>

## Recommendation

Start with exactly one of these:

- Approve
- Approve after edits
- Do not approve yet

Then add one sentence explaining why.

<While any open question still requires an owner decision - an unresolved
custody conflict, an ignore-rule question, a scope choice - the recommendation
must not be `Approve`. Use `Do not approve yet` or `Approve after edits` until
the owner has settled it.>

## What The Repo Appears To Be

<Plain-English summary of the repo based on evidence read directly from the repo.>

## Proposed Durable Guidance

<Short summary of what would be written and how it keeps code, docs, decisions,
verification, and future agent behavior aligned.>

## Verification Default

<State this run's verification concretely: the automated command(s) run and their result,
or — for a docs-only change exempt under the verification default (see the AGENTS
Verification section) — that it was exempt and why. Give the applied outcome for this run,
not a copy of the generic rule's conditions; do not ask the human to approve this normal
default.>

## Assumptions

<List inferred but unverified facts, or "None". Do not state assumptions as facts in the
draft guidance unless the human approves them. Do not turn normal verification hygiene into
a human approval question.>

## Files Proposed For Approval

<Sort every proposed file into the two lists below using `git check-ignore`
on its final path - never by assumption. A path the repo gitignores cannot
enter the commit and must not be listed as committed.>

### Committed — judgment drafts (copied from `.bootstrap-tmp/drafts/` on approval)

- `.agents/repo-guidance.md`
- `.agents/state.md`
- `.agents/decisions.md`
- `.agents/push-policy.md`
- <migration runs: supersession banners on superseded files>

### Committed — shipped set (installed by `tools/refresh.py --stage-only`)

<List what the refresh script will install here, rendered from the
`--plan-json` record this run generated (`AGENTS.md`, harness shims,
operator wrappers, playbooks, hook settings) — never reconstructed by hand.
These files are never drafted or hand-copied; the script is their single
installer, and Step 7 applies exactly this record.>

### Local-only (gitignored, copied but never committed)

<Files whose final paths an ignore rule covers. The refresh script repairs a
known blanket harness-dir ignore itself; anything else it flags. Write
"None" when the list is empty. If keeping one of these tracked seems
important, raise the ignore rule as a question instead; never plan a silent
`git add -f`.>

<State the exact commit message that will be used. Approving this summary
authorizes copying the judgment drafts, running the refresh install, and
making ONE scoped commit covering both groups (exactly the lists above,
never `git add -A`, never `git add -f`). Nothing is pushed yet; the push
policy written by this run governs all subsequent commits.>

<Legacy carve-out runs (a foreign `AGENTS.md` is being superseded): state
BOTH exact commit messages instead — commit 1, the carve-out (judgment
drafts + supersession banners + the legacy file's deletion); commit 2, the
refresh install's own commit. Approving this summary authorizes exactly
those two commits, in that order, and nothing else. Git is a hard
requirement settled at Step 1; a target without git never reaches this
summary.>

## Push Policy

Push policy will be set to: **4 — ask** (default).

To change it, reply with a number when you approve:

  1 — always: Always push after every commit.
  2 — operators: Push automatically after operator-invoked commits (handoff, decision, drift, plan); ask for all others.
  3 — docs: Push automatically after docs/state-only commits; ask for code or tool changes.
  4 — ask: Always ask before pushing. (default)

<Do NOT pre-select or infer the option from prior decisions, context, or the decisions log. Write the default (4) here and wait for the owner's answer at approval time. The owner's reply to the approval question is the only valid source for this choice.>

## Risks, Limitations, Or Open Questions

<List unresolved questions, inferred facts, stale evidence, unread areas, or decisions
that still need human approval. Questions should be answerable as owner intent, scope, or
risk tolerance, not require code expertise. Label each item Low, Medium, or High risk for
approving the proposed durable guidance. Use "None identified" only when that is true.>

## Repo Memory Check

<State whether any important repo-specific facts, decisions, invariants, verification
rules, non-goals, or open questions remain unrecorded.>

## Existing Governance Inventory

<Migration runs only. Include the completed inventory table from
`governance-inventory.template.md`: every existing governance artifact, its role,
its verdict (migrate / supersede / leave), and its destination, in plain
English. For greenfield runs write "Not applicable - no existing governance.">

## Fresh-Eyes Verification

<One plain-English sentence reporting the result of the fresh-eyes catchup
test, stating what it covers - discoverability and internal consistency, not
external truth. For example: "A fresh agent given only the drafted files
correctly answered all six questions in the verification procedure; this
checks that the guidance is findable and consistent, not that external
claims are true." Never present this test as proof that CI or deployment
claims are correct. If issues were found and fixed, say so. Required for
migration runs; if skipped on a greenfield run, say "Not run (greenfield).">
