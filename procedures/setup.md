# Greenfield setup

`tools/new-project.py` has installed and staged the shipped governance.
Complete setup in the current agent when one is already handling it.

Read guidance missing from context and inspect the staged scope. Use the
owner's project hint as given; ask what the project is only if missing.
Do not reconfirm a supplied answer.

Draft the four repo-owned files from their templates:
- `.agents/repo-guidance.md`: project summary, reading order, verification.
  With no code/check yet, say so instead of inventing a command.
- `.agents/state.md`: setup state and first real work item.
- `.agents/decisions.md`: settled decisions only.
- `.agents/push-policy.md`: preserve a supplied/established choice.
  If missing, ask once using the template's four options (default: ask).

Verify with `git diff --check`, then commit the shipped set and judgment
files together, staging exactly those paths. Preserve unrelated work;
never force-add ignored files. This initial commit establishes main.
Push per policy and existing authority; a new repo may have no remote.

Report setup completion and the next work item. Mention `toolkit` once
if useful; no repeated summary of every file or answered question.
