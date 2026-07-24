# Agent Decisions

Record durable repo decisions here. Do not use this as a chat log. Each entry should make
sense without conversation history and should name superseded guidance when relevant.

Keep this file to what is currently in force or still open. When a decision is
closed - superseded, or settled and retained only as the rationale for a rule that
now lives in its canonical home elsewhere - move it verbatim, in that same change,
to an archive under `docs/history/` (for example `docs/history/decisions-archive.md`);
never summarize or drop wording, the exact text is the record. Keep a single
pointer to the archive at the top of this file, not a stub per entry. The archive
is the provenance log; this file is what is in force or still open.

## Decision lifecycle

A decision moves through these states:

- **Open** - a finding has been assessed but not yet acted on. It lives in the
  `## Open Decisions` queue below, with the verified evidence, the options, and a
  standing recommendation. The process is unchanged until it is adopted; an agent
  records it rather than implementing on the spot.
- **Active** - a decision that is in force now.
- **Adopted YYYY-MM-DD** - an Open finding that has been acted on: its rule now
  lives in its canonical home (a procedure, template, or invariant). Note where the
  rule landed; the finding is retained in place as the rationale that led to it,
  until it is archived.
- **Superseded** - replaced by a later decision; name the replacement.

When an entry becomes purely historical rationale - Adopted or Superseded, with the
live rule now owned elsewhere - archive it per the rule above: move it verbatim to
`docs/history/`, do not leave a stub.

## Decisions

<!--
### YYYY-MM-DD - <Decision title>

Status: Active | Adopted YYYY-MM-DD | Superseded

Decision:
<What was decided.>

Reason:
<Why this is the durable rule or direction.>

Supersedes:
<Optional prior decision, doc, or rule.>
-->

## Open Decisions (deferred - not yet adopted)

Assessed findings the owner chose to record as a future decision rather than
implement now. The process is unchanged until one is adopted. Each states its
verified evidence, the options, and a standing recommendation. When one is adopted,
flip its status to `Adopted YYYY-MM-DD`, note where the rule now lives, and keep the
finding here as the rationale until it is archived.

<!--
### YYYY-MM-DD - <Finding title>

Status: Open (deferred; no change made) | Adopted YYYY-MM-DD

Finding:
<What was observed, in durable wording.>

Evidence:
<The exact queries, file:line cites, or facts that prove the finding is currently true.>

Options:
<The candidate end states, including a "Leave" option.>

Recommendation:
<The standing recommendation and its scope (product vs. this repo's own governance).>
-->
