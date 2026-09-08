<!-- toolkit-owned; edits are drift — see AGENTS.md -->

# Playbook: approach review (`openreview`)

`openreview <agent>` asks the named reviewer for an unprimed judgment of a
change: code, plan, or both. The owner chooses this playbook; do not select
it automatically in place of codereview.

## Question and scope

The substantive prompt is exactly:

> From your own reading of the repository, state the goal this change serves
> and how you would achieve it. Then judge: is the change as made the best
> way to achieve that goal?

Supply only mechanical coordinates: the repository path, pinned base/head
SHAs, inspection permissions, tool/side-effect boundaries and verdict
schema. Base is the merge-base with main at dispatch. Read the pinned diff
from the shared repository; a read-only review needs no worktree.

Do not summarize the plan, propose risks or findings, supply a checklist,
repeat claimed invariants, or disclose prior reviewer conclusions. The
reviewer may discover plans and records itself. Endorsement is a valid
result; never shop for a harsher verdict.

## Dispatch

Use the codereview playbook's Dispatch grammar, Deriving the reviewer
incantation, Self-permissioning launch, Dispatch provenance, and Verdict
handling sections. They are the shared contracts; this playbook changes
the review question and result schema only.

A bare `openreview` asks which reviewer to run with machine-local cache
recall, probing nothing and storing no bare-invocation default.

Reviewer tiers and routing: always use the named harness's owner-named
frontier pair at max effort, subject to its recorded supported level.
Its owner-declared `competitive` grade is eligible. A `fallback` grade
requires explicit acceptance for this dispatch; reuse that acceptance if
already given. A model name alone grants no grade. No stronger tier exists;
contested judgments go to the owner.

## Verdict contract

```json
{"verdict":"best_approach|acceptable_with_changes|replace",
 "capability_ok":true,"reviewed_sha":"<head-sha>","base_sha":"<base-sha>",
 "goal":"<goal the reviewer discovered>",
 "recommended_approach":"<how the reviewer would achieve it>",
 "comparison":"<comparison with the reviewed change>",
 "material_changes":["<required change>"],
 "findings":[{"title":"…","evidence":"file:line — …",
  "predicted_failure":"…","severity":"CRITICAL|HIGH|MEDIUM|LOW",
  "better_approach":"…"}]}
```

- `best_approach`: `material_changes` must be empty.
- `acceptable_with_changes`: the approach stands, but
  `material_changes` must be non-empty.
- `replace`: the recommended approach should supplant the current one;
  `material_changes` must be non-empty.

`findings` is optional; an empty list is valid for every verdict.
The reviewer leads with its approach, not a defect list.

The orchestrator accepts only a successful call, a valid envelope and
schema, matching dispatched SHAs, `capability_ok` literally true, and
the verdict/list conditions above. Use codereview's extraction and
one re-emission-only retry for malformed payloads; otherwise record a
contested outcome. A parse miss never becomes acceptance.

## Record and follow through

Record the outcome with dispatch-sourced harness, resolved model, effort,
grade and base/head pins:

`openreview <agent> (<model> @ <effort>, <grade>) over <base>..<head>: <verdict>`

Include material-change titles when present. Report provenance limitations
rather than inventing resolved identity.

Design judgments go to the owner one ruling at a time. Only adopted
material changes become plan revisions or implementation work. Candidate
findings pass codereview's intake gate and per-finding flow; none is a
direct instruction to fix.

The review pass may finish here. Implementation remains pending until
the git playbook's merge and branch-deletion closeout is satisfied.
