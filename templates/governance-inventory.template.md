# Existing Governance Inventory

Every existing governance artifact gets a row. Verdicts:

- **migrate** — content moves into the standard `.agents/` layout or `AGENTS.md`.
- **supersede** — file stays, gets a banner pointing at its replacement.
- **leave** — stays untouched (e.g., append-only journals: history, not state).

When content migrates AND the old file stays behind with a banner (the most
common case), use the verdict `migrate` and write "supersede with banner" in
the Notes column. Use plain English in every cell; the owner reads this table
to approve the migration.

| Artifact | Role today | Verdict | Destination | Notes |
| --- | --- | --- | --- | --- |
| <path> | <what it does now, one phrase> | <migrate/supersede/leave> | <new path or "-"> | <anything the owner should know> |

## Supersession Banner

Applied to the top of each superseded file after approval:

> **Superseded (<YYYY-MM-DD>).** <What this file used to hold> now lives in
> `<new path>`. This file is retained as history and is no longer updated.
