<!-- toolkit-owned; edits are drift — see AGENTS.md -->

# Playbook: defect review (`codereview`)

Review the requested change for observable defects, or verify an admitted
fix. The caller coordinates; the owner selects the reviewer. Self-review
requires the owner's explicit request, including when a transport fails.
A clean result and a supported decline are valid; never manufacture issues.

## Dispatch grammar

`/codereview <harness> <model> <effort> [<base>..<head>]`; `review` is an alias.
A range starts Change review; otherwise continue the active finding.
Ask for a missing range or finding only when context does not identify it.

Use the owner's literal model and effort. Inline overrides are session-only
unless the owner asks to save them. `frontier` selects the configured
stronger pair. Never infer model strength from its name or switch providers.

A bare `codereview` reuses an owner-designated reviewer if one exists;
otherwise ask once, with available cached dispatches as recall. A previous
dispatch is not a saved default. Save a default only when asked.
Omitted model/effort uses the selected cached pair, then the harness default
for effort; ask only for a missing model or a rejected setting.

## Deriving the reviewer incantation

Reuse verified transport facts in gitignored
`.agents/review/harnesses.local.json`. Probe only unknown or changed facts:
presence, version, headless invocation, prompt input, and model/effort flags.
Use an available verified MCP transport, otherwise CLI. For Codex CLI,
send the prompt through stdin. Do not launch a separate capability ping
when the real review can demonstrate the required reads and commands.

Cache transport flags by harness version/profile and owner-selected pairs
under `tiers.standard` and `tiers.frontier`; pairs survive upgrades.
Honor supported transport settings. A failure warrants another attempt only
after its cause changes or evidence indicates a transient failure.
A permission denial is not permission to work around the boundary.
Reuse all usable output from a failed call before deciding what is missing.

### Self-permissioning launch

Grant tools at launch: repository reads/searches, named Git inspection,
the relevant verification commands, and proof edits only in a disposable
worktree at the pinned head. The reviewer creates it when proof edits are
needed; read-only inspection needs none. Never edit the caller's worktree.

Grant no wildcard Git or shell access and no commit, push, ref-changing,
or network-mutation authority beyond that worktree's creation/removal.
Do not widen persistent settings. If a transport cannot enforce these
boundaries, report the limitation and use already-authorized alternatives.

### Dispatch provenance

Record once per review: dispatched harness/model/effort, base/head SHAs,
verdict and material evidence or limitations. Take resolved identity from
the invocation envelope, never reviewer prose; if unavailable, record
the dispatched identity and the limitation. Link this record from findings
instead of copying it into every finding and index row.

## Reviewer tiers and routing

`standard` and `frontier` retain the owner's configured pairs. Use the
requested pair; do not impose high/xhigh/max effort or a provider grade.
Sensitive paths and severity determine what needs scrutiny, not automatic
model spending. Escalate only when an unresolved material question needs
a stronger configured reviewer and existing authority covers that dispatch;
otherwise present that question to the owner.

Reuse the existing review session and prior evidence for repair deltas.
Start fresh only if the owner requests it, the transport requires it, or
the existing context demonstrably cannot support the review.
A reopen, metadata change, or added file within approved scope alone
requires neither a stronger model nor a full replay. Out-of-scope work
still requires authority.

## Verdict handling

Use every readable, valid piece of response data, whether prose, JSON,
Markdown, partial output, or a mixed envelope. Formatting, field names,
literal booleans, missing metadata, and process exit status do not invalidate
usable evidence. Infer meaning only when it is clear; never invent proof.

Never request re-emission, resubmit code, or rerun a review because output
does not match a structure. Extract or normalize locally if needed.
Compare evidence with the dispatched code pins using the existing transcript
and repository. A missing echoed SHA or capability flag needs no model call.
A conflicting SHA or ambiguous conclusion remains unresolved only to the
extent it affects the decision; retain the rest of the response.

Another model call must answer a material question still unresolved by
available evidence. Supply only that question and its necessary context.
Do not repeat an answered review or ask for cosmetic completion.
A readable result is not automatically an accepted fix: acceptance requires
evidence addressing the actual finding and requested code.

## Change review (defect generation)

Resolve `<base>..<head>` to SHAs. Supply the repository path, pins and the
bounded defect-hunt question. The reviewer reads the pinned diff from the
repository; do not duplicate it in the prompt.

Ask for a concise conclusion and any concrete findings: location, triggering
condition, predicted observable failure and impact. No output schema.
A clean review ends the pass. Findings are candidates, not fix instructions.
Do not append another review pass automatically.

## Finding intake and triage

Admit concrete, supported failures within scope. Decline duplicates, style
preferences and unsupported or out-of-scope claims with one reason in the
existing record. A finding ID and separate file are useful when it needs
ongoing work; a declined candidate needs no separate contested document.
Resolve objective questions from available evidence. Escalate substantive
disagreements requiring owner judgment without shopping for another verdict.

## Per-finding flow

Repo policy selects **one finding ↔ one commit ↔ one verdict** on main,
or a work branch. Repairs use follow-up commits, never an amend.
Keep the synchronous flow: resolve one finding before dispatching the next.
Implementation and closeout still require their existing authority.

1. Implement the admitted fix. Run the relevant verification; for a new
   regression guard, establish that it detects the reported failure.
   Record evidence once with the fix. Use a justified manual check when
   automation cannot establish the behavior.
2. Dispatch the named reviewer with the finding, pins and existing evidence.
   On main, base is the fix's parent; on a branch, its merge-base with main.
   Inspect the fix and assess whether the evidence proves closure. Repeat
   a command or revert/restore proof only to resolve a remaining material
   uncertainty; trustworthy results on unchanged code remain usable.
3. Interpret the response under Verdict handling. An accepted, reopened or
   disputed conclusion may arrive in any readable form. Missing labels or
   proof flags do not require another response.
4. Record the conclusion and remaining work in the existing finding:
   - Accepted: close direct-to-main work after required records/pushes;
     branch work follows the git playbook through merge and deletion.
   - Reopened: repair the demonstrated failure, then review only the
     unresolved repair delta using prior evidence.
   - Disputed: record the material disagreement and seek the owner's ruling
     if it cannot be settled from available evidence. No automatic third
     harness or self-review.

The reviewer may inspect adjacent regressions in the changed surface.
Full replay needs a substantive reason within authorized scope.

## Records

Use `.agents/review/findings/<id>.md` for an ongoing finding: failure and
impact, fix/commit, verification, reviewer conclusion, and pending closeout.
Omit empty sections and duplicate metadata. Existing readable records need
no migration to a format. Group a related record update with its code commit
where possible; never launch another agent to produce paperwork.

## Status index: `.agents/review/index.md`

For multiple ongoing findings, keep ID/link and status only:

- `[ ]` Open.
- `[~]` In progress.
- `[v]` Verified / awaiting merge.
- `[d]` Merged / awaiting deletion.
- `[x]` Complete: verified on main; work branch merged and deleted locally and remotely.
- `[!]` Disputed.
- `[-]` Declined.

Keep one state pointer while work remains. A single finding needs only its
state pointer; do not create a duplicate index.
