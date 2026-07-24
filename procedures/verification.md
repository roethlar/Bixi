# Fresh-Eyes Verification

Purpose: prove the drafted guidance is discoverable and internally consistent
for an agent with zero context - the exact situation it exists for. Run after
drafting, before the approval summary. Required for migration runs;
recommended for substantial greenfield runs.

Scope warning: this is a discoverability and consistency check, NOT a fact
check. It proves a zero-context agent can find the answers in the rehearsal
repo; it does not prove those answers are true. A draft that confidently
repeats a false claim about an external system (CI that never runs, a deploy
target that moved) will pass questions 1-5. Claims about external systems
must be validated under the evidence rule in `procedures/bootstrap.md`, and
the approval summary must not cite this test as proof of factual
correctness.

## How (default form: throwaway-clone rehearsal)

1. Build the rehearsal clone: `git clone <target-repo> <scratch>` - a local
   clone into a throwaway directory, no network. On a legacy carve-out
   migration (a foreign `AGENTS.md` is being superseded), first rehearse
   carve-out commit 1 in the clone exactly as `procedures/bootstrap.md`
   Step 7 will run it: copy the judgment drafts to their final paths, apply
   the prepared supersession banners, delete the legacy `AGENTS.md`, and
   commit. Refresh refuses to install over a foreign `AGENTS.md`, so doing
   commit 1 first is what keeps the next step's install from raising the
   expected foreign-core FLAG. On a non-carve-out migration, just apply the
   prepared supersession banners in the clone.
2. Install the shipped set in the clone:
   `<probed-python> <toolkit>/tools/refresh.py --stage-only <scratch>`.
   This rehearses the real install - the actual `AGENTS.md`, shims, skills,
   and wrappers land at their real paths, and refresh's validation and lint
   run. Surface any FLAG line: an unexpected flag in the rehearsal is a
   bootstrap defect to resolve before the approval summary, not noise (the
   foreign-core FLAG a carve-out would otherwise raise is pre-resolved by
   commit 1 in step 1). Only the scratch clone changes; the target repo is
   untouched, so nothing changes in the target before approval.
3. Copy the judgment drafts from `.bootstrap-tmp/drafts/` to their final
   paths in the clone (on a carve-out they were already placed by commit 1
   in step 1; re-copying is idempotent).
4. Start a fresh agent context with no knowledge of this session (a subagent
   with a clean context, or a new session), working IN the clone. Do not
   summarize the migration for it - that would defeat the test.
5. Give it only this prompt:

   "Using only the files in this repo, answer: (1) What is this project?
   (2) What is true right now - active work, blockers? (3) What should
   happen next? (4) How are code changes verified before completion?
   (5) Which file would you update at the end of a work session, and how
   would you record a new durable decision? (6) For every claim in the
   guidance files about CI, deployment, or another external system, name the
   repo evidence showing the claim is currently ACTIVE rather than merely
   present as a file - for example, a workflow that sits in a path its
   provider executes and triggers on the current branch. Mark UNVERIFIED any
   claim you cannot support. Answer concisely. If any answer is not
   discoverable from the files, say MISSING and name what you needed."

6. Grade the answers yourself against the drafts. Any MISSING, wrong, or
   guessed answer is a defect in the drafts, not in the fresh agent. Treat
   every UNVERIFIED claim from question 6 as a defect too: prove it with a
   concrete query, or downgrade it in the drafts to a labeled assumption or
   local-only verification.
7. Fix the drafts, then re-run the test once with another fresh context and
   a freshly prepared clone.
8. Delete the scratch clone after grading (its staged index goes with it).
9. Record the outcome as one plain-English sentence for the approval
   summary, stating what the test covers, for example: "A fresh agent given
   only the rehearsal repo correctly answered what the project is, what is
   in progress, what comes next, and how changes are verified, and no
   external-system claim remained unverified - this checks discoverability
   and consistency, not external truth." If the second run still has
   defects, say so honestly and list them as risks in the approval summary
   instead of hiding them.

## Fallback form (only when a clone or Python genuinely is not available)

Read the drafts in place: point the fresh agent at `.bootstrap-tmp/drafts/`
"as if those files were at their final paths", with one mandatory warning in
the prompt - the drafted `.agents` content lives in the dot-named
subdirectory `.bootstrap-tmp/drafts/.agents/`, which default directory
listings HIDE; the agent must enumerate that exact path explicitly (a live
false-fail on 2026-07-09 graded an entire drafted set MISSING because of
this). The installed constitution is not inspectable in this form. The
recorded result must name which form ran.
