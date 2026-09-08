# Governance bootstrap

Discover the repo and prepare usable governance without losing rules or
working integrations. Use the current agent when available. Before install
authority, write drafts only in self-ignored `.bootstrap-tmp/`; do not
change tracked target files, index, remotes or settings. An explicit
owner-only self-refresh rule still applies.

## Ground once

Use the selected toolkit clone. Sync once from its configured canonical
remote, fast-forward only; reuse a current sync result. Caveat offline or
divergent clones. If absent, clone `https://github.com/roethlar/Bixi.git`.
Reload instructions only if changed. This sync is the only toolkit write
permitted from the target session.

Confirm Git and Python 3.10+; reuse verified machine facts. Otherwise probe
`py -3`, `python3`, then `python`, rejecting Store stubs and old versions.
A target without Git needs initialization authority before installation.

## Discover and draft

Inspect tracked files, current changes, relevant entry points, verification
and active governance. Reuse prior reads; do not load historical archives
or every generated adapter. Search callers before moving a load-bearing path.

Use `templates/governance-inventory.template.md` for proposed migrations
and ownership conflicts. Group generated content; omit unchanged artifacts.
Preserve unrelated work and working integrations. Resolve contradictory
authority rather than guessing.

Draft repo-owned files under `.bootstrap-tmp/drafts/` at their final layout:
- `.agents/repo-guidance.md`: purpose, reading order, verification, remotes
  and earned rules. Check changed or uncertain claims; reuse supported facts.
- `.agents/state.md`: active work, blockers and next action. Machine facts
  belong in `.agents/machines.md`; history stays outside active state.
- `.agents/decisions.md`: settled rules and evidence not already recorded.
- `.agents/push-policy.md`: preserve the established choice; if absent,
  ask once using the template's options.

Label assumptions. Templates guide content, not mandatory empty sections.
Refresh alone installs shipped artifacts; do not draft or hand-copy them.
Prepare useful supersession pointers and check custody with
`git check-ignore`; never force-add ignored files.

## Verify and present

Use `procedures/verification.md` for relevant claims and discoverability.
Separate agents or rehearsals are not automatic. Recheck changed inputs only.

Generate the install plan without another sync:
`<python> <toolkit>/tools/refresh.py --no-sync --plan-json .bootstrap-tmp/refresh-plan.json <target>`.
For an explicitly proposed foreign AGENTS.md replacement, include `--force`
in both plan and apply. Preserve its repo-specific rules in the drafts and
its prior content in Git; no intermediate deletion commit.

Use `templates/approval-summary.template.md` for concise scope, evidence
and unsettled choices. Link exact operations instead of copying the
manifest. Identify destructive changes and custody conflicts individually.
Reuse installation authority; ask only for missing scope or decisions.
A new hash or unrelated commit is not itself grounds for reapproval.

## Install within authority

The installation go covers the presented writes, scoped commit and removal
of this task’s disposable bootstrap scratch.

Copy approved judgment drafts and supersession pointers, then run:
`<python> <toolkit>/tools/refresh.py --apply .bootstrap-tmp/refresh-plan.json --stage-only <target>`,
with `--force` for the approved legacy replacement.
Refresh validates the operation and protects uncommitted target content.
Reassess affected changes; ask again only for changed scope or a decision.

Stage exactly the approved judgment and shipped paths, including setup's
already-staged files, and commit together. Exact commit wording needs no
separate approval. Follow push policy and git closeout: branch work ends
after merge into main and local/remote deletion. No unauthorized rewrites.

Explain and authorize hook trust only when the current harness needs it.
Do not trust other harnesses or widen global settings as a side effect.

## Finish

Report the result and remaining work. Remove only task-created disposable
scratch under existing cleanup authority; preserve unrelated files.

For a confirmed toolkit defect or incident-earned portable rule, prepare
feedback only when useful. Filing to Bixi's public issues needs explicit
authority and redacted evidence. No speculative issue, empty report or
extra agent to produce paperwork.
