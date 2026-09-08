<!-- toolkit-owned; edits are drift — see AGENTS.md -->

# Playbook: approach review (`openreview`)

`openreview <agent>` asks the named reviewer for an unprimed judgment of
code, a plan, or both. Run it only when requested.

## Question and scope

Ask:

> From your own reading of the repository, state the goal this change serves
> and how you would achieve it. Then judge: is the change as made the best
> way to achieve that goal?

Supply the repository path, pinned base/head SHAs and inspection/side-effect
boundaries. Base is the merge-base with main. The reviewer reads the pinned
diff; read-only review needs no worktree. Do not prime the judgment with the
caller's rationale, suspected findings, checklist or prior verdicts.
The independent discovery is the requested purpose of this operator.

## Dispatch and result

Use only codereview's dispatch, transport, permissions, provenance and
Verdict handling sections. A bare `openreview` uses an owner-designated
reviewer or asks for the missing choice. Use the owner's model/effort;
reuse an already selected pair, without a forced max effort or grade gate.
Self-review requires the owner's explicit request.

Request a concise explanation of the goal, recommended approach, comparison
and any material changes. An endorsement is valid. No JSON schema, required
labels, empty lists or formatting retries. Apply readable evidence even when
the call reports an error; resolve only material missing information.

Record the result once with dispatch provenance. Adopted material changes
follow existing implementation authority; ask only for unsettled decisions.
Concrete defect candidates use codereview intake. Do not launch further
reviews automatically. Branch work remains pending until git closeout.
