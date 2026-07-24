# Agent Governance Bootstrap

A personal governance toolkit for repositories maintained with LLM coding
agents. It keeps code, docs, decisions, and agent behavior aligned so future
agents do not work from stale assumptions or missing chat context.

Every governed repo gets the same two-layer setup:

- `AGENTS.md` — the portable constitution, identical bytes in every repo,
  installed and replaced whole by the toolkit (never hand-edited): prime
  invariants, universal invariants, the operator vocabulary, verification
  and git-safety rules.
- `.agents/` — everything repo-specific: `repo-guidance.md` (rules, reading
  order, the verification command), `state.md` (current work, with rotation
  to an archive), `decisions.md` (settled decisions), `push-policy.md`,
  and the operator playbooks (the shipped set is enumerated in
  `tools/shipped-set.json`, this repo's manifest).

Plus harness adapters (shims like `CLAUDE.md`/`GEMINI.md`, operator command
wrappers, and two hooks — the Claude Code compaction re-ground and the
blocking protect-governance pre-edit deny), shipped only where the mechanism
is verified to work (`docs/harness-capabilities.md`).

## Install into a new project (one command)

```sh
<path-to-this-repo>/tools/new-project <project-dir> [hint]
```

(Windows: `<path-to-this-repo>\tools\new-project.cmd <project-dir> [hint]` —
verified on macOS/Linux; the Windows launcher follows the repo's documented
Windows probe contract and is unverified live until its first Windows run.)

Creates `<project-dir>` if needed, runs `git init`, installs the governance
set, and offers to launch a detected agent harness in it — the agent asks
three short questions (what are we building, push policy, communication
level) and finishes setup with a first commit. The optional hint primes the
agent ("a markdown todo CLI") so setup opens with a confirmation. The
launcher finds a working Python itself; no interpreter knowledge needed.

## The two flows

**Bootstrap (judgment — an agent session).** Open a fresh agent session in
the target repo and paste:

```text
Read <path-to-this-repo>/procedures/bootstrap.md and follow it.
```

The agent syncs this toolkit, discovers the repo live, inventories any
existing governance (migrate / supersede / leave), drafts the repo-specific
files under a self-ignored scratch dir, and presents one plain-English
approval summary. On approval it installs everything — drafts plus the
shipped set — as ONE scoped commit. Nothing changes before you approve.

**Refresh (mechanical — one command).** From any governed repo:

```bash
py -3 <path-to-this-repo>/tools/refresh.py    # or python3 on macOS/Linux
```

(or `/update-governance` in Claude Code; codex, grok, and agy sessions get
the same entry point as the `update-governance` skill, installed under
`.agents/skills/` — verified on all three). The script syncs the toolkit,
reconciles the repo to the shipped artifact set — installs what's new,
updates stale files, removes retired ones — and makes one scoped commit
recording the toolkit version. Installed governance is toolkit-owned:
committed content that matches no shipped version is drift and is restored
(or, for retired files, removed), reported as a DRIFT line naming the
commits that introduced it; uncommitted or untracked content on touched
paths makes the run refuse and change nothing. A repo gets current the next
time you work in it; there is no registry and nothing to maintain
centrally.

## Feedback

Toolkit defects and field-earned governance rules are filed as GitHub issues
on this repo (templates under `.github/ISSUE_TEMPLATE/`; agents file only on
an explicit owner go; no secrets or PII — issues are public). Open issues
are the triage queue; closed issues are the outcome ledger.

## Requirements

- Git.
- Python 3.10+ (`tools/refresh.py`, stdlib only). On Windows prefer `py -3`;
  a bare `python3` on PATH is often the Microsoft Store stub.
- An agent harness that can read files and run commands (bootstrap only;
  refresh is plain Python).

Governed repos inherit no runtime dependency: installed guidance is Markdown
plus one JSON hook settings file.

## Layout

- `procedures/` — the bootstrap procedure and the fresh-eyes check.
- `templates/` — the AGENTS template, `.agents/` file templates, shims,
  wrappers, playbooks, the hook settings.
- `tools/refresh.py` + `tools/shipped-set.json` — the refresh mechanism and
  the manifest of what ships where.
- `docs/` — design notes, `harness-capabilities.md` (the per-harness
  verify-once record), usage, and `docs/history/` (archives).

Live repo state is tracked in [`.agents/state.md`](.agents/state.md);
settled decisions in [`.agents/decisions.md`](.agents/decisions.md). The
2026-07-08 zero-based consolidation that produced this shape is recorded in
[`docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`](docs/superpowers/plans/2026-07-08-zero-based-consolidation.md).
