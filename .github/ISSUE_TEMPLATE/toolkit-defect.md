---
name: Toolkit defect
about: A confirmed defect in the toolkit's code or procedures, found while using it
labels: bug
---

<!-- Discipline (read before writing anything):

- File only for a defect PROVEN with a citable command or observation. A
  suspected-but-unverified problem is an assumption: verify it first or leave
  it out. An unproven or padded report wastes triage and erodes trust.
- A defect in the product, not a record of your own mistake in a run. If the
  procedure or code did the right thing and you misread it, there is no bug.
- One defect per issue.
- REDACTION: issues are public. No secrets, tokens, credentials, private
  hostnames/IPs, or personal data. Cite evidence by repo-relative path and
  commit hash, never by pasting sensitive content.
- Agents: file only on an explicit owner go. -->

- **Source:** <two commits — the repo you were running in @ its HEAD, and the toolkit @ the commit its governance came from (recoverable from that repo's last governance-refresh commit message) — e.g. `SomeRepo @ abc1234, toolkit @ def5678`>
- **Severity:** <low / medium / high, with one clause on impact>
- **Summary:** <one or two plain-English sentences — what breaks, and the consequence>
- **Root cause:** <file/section and mechanism — why it misbehaves>
- **Evidence:** <the exact command and output that proves the defect is currently active>
- **Why it slipped through:** <which test, guard, or review should have caught it — omit if n/a>
- **Proposed fix:** <one or two sentences + the bite proof that would confirm it, or "none yet">
- **Affected files:** <paths a fix would touch>
