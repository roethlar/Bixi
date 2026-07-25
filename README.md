# Bixi

> **Bixi** (赑屃) is the dragon-turtle of Chinese myth, who carries stone
> steles — durable inscriptions — on his back for eternity.

Bixi carries the durable record for a repository worked on by LLM coding
agents, so nothing drifts.

## The problem

Agent sessions are amnesiac. Every new session starts cold, and the things
that should govern it — why this repo does things this way, what was already
decided, what must never happen again — live in chat logs the next session
will never see. So the truth drifts: docs disagree with code, decisions get
relitigated, and rules earned from a real incident quietly stop applying.

Bixi puts that record in the repository, in a fixed place, in a form the next
agent reads before it touches anything.

## What lands in your repo

- **`AGENTS.md`** — the portable constitution. Identical bytes in every
  governed repo: prime invariants, the operator vocabulary, verification and
  git-safety rules. Installed and replaced whole; never hand-edited.
- **`.agents/`** — everything specific to *your* repo: the rules and
  verification command, current state, settled decisions with the evidence
  behind them, the push policy, and the operator playbooks.
- **Harness adapters** — a `CLAUDE.md` shim, command wrappers, and two hooks
  (a compaction re-ground and a blocking pre-edit deny that protects the
  governance files). Shipped only where the mechanism is verified to work on
  that harness, never on assumption.

Governed repos inherit no runtime dependency: it's Markdown plus one JSON
settings file.

## Start a new project

```sh
<path-to-bixi>/tools/new-project <project-dir> [hint]
```

Windows: `<path-to-bixi>\tools\new-project.cmd <project-dir> [hint]`

Creates the directory, runs `git init`, installs the governance set, and
offers to launch an agent harness it detects to finish setup — it asks what
you're building and how you want pushes handled, then makes the first commit.
The optional hint ("a markdown todo CLI") means setup opens with a
confirmation instead of an interrogation. The launcher finds a working Python
itself.

## Adopt an existing repo

Open an agent session in that repo and paste:

```text
Read <path-to-bixi>/procedures/bootstrap.md and follow it.
```

The agent discovers the repo live, inventories any governance it already has
(migrate, supersede, or leave — each with a reason), drafts the repo-specific
files in a scratch directory, and shows you one plain-English approval
summary. Nothing changes until you approve; on approval everything lands as
one commit.

## Keep a repo current

From any governed repo:

```bash
python3 <path-to-bixi>/tools/refresh.py    # py -3 on Windows
```

It reconciles the repo to the shipped set: installs what's new, updates what's
stale, removes what's retired, and makes one commit recording the toolkit
version. Governance files are toolkit-owned, so committed content matching no
shipped version is drift — reported with the commits that introduced it, and
restored. Uncommitted work on any path it would touch makes the run refuse and
change nothing.

There's no registry and nothing to maintain centrally. A repo catches up the
next time you work in it.

## Requirements

- Git.
- Python 3.10+ (standard library only). On Windows prefer `py -3`; a bare
  `python3` is often the Microsoft Store stub.
- An agent harness that can read files and run commands — for setup and
  adoption only. Refreshing is plain Python.

## Development

Bixi is the released toolkit. It's developed in
[AgentGovernanceBootstrap](https://github.com/roethlar/AgentGovernanceBootstrap),
where the design notes, the per-harness verification record, and the full
decision log live. File issues
[there](https://github.com/roethlar/AgentGovernanceBootstrap/issues).
