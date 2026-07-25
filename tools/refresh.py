#!/usr/bin/env python3
"""Reconcile a governed repo to the toolkit's shipped artifact set.

Pull-based, per-repo, no registry: run it while standing in (or pointing it
at) a governed repo. It syncs the local toolkit clone from its canonical
remote, then reconciles the target repo to tools/shipped-set.json:

  - replace-whole   (AGENTS.md): current or formerly-shipped versions update
                    normally. Divergent content forks on git evidence: if any
                    committed version of the file ever matched a shipped hash
                    the repo was governed, so the divergence is drift and the
                    file is RESTORED to current (reported with the commits
                    that introduced it); if no committed version ever matched,
                    it is a foreign governance file - flagged, never
                    overwritten, a migration rather than a refresh.
  - replace:        missing -> install; matches a formerly-shipped version ->
                    update to current; anything else -> drift: reported with
                    its introducing commits and RESTORED to current.
  - retired:        formerly-shipped paths are removed. Content matching no
                    shipped version is drift and is removed with a report.

Installed governance is toolkit-owned (owner ruling 2026-07-16): no
out-of-band edit to an installed artifact is legitimate, whoever made it, so
divergence is always drift and every run converges the repo to exactly the
shipped set. Nothing uncommitted is ever machine-destroyed: restores and
removes are touched paths, so the dirty-tree refusal fires first; committed
drift stays recoverable from git history.

Matching is newline-equivalent: CRLF normalizes to LF, and content differing
only by at most one trailing final newline matches - a file touched by
insert-final-newline tooling is not a divergence (issue #1).

Repo-owned files (.agents/state.md, decisions.md, repo-guidance.md,
push-policy.md, machines.md, plans, review trails,
archives) are never touched by reconcile — refresh's own mechanical
repairs (recorded push-status lines, git-proven moved references,
closed-decision archiving) are the only exception. The manifest's seeded[]
section is the one creation exception: the policy files that installed
artifacts reference unconditionally are written from their templates when
absent (a repo governed before they existed), reported with an ACTION line,
and never read or compared again once they exist.

Committability follows the recorded custody rules: git check-ignore per
target path; a blanket harness-adapter-dir ignore (.claude/ etc.) gets the
established narrow repair with the .gitignore edit included in the same
commit; a path ignored by an unrecognized rule is flagged and skipped;
git add -f is never used.

Default mode stages the reconciled paths and makes one scoped commit whose
message records the toolkit commit it synced to. --stage-only stages and
stops (the bootstrap procedure then stages the approved judgment drafts and
makes the single scoped commit covering both groups). Neither mode pushes.

Exit codes:
  0  converged, or a read-only plan/preview - nothing left to reconcile
  2  usage error, or the target/toolkit is not a usable git repository
  3  refused: uncommitted changes on a path the run would touch
  4  refused: manifest failed validation, an unsafe destination, an approved
     plan that no longer matches, or an apply that did not land cleanly
  5  applied, but a core (replace-whole) governance file was flagged foreign
     and left unreplaced - the repo is not converged; run bootstrap. Distinct
     from 0 so a script can tell an ungoverned repo from a converged one.

Python 3.10+, stdlib only.
"""

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANONICAL_URLS = [
    # Order matters: the clone's own origin is tried first (a product clone
    # syncs from its product home, the dev clone from its home); the public
    # product repo is the canonical fallback, then the dev remote and the
    # LAN gitea mirror. (Mirror-first would fast-forward to a lagging mirror
    # head and silently run a stale toolkit.) Offline -> proceed on the
    # local copy with a flag.
    "https://github.com/roethlar/Bixi.git",
    "https://github.com/roethlar/AgentGovernanceBootstrap.git",
    "http://q:3000/michael/AgentGovernanceBootstrap.git",
]


def sync_urls(toolkit: Path) -> "list[str]":
    """Sync candidates for the toolkit clone: its own origin first, then the
    canonical list (deduped, order preserved). The clone's origin is how a
    product clone finds its product home (2026-07-24 packaging)."""
    urls = []
    origin = git(toolkit, "remote", "get-url", "origin", check=False)
    if origin.returncode == 0 and origin.stdout.strip():
        urls.append(origin.stdout.strip())
    for url in CANONICAL_URLS:
        if url not in urls:
            urls.append(url)
    return urls

ADAPTER_DIRS = (".claude", ".codex", ".gemini", ".grok")


def norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _stem(data: bytes) -> bytes:
    """Equivalence stem: normalized bytes minus at most one trailing newline."""
    n = norm(data)
    return n[:-1] if n.endswith(b"\n") else n


def candidate_hashes(data: bytes) -> "set[str]":
    """The nhash values every byte-form equivalent to `data` can have
    recorded: the stem itself and the stem plus one final newline."""
    stem = _stem(data)
    return {hashlib.sha256(stem).hexdigest(),
            hashlib.sha256(stem + b"\n").hexdigest()}


def nhash(data: bytes) -> str:
    """The maintenance-rule hash: shipped-set.json formerly[] entries are
    nhash of the outgoing source bytes (see the manifest comment)."""
    return hashlib.sha256(norm(data)).hexdigest()


def git(repo: Path, *args: str, check: bool = True) -> "subprocess.CompletedProcess[str]":
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            "git {} failed in {}: {}".format(" ".join(args), repo, proc.stderr.strip())
        )
    return proc


def worktree_root_error(path: Path) -> "str | None":
    """Non-None reason when `path` is not the root of a git working tree.
    Bare repos and nested subdirectories are refused before any mutation —
    a nested install would govern a subtree and leave the root bare."""
    inside = git(path, "rev-parse", "--is-inside-work-tree", check=False)
    if inside.returncode != 0:
        return "not a git repository"
    if inside.stdout.strip() != "true":
        return "a bare repository (no working tree)"
    top = git(path, "rev-parse", "--show-toplevel", check=False)
    if top.returncode != 0 or not top.stdout.strip():
        return "missing a resolvable working-tree root"
    if Path(top.stdout.strip()).resolve() != path:
        return "not the working-tree root (that is {})".format(top.stdout.strip())
    return None


def sync_toolkit(toolkit: Path) -> str:
    """Fast-forward the toolkit clone from a canonical remote. Never blocks:
    offline or diverged -> proceed on the local copy, returning a flag note."""
    for url in sync_urls(toolkit):
        live = git(toolkit, "ls-remote", "--exit-code", url, "HEAD", check=False)
        if live.returncode != 0:
            continue
        fetched = git(toolkit, "fetch", url, check=False)
        if fetched.returncode != 0:
            continue
        ff = git(toolkit, "merge", "--ff-only", "FETCH_HEAD", check=False)
        if ff.returncode != 0:
            return "toolkit clone has local work not on {} (no fast-forward); proceeding on the local copy".format(url)
        return ""
    return "no canonical remote reachable; proceeding on the local toolkit copy (may be stale)"


def maybe_reexec(head_before: str, head_after: str, environ=None, execv_fn=None,
                 script_argv=None) -> bool:
    """After a sync fast-forward, run the freshly synced runner exactly once:
    re-exec with --no-sync under a loop-guard marker, so a new manifest is
    never read by an old in-memory runner. Returns False when no re-exec is
    needed; a real re-exec never returns (fakes do, for tests)."""
    environ = os.environ if environ is None else environ
    if head_after == head_before or environ.get("AGB_REFRESH_REEXEC"):
        return False
    environ["AGB_REFRESH_REEXEC"] = "1"
    argv = [sys.executable, str(Path(__file__).resolve())]
    argv += list(sys.argv[1:] if script_argv is None else script_argv)
    if "--no-sync" not in argv:
        argv.append("--no-sync")
    (os.execv if execv_fn is None else execv_fn)(sys.executable, argv)
    return True


def load_shipped_set(toolkit: Path) -> dict:
    return json.loads((toolkit / "tools" / "shipped-set.json").read_text(encoding="utf-8"))


_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_KNOWN_CLASSES = ("replace-whole", "replace")


def validate_manifest(shipped: dict, toolkit: Path) -> "list[str]":
    """Structural safety checks before any read or write: the manifest is
    trusted input only after these hold. Relative paths only, no upward
    traversal, unique targets, known classes, well-formed hashes,
    existing sources."""
    errors = []
    seen = set()
    if shipped.get("schema") != 1:
        errors.append("unsupported or missing manifest schema (expected 1, got {!r})".format(shipped.get("schema")))

    def check_rel(kind, rel):
        p = Path(rel)
        if not rel or p.is_absolute() or rel.startswith(("/", "\\")):
            errors.append("{} path is absolute or empty: {!r}".format(kind, rel))
        elif ".." in p.parts:
            errors.append("{} path traverses upward: {}".format(kind, rel))

    for art in shipped.get("artifacts", []):
        tgt = art.get("target", "")
        check_rel("source", art.get("source", ""))
        check_rel("target", tgt)
        if tgt in seen:
            errors.append("duplicate target: {}".format(tgt))
        seen.add(tgt)
        if art.get("class") not in _KNOWN_CLASSES:
            errors.append("unknown class {!r} for {}".format(art.get("class"), tgt))
        elif not (toolkit / art.get("source", "")).is_file():
            errors.append("missing source file: {}".format(art.get("source")))
        for h in art.get("formerly", []):
            if not _HEX64.match(h):
                errors.append("malformed hash for {}: {!r}".format(tgt, h))
    for ret in shipped.get("retired", []):
        rt = ret.get("target", "")
        check_rel("retired target", rt)
        if rt in seen:
            # A target in both artifacts and retired would be installed
            # (write) and then removed (unlink) in the same run, committing a
            # fleet-wide deletion of a shipped file. Fold retired targets into
            # the same duplicate-set as the artifacts above so the overlap
            # exits before any write.
            errors.append("target listed in both artifacts and retired: {}".format(rt))
        seen.add(rt)
        for h in ret.get("formerly", []):
            if not _HEX64.match(h):
                errors.append("malformed hash for retired {}: {!r}".format(rt, h))
    for sd in shipped.get("seeded", []):
        st = sd.get("target", "")
        check_rel("seeded source", sd.get("source", ""))
        check_rel("seeded target", st)
        if st in seen:
            # Same duplicate-set as artifacts and retired: a seeded target
            # that is also shipped or retired would be written once as a
            # never-touched-again file and then reconciled or unlinked in the
            # same run. Exit before the first write.
            errors.append("target listed in both seeded and artifacts/retired: {}".format(st))
        seen.add(st)
        if not (toolkit / sd.get("source", "")).is_file():
            errors.append("missing seeded source file: {}".format(sd.get("source")))
    return errors


def assert_safe_dest(target_repo: Path, rel: str) -> None:
    """Refuse a destination whose existing components include a symlink or
    whose resolved parent escapes the repository root. The never-overwrite
    promise depends on writes landing exactly where the manifest names."""
    probe = target_repo
    for part in Path(rel).parts:
        probe = probe / part
        if probe.is_symlink():
            raise RuntimeError(
                "{}: {} is a symlink; refusing to write through it".format(rel, probe))
        if not probe.exists():
            break
    root = target_repo.resolve()
    resolved_parent = (target_repo / rel).parent.resolve()
    if resolved_parent != root and root not in resolved_parent.parents:
        raise RuntimeError("{}: resolves outside the repository root".format(rel))


def write_atomic(dest: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(dest.parent), prefix=".refresh-tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, str(dest))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class Plan:
    def __init__(self) -> None:
        self.install = []   # (target, source_path)
        self.update = []    # (target, source_path)
        self.restore = []   # (target, source_path) - diverged, converged back
        self.remove = []    # target
        self.current = []   # target
        self.flags = []     # (target, reason)
        self.drift = {}     # target -> introducing-commit provenance line
        self.gitignore_repairs = []  # (line_no, old_line, new_lines)
        self.repairs = []   # (target, note) - mechanical fixes outside the shipped set
        self.seeded = []    # target - installed because it was absent (seeded[])


# Push-status lines are never recorded in state files (2026-07-11 ruling):
# git owns that fact, so any recorded line is deleted on sight. Narrow,
# high-precision patterns only — "push policy" lines are repo settings and
# must survive.
PUSH_STATUS_RE = re.compile(
    r"unpushed|push[ -]status|push[ -]state|not yet pushed|pending push",
    re.IGNORECASE)


def _moved_target(target_repo, tok, _cache={}):
    """The single rename target for a missing path, proven by git history,
    or None. Mechanical only: zero or ambiguous targets stay judgment.
    (No pathspec: rename records are keyed by the NEW path, so filtering by
    the old one hides them.)"""
    key = str(target_repo)
    if key not in _cache:
        proc = git(target_repo, "log", "--diff-filter=R", "--find-renames",
                   "--name-status", "--format=", check=False)
        pairs = {}
        for line in proc.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].startswith("R"):
                pairs.setdefault(parts[1], set()).add(parts[2])
        _cache[key] = pairs
    targets = _cache[key].get(tok.rstrip("/"), set())
    if len(targets) == 1:
        t = next(iter(targets))
        if (target_repo / t).exists():
            return t
    return None


def repair_moved_references(target_repo: Path, plan: Plan) -> None:
    """Mechanical lint repair (2026-07-23 owner-surface D3): a backticked
    reference whose file MOVED — git history proves exactly one rename
    target — is rewritten in place and joins the refresh commit. Lines
    carrying a deliberate lint: allow marker are untouched, and dirty files
    are never folded into a refresh commit."""
    agents_dir = target_repo / ".agents"
    if not agents_dir.is_dir():
        return
    for f in sorted(agents_dir.glob("*.md")):
        rel = f.relative_to(target_repo).as_posix()
        dirty = git(target_repo, "status", "--porcelain", "--", rel,
                    check=False).stdout.strip()
        if dirty:
            continue
        changed_lines = 0
        out_lines = []
        for line in f.read_text(encoding="utf-8").splitlines():
            if "lint: allow" in line:
                out_lines.append(line)
                continue
            for m in PATH_TOKEN.finditer(line):
                tok = m.group(1)
                if (not _lintable_repo_path(tok)
                        or tok.rstrip("/") in LINT_EXEMPT_PATHS
                        or (target_repo / tok.rstrip("/")).exists()):
                    continue
                moved = _moved_target(target_repo, tok)
                if moved:
                    line = line.replace("`" + tok + "`", "`" + moved + "`")
                    changed_lines += 1
            out_lines.append(line)
        if changed_lines:
            write_atomic(f, ("\n".join(out_lines) + "\n").encode("utf-8"))
            plan.repairs.append((rel, "rewrote {} moved reference(s) "
                                      "(rename proven by git history)".format(changed_lines)))


def repair_closed_decisions(target_repo: Path, plan: Plan) -> None:
    """Mechanical lint repair (2026-07-23 owner-surface D3): decisions.md
    entries with Status Adopted/Superseded move verbatim to
    docs/history/decisions-archive.md with a dated pointer — the lifecycle
    rule is deterministic. Dirty files are never folded in."""
    import datetime
    decisions = target_repo / ".agents" / "decisions.md"
    archive = target_repo / "docs" / "history" / "decisions-archive.md"
    if not decisions.exists():
        return
    for f in (decisions, archive):
        rel = f.relative_to(target_repo).as_posix()
        dirty = git(target_repo, "status", "--porcelain", "--", rel,
                    check=False).stdout.strip()
        if dirty:
            return
    text = decisions.read_text(encoding="utf-8")
    entries = list(re.finditer(r"^### (.+)$", text, re.M))
    blocks = []  # (start, end) of closed entries, in document order
    for i, em in enumerate(entries):
        end = entries[i + 1].start() if i + 1 < len(entries) else len(text)
        seg_end = end
        m2 = re.search(r"^## ", text[em.end():end], re.M)
        if m2:
            seg_end = em.end() + m2.start()
        seg = text[em.start():seg_end]
        sm = re.search(r"^Status:\s*(\w+)", seg, re.M)
        if sm and sm.group(1) in ("Adopted", "Superseded"):
            blocks.append((em.start(), seg_end))
    if not blocks:
        return
    moved = []
    for start, end in blocks:
        moved.append(text[start:end].strip("\n"))
    kept = text[:blocks[0][0]]
    for i in range(len(blocks) - 1):
        kept += text[blocks[i][1]:blocks[i + 1][0]]
    kept += text[blocks[-1][1]:]
    kept = re.sub(r"\n{3,}", "\n\n", kept)
    today = datetime.date.today().isoformat()
    addition = "\n\n" + "\n\n".join(
        m + "\n\n> Archived {} (refresh auto-archive): the entry carried a "
        "closed status; the lifecycle rule moves closed entries here "
        "verbatim.".format(today) for m in moved) + "\n"
    archive.parent.mkdir(parents=True, exist_ok=True)
    prior = (archive.read_text(encoding="utf-8")
             if archive.exists() else "# Agent Decisions — Archive\n")
    if not prior.endswith("\n"):
        prior += "\n"
    write_atomic(archive, (prior + addition).encode("utf-8"))
    write_atomic(decisions, kept.encode("utf-8"))
    plan.repairs.append((".agents/decisions.md",
                         "auto-archived {} closed decision entr{} verbatim".format(
                             len(moved), "y" if len(moved) == 1 else "ies")))
    plan.repairs.append(("docs/history/decisions-archive.md",
                         "received {} archived entr{}".format(
                             len(moved), "y" if len(moved) == 1 else "ies")))


def repair_push_status_lines(target_repo: Path, plan: Plan) -> None:
    """Mechanical repair (2026-07-23 owner-surface D3): delete recorded
    push-status lines from .agents/state.md in the run, never report them.
    The repair joins the refresh commit like any planned change."""
    state = target_repo / ".agents" / "state.md"
    if not state.exists():
        return
    dirty = git(target_repo, "status", "--porcelain", "--", ".agents/state.md",
                check=False).stdout.strip()
    if dirty:
        # Never fold the owner's uncommitted edits into a refresh commit.
        return
    lines = state.read_text(encoding="utf-8").splitlines()
    kept = [ln for ln in lines if not PUSH_STATUS_RE.search(ln)]
    dropped = len(lines) - len(kept)
    if not dropped:
        return
    write_atomic(state, ("\n".join(kept) + "\n").encode("utf-8"))
    plan.repairs.append((".agents/state.md",
                         "deleted {} recorded push-status line(s) — git owns "
                         "that fact (2026-07-11)".format(dropped)))


def _drift_provenance(target_repo: Path, rel: str) -> str:
    """The last few commits that touched a diverged path - the audit trail
    that lets the owner see who introduced the drift without digging."""
    proc = git(target_repo, "log", "-3", "--format=%h %s", "--", rel, check=False)
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()] \
        if proc.returncode == 0 else []
    return " | ".join(lines) if lines else "no commit history for this path"


def _ever_shipped(target_repo: Path, rel: str, known: "set[str]") -> bool:
    """True when any committed historical version of `rel` matches a known
    shipped hash - evidence the repo was governed, so a present-day mismatch
    is drift to restore, not a foreign file to protect. Runs only when a
    replace-whole target diverges; blobs are read once each."""
    proc = git(target_repo, "log", "--format=%H", "--", rel, check=False)
    if proc.returncode != 0:
        return False
    seen = set()
    for commit in proc.stdout.split():
        blob = git(target_repo, "rev-parse", "{}:{}".format(commit, rel), check=False)
        oid = blob.stdout.strip()
        if blob.returncode != 0 or not oid or oid in seen:
            continue
        seen.add(oid)
        data = subprocess.run(["git", "-C", str(target_repo), "cat-file", "blob", oid],
                              capture_output=True)
        if data.returncode == 0 and candidate_hashes(data.stdout) & known:
            return True
    return False


def classify(target_repo: Path, toolkit: Path, shipped: dict) -> Plan:
    plan = Plan()
    for art in shipped["artifacts"]:
        src = toolkit / art["source"]
        src_bytes = src.read_bytes()
        tgt = target_repo / art["target"]
        if not tgt.exists():
            plan.install.append((art["target"], src))
            continue
        tgt_bytes = tgt.read_bytes()
        if _stem(tgt_bytes) == _stem(src_bytes):
            plan.current.append(art["target"])
        elif (candidate_hashes(tgt_bytes) & set(art.get("formerly", []))
              and not candidate_hashes(tgt_bytes) & candidate_hashes(src_bytes)):
            # A historical hash never widens the current equivalence
            # boundary: when the current source's own hash sits in
            # formerly[], a file within one newline of current-but-not-
            # stem-equal is drift to restore, never a silent update (M1).
            plan.update.append((art["target"], src))
        elif art["class"] == "replace-whole" and not _ever_shipped(
                target_repo, art["target"],
                set(art.get("formerly", [])) | candidate_hashes(src_bytes)):
            plan.flags.append((
                art["target"],
                "matches no known template version and no committed version ever "
                "did - a foreign governance file; refusing to replace (re-run with "
                "--force to replace anyway - git history preserves the old content - "
                "or run the bootstrap procedure to migrate its content).",
            ))
        else:
            plan.restore.append((art["target"], src))
            plan.drift[art["target"]] = _drift_provenance(target_repo, art["target"])
    # Seeded files are repo-owned, not shipped: installed artifacts reference
    # them unconditionally (AGENTS.md's push policy and communication level),
    # but only the bootstrap procedure ever creates them, so a repo governed
    # before they existed carries pointers to nothing. Backfill an absent one
    # at its documented default; a present one is invisible here - never
    # hashed, updated, restored, removed, or counted as current, so owner
    # edits stay owner-owned (owner ruling 2026-07-25).
    for sd in shipped.get("seeded", []):
        if (target_repo / sd["target"]).exists():
            continue
        plan.install.append((sd["target"], toolkit / sd["source"]))
        plan.seeded.append(sd["target"])
    for ret in shipped.get("retired", []):
        tgt = target_repo / ret["target"]
        if not tgt.exists():
            continue
        if not candidate_hashes(tgt.read_bytes()) & set(ret.get("formerly", [])):
            plan.drift[ret["target"]] = _drift_provenance(target_repo, ret["target"])
        plan.remove.append(ret["target"])
    return plan


def check_committability(target_repo: Path, plan: Plan, shipped: dict) -> None:
    """check-ignore each path we would add; repair known blanket adapter-dir
    ignores in the repo's root .gitignore; flag-and-skip anything else."""
    paths = [t for t, _ in plan.install + plan.update + plan.restore]
    exclusions = shipped.get("machine_local_exclusions", {})
    gitignore = target_repo / ".gitignore"
    for path in list(paths):
        probe = git(target_repo, "check-ignore", "--verbose", "--", path, check=False)
        if probe.returncode != 0:
            continue  # not ignored
        # format: <source>:<linenum>:<pattern>\t<path>
        head = probe.stdout.strip().split("\t")[0]
        source, lineno, pattern = head.rsplit(":", 2)
        pat = pattern.strip().strip("/")
        if source == ".gitignore" and pat in ADAPTER_DIRS:
            repl = exclusions.get(pat, [])
            plan.gitignore_repairs.append((int(lineno), pattern, repl))
        else:
            for lst in (plan.install, plan.update, plan.restore):
                lst[:] = [(t, s) for t, s in lst if t != path]
            # plan.seeded drives the counts, the commit summary and the ACTION
            # line, so a skipped seed left there reports a file that was never
            # written.
            plan.seeded[:] = [t for t in plan.seeded if t != path]
            plan.flags.append((path, "ignored by '{}' ({}:{}) - unrecognized rule; skipped, never force-added".format(pattern, source, lineno)))
    # dedupe repairs (several paths may hit the same blanket line)
    plan.gitignore_repairs = sorted(set(
        (ln, old, tuple(new)) for ln, old, new in plan.gitignore_repairs
    ))


PATH_TOKEN = re.compile(r"`([^`\s]+)`")

# The toolkit's own designated create-on-first-use homes: the template and
# the decisions header name these before a repo's first rotation creates
# them, so their absence is expected in every fresh repo, not a dead
# reference (field finding, 2026-07-08). `.agents/review/harnesses.local.json`
# is the machine-local, gitignored reviewer-tier session cache (review-economy
# plan, 2026-07-17): governance prose legitimately names it, but it never
# exists in a committed tree — same class as `.agents/machines.md`.
LINT_EXEMPT_PATHS = frozenset({
    "docs/history",
    "docs/history/state-archive.md",
    "docs/history/decisions-archive.md",
    ".agents/machines.md",
    ".agents/review/harnesses.local.json",
})


def _lintable_repo_path(tok: str) -> bool:
    """True for backtick tokens that read as repo-relative file references.
    Conservative by design: commands, URLs, globs, placeholders, file:line
    cites, absolute/outside paths, and bare shorthand names are all skipped —
    a missed lint is cheap, a false LINT line erodes trust in the report."""
    if any(c in tok for c in ":<>*{}$\\(),"):
        return False
    if tok.startswith(("http", "..", "~", "/", "-", "@")):
        return False
    return "/" in tok


def _deletion_commit(target_repo, tok, _cache):
    """Short hash of the commit that deleted `tok`, or None. Git is the
    no-maintenance evidence that a missing path is historical rather than a
    typo: a deliberate deletion always left a commit behind, a typo never
    did (owner direction, 2026-07-09 — no allowlists, consult history,
    print the note). Any failure (never tracked, shallow clone, not a git
    repo) returns None and the caller keeps the loud warning: degradation
    is toward loud, never toward silent-wrong."""
    key = tok.rstrip("/")
    if key not in _cache:
        proc = git(target_repo, "log", "--diff-filter=D", "--format=%h",
                   "-1", "--", key, check=False)
        out = proc.stdout.strip().splitlines() if proc.returncode == 0 else []
        _cache[key] = out[0].strip() if out else None
    return _cache[key]


def lint_governance(target_repo: Path) -> list:
    """Read-only hygiene checks over the repo-authored governance prose
    (`.agents/*.md` — NOT `AGENTS.md`, whose text is the byte-verified
    template and whose references are template-intentional). Never blocks,
    never edits; emits LINT report lines only. Runs on every refresh —
    the field lesson is that checks nobody triggers rot, checks riding an
    existing touchpoint stay true."""
    findings = []
    files = []
    deleted_cache = {}
    agents_dir = target_repo / ".agents"
    if agents_dir.is_dir():
        files += sorted(agents_dir.glob("*.md"))
    for f in files:
        if not f.is_file():
            continue
        rel = f.relative_to(target_repo).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        seen = set()
        for line in text.splitlines():
            if "lint: allow" in line:
                # The visible per-line escape for legitimate illustrative or
                # historical references (same convention as the plan lint).
                continue
            for m in PATH_TOKEN.finditer(line):
                tok = m.group(1)
                if tok in seen or not _lintable_repo_path(tok):
                    continue
                seen.add(tok)
                if tok.rstrip("/") in LINT_EXEMPT_PATHS:
                    continue
                if not (target_repo / tok.rstrip("/")).exists():
                    dh = _deletion_commit(target_repo, tok, deleted_cache)
                    if dh:
                        findings.append((rel, "historical: `{}` - deleted in {}".format(tok, dh), "note"))
                    else:
                        findings.append((rel, "references missing path `{}`".format(tok), "warn"))
        if f.name == "decisions.md":
            entries = list(re.finditer(r"^### (.+)$", text, re.M))
            for i, em in enumerate(entries):
                end = entries[i + 1].start() if i + 1 < len(entries) else len(text)
                seg = text[em.end():end]
                sm = re.search(r"^Status:\s*(\w+)", seg, re.M)
                if sm and sm.group(1) in ("Adopted", "Superseded"):
                    findings.append((rel, "closed decision awaiting archive: {}".format(em.group(1)[:70]), "warn"))
    return findings


def manifest_digest(toolkit: Path) -> str:
    return hashlib.sha256(
        (toolkit / "tools" / "shipped-set.json").read_bytes()).hexdigest()


def build_record(toolkit: Path, target: Path, plan: Plan) -> dict:
    """The immutable operation record: what a human approves is what
    --apply later verifies, field for field, before any write."""
    def entry(t, s):
        return {"target": t,
                "source": Path(s).relative_to(toolkit).as_posix(),
                "sha256": hashlib.sha256(Path(s).read_bytes()).hexdigest()}
    head = git(target, "rev-parse", "HEAD", check=False)
    rec = {
        "schema": 1,
        "toolkit_sha": git(toolkit, "rev-parse", "HEAD").stdout.strip(),
        "toolkit_dirty": bool(
            git(toolkit, "status", "--porcelain", check=False).stdout.strip()),
        "manifest_digest": manifest_digest(toolkit),
        "target_head": head.stdout.strip() if head.returncode == 0 else "",
        "installs": [entry(t, s) for t, s in plan.install],
        "updates": [entry(t, s) for t, s in plan.update],
        "restores": [entry(t, s) for t, s in plan.restore],
        "drift": dict(sorted(plan.drift.items())),
        "removes": list(plan.remove),
        "gitignore_repairs": [[ln, old, list(repl)]
                              for ln, old, repl in plan.gitignore_repairs],
        "flags": [[t, r] for t, r in plan.flags],
        "staged_paths": touched_paths(plan),
    }
    canonical = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    rec["digest"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return rec


def verify_record(record: dict, toolkit: Path, target: Path, plan: Plan) -> "list[str]":
    """Reasons an approved plan record no longer matches reality. Any
    non-empty result refuses the apply before the first write."""
    if record.get("schema") != 1:
        return ["unsupported plan schema: {!r}".format(record.get("schema"))]
    current = build_record(toolkit, target, plan)
    problems = []
    if current["toolkit_dirty"] or record.get("toolkit_dirty"):
        problems.append("toolkit worktree is dirty (apply requires a clean tree)")
    for field in ("toolkit_sha", "manifest_digest", "target_head", "installs",
                  "updates", "restores", "drift", "removes",
                  "gitignore_repairs", "flags", "staged_paths"):
        if current[field] != record.get(field):
            problems.append("drift in {}: the current state no longer matches the approved plan".format(field))
    if not problems and current["digest"] != record.get("digest"):
        problems.append("plan digest mismatch")
    return problems


def touched_paths(plan: Plan) -> list:
    paths = [t for t, _ in plan.install + plan.update + plan.restore] + list(plan.remove)
    paths += [t for t, _ in plan.repairs]
    if plan.gitignore_repairs:
        paths.append(".gitignore")
    return paths


def dirty_conflicts(target_repo: Path, plan: Plan) -> list:
    paths = touched_paths(plan)
    if not paths:
        return []
    out = git(target_repo, "status", "--porcelain", "--", *paths).stdout
    conflicts = [line for line in out.splitlines() if line.strip()]
    # `status --porcelain` omits IGNORED untracked files, so an ignored copy
    # of a retired target would sail past the dirty check and be unlinked -
    # destroying content that exists nowhere in git (openreview finding,
    # 2026-07-16). Removal requires the path to be tracked: tracked content
    # is committed (working-tree edits already show up above), untracked or
    # ignored content exists only in the working tree - refuse.
    flagged = {ln[3:].strip() for ln in conflicts}
    for target in plan.remove:
        if target in flagged:
            continue
        tracked = git(target_repo, "ls-files", "--error-unmatch", "--", target,
                      check=False)
        if tracked.returncode != 0:
            conflicts.append("!! {} (untracked or ignored; its content exists "
                             "only in the working tree)".format(target))
    return conflicts


def apply_plan(target_repo: Path, plan: Plan) -> None:
    # Validate every destination before the first write: a refusal must
    # leave the tree untouched, never partially mutated.
    for target, _src in plan.install + plan.update + plan.restore:
        assert_safe_dest(target_repo, target)
    for target in plan.remove:
        assert_safe_dest(target_repo, target)
    if plan.gitignore_repairs:
        assert_safe_dest(target_repo, ".gitignore")
    for target, src in plan.install + plan.update + plan.restore:
        dest = target_repo / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(dest, src.read_bytes())
    for target in plan.remove:
        (target_repo / target).unlink()
    if plan.gitignore_repairs:
        gitignore = target_repo / ".gitignore"
        lines = gitignore.read_text(encoding="utf-8").splitlines()
        # apply bottom-up so line numbers stay valid
        for lineno, _old, repl in sorted(plan.gitignore_repairs, reverse=True):
            lines[lineno - 1:lineno] = list(repl)
        write_atomic(gitignore, ("\n".join(lines) + "\n").encode("utf-8"))


def stage(target_repo: Path, plan: Plan) -> None:
    paths = touched_paths(plan)
    if paths:
        git(target_repo, "add", "--", *paths)


def governance_roots(shipped: dict) -> set:
    """First path segment of every manifest target that lives in a
    directory - the trees the toolkit owns (.agents, .claude, ...). A
    top-level file target (AGENTS.md) contributes no tree. The prune sweep
    never leaves these roots."""
    roots = set()
    for section in ("artifacts", "retired", "seeded"):
        for entry in shipped.get(section, []):
            parts = Path(entry.get("target", "")).parts
            if len(parts) > 1:
                roots.add(parts[0])
    return roots


def emptied_dirs(target_repo: Path, shipped: dict) -> list:
    """Directories under the governance roots holding nothing at all,
    deepest first. Read-only. Removing a retired target leaves its
    directory behind and git cannot report it - it does not track
    directories - so the litter survives every later run (observed after
    the drift/harness-update retirement, 2026-07-24). The roots themselves
    are never candidates: an empty `.agents/` is a repo's business, not
    ours."""
    removable = set()
    found = []
    for root in sorted(governance_roots(shipped)):
        base = target_repo / root
        if not base.is_dir():
            continue
        # Bottom-up, and a directory counts as empty when every entry it
        # holds is itself already marked removable: a chain of empty
        # directories collapses in one pass instead of one per run. Any
        # file, or any entry that is not a removable directory (a symlink),
        # disqualifies it.
        for dirpath, _dirnames, _filenames in os.walk(str(base), topdown=False):
            if Path(dirpath) == base:
                continue
            entries = os.listdir(dirpath)
            if all(os.path.join(dirpath, e) in removable for e in entries):
                removable.add(dirpath)
                found.append(Path(dirpath).relative_to(target_repo).as_posix())
    # Deepest first so a child is gone before its parent is attempted.
    return sorted(found, key=lambda p: (-p.count("/"), p))


def confirm_prune(count: int, input_fn=input) -> bool:
    """One question, default yes; anything else declines. Callers gate on
    isatty - never reached non-interactively."""
    try:
        answer = input_fn(
            "Remove {} empty director{} left by retired files? [Y/n] ".format(
                count, "y" if count == 1 else "ies")).strip().lower()
    except EOFError:
        return False
    return answer in ("", "y", "yes")


def prune_dirs(target_repo: Path, dirs: list) -> list:
    """rmdir each, deepest first; a directory that stopped being empty
    (racing writer) is skipped, never forced."""
    pruned = []
    for rel in dirs:
        try:
            (target_repo / rel).rmdir()
        except OSError:
            continue
        pruned.append(rel)
    return pruned


# Harness detection is a PATH probe, never a gate (owner ruling 2026-07-23):
# a wide set of common agent CLI names is probed, plus any the owner recorded
# on this machine (.agents/machines.md "harness-cli:" lines, written by the
# offer's "another" option). A harness not probed is reached via "another"
# and remembered after first use. Shape exceptions are one-liners for CLIs
# that do not take a positional prompt (agy needs -i); everything else
# launches as `<name> "<prompt>"`. Adding or changing an exception is a
# provenance-bearing change (2026-07-08 standing rule).
PROBE_HARNESSES = [
    "claude", "codex", "agy", "grok", "kimi", "kimi-code", "hermes",
    "cursor", "aider", "gemini", "goose", "opencode",
]
SHAPE_EXCEPTIONS = {
    "agy": ("agy", "-i", "{prompt}"),
}


def detect_harnesses(which=shutil.which, target=None):
    """Harness CLIs actually installed right now - probed at offer time,
    never remembered between runs - plus the owner's recorded CLIs from the
    repo's machines.md (still only when present on PATH right now)."""
    names = [n for n in PROBE_HARNESSES if which(n)]
    if target is not None:
        machines = Path(target) / ".agents" / "machines.md"
        if machines.exists():
            text = machines.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"harness-cli:\s*([A-Za-z0-9._-]+)", text):
                name = m.group(1)
                if name not in names and which(name):
                    names.append(name)
    return [(n, SHAPE_EXCEPTIONS.get(n, (n, "{prompt}"))) for n in names]


def record_harness_cli(target_repo: Path, name: str) -> None:
    """Remember an "another"-typed harness CLI in the repo's machines.md so
    the next offer numbers it. Best-effort: a record failure never blocks
    the launch."""
    import datetime
    machines = target_repo / ".agents" / "machines.md"
    try:
        machines.parent.mkdir(parents=True, exist_ok=True)
        text = (machines.read_text(encoding="utf-8")
                if machines.exists() else "# Machines\n")
        if "harness-cli: {}".format(name) in text:
            return
        line = "- harness-cli: {} (recorded {}, refresh offer)".format(
            name, datetime.date.today().isoformat())
        if not text.endswith("\n"):
            text += "\n"
        write_atomic(machines, (text + line + "\n").encode("utf-8"))
        git(target_repo, "add", "--", ".agents/machines.md", check=False)
        git(target_repo, "commit", "-q", "-m",
            "record harness CLI: {}".format(name), "--",
            ".agents/machines.md", check=False)
    except OSError:
        pass


def core_flags(plan: Plan, shipped: dict) -> list:
    """Flag targets in the replace-whole (core file) class - the one flag
    category that is never a legitimate steady state."""
    whole = {a["target"] for a in shipped["artifacts"]
             if a["class"] == "replace-whole"}
    return [t for t, _ in plan.flags if t in whole]


def banner_block(targets) -> str:
    bar = "=" * 66
    lines = [bar]
    for t in targets:
        lines.append("  ATTENTION: {} was NOT replaced.".format(t))
    lines.append("  It matches no known template version (hand-edited or foreign), so")
    lines.append("  replacing it could destroy content the toolkit does not own.")
    lines.append("  To replace it anyway — git history preserves the old content —")
    lines.append("  re-run with --force. To migrate its content instead, run the")
    lines.append("  bootstrap procedure.")
    lines.append(bar)
    return "\n".join(lines)


def bootstrap_prompt(toolkit: Path, target: Path) -> str:
    return ("Read {} in full, then run the bootstrap procedure against this "
            "repo ({}). Governance refresh refused to replace a core "
            "governance file here; the procedure owns recovery, including "
            "the legacy-governance carve-out.").format(
                toolkit / "procedures" / "bootstrap.md", target)


def launch_argv(shape, prompt: str) -> list:
    return [part.replace("{prompt}", prompt) for part in shape]


def render_cmd(argv, windows=None) -> str:
    """Platform-correct copy/paste rendering: POSIX quoting is wrong for
    Windows shells, so render with list2cmdline there."""
    win = (os.name == "nt") if windows is None else windows
    return subprocess.list2cmdline(argv) if win else shlex.join(argv)


def non_tty_commands(candidates, prompt: str, target: Path, toolkit: Path) -> str:
    """The non-interactive fallback under the banner: never prompt, never
    hang - print the exact ready-to-paste launch command per detected
    harness (or the procedure path when nothing is installed)."""
    if not candidates:
        return ("  no known harness CLI found on PATH; the procedure is\n"
                "  {}".format(toolkit / "procedures" / "bootstrap.md"))
    lines = ["  to run bootstrap, launch one of these in {}:".format(target)]
    for _name, shape in candidates:
        lines.append("    " + render_cmd(launch_argv(shape, prompt)))
    return "\n".join(lines)


def remediate_prompt(toolkit: Path, target: Path, warns) -> str:
    lines = ["Governance hygiene findings in this repo need judgment fixes:"]
    for rel, msg, _kind in warns:
        lines.append("- {}: {}".format(rel, msg))
    return ("Read {} in full. This is an INTERACTIVE session with the "
            "owner: present each finding below one at a time — its evidence, "
            "the options, your recommendation — and ask the owner how to "
            "remediate it. The owner decides; you apply the decision. Do not "
            "fix anything on your own authority and do not end the session; "
            "the owner ends it. Findings in {}:\n\n{}").format(
                toolkit / "procedures" / "remediate-governance.md",
                target, "\n".join(lines))


def offer_bootstrap(candidates, prompt: str, target: Path,
                    input_fn=input, launch_fn=None, question="Run bootstrap now?"):
    """One question at a real TTY. A valid number launches that harness with
    the kickoff prompt; "t" asks for a harness command and launches whatever
    the owner types — verbatim, never gated by the probe list (owner ruling
    2026-07-23), as `<name> "<prompt>"` — and records it in machines.md for
    next time. Anything else (q, empty, EOF, out-of-range) declines and
    changes nothing. Returns the harness exit code, or None when declined.
    Callers gate on isatty - this function is never reached non-interactively."""
    menu = "  ".join("[{}] {}".format(i + 1, name)
                     for i, (name, _shape) in enumerate(candidates))
    try:
        choice = input_fn("{} Installed harnesses: {}  [t] another  [q] no\n> ".format(
            question, menu)).strip()
    except EOFError:
        return None
    if choice.lower() == "t":
        try:
            name = input_fn("harness command: ").strip()
        except EOFError:
            return None
        if not name:
            return None
        argv = [name, prompt]
        record_harness_cli(target, name)
    else:
        if not choice.isdigit() or not (1 <= int(choice) <= len(candidates)):
            return None
        _name, shape = candidates[int(choice) - 1]
        argv = launch_argv(shape, prompt)
    if launch_fn is None:
        launch_fn = lambda a: subprocess.call(a, cwd=str(target))
    return launch_fn(argv)


def terse_line(target: Path, plan: Plan, sync_note: str, changed: bool,
               commit_sha: str, stage_only: bool) -> str:
    """The whole owner-facing result of a run in one line (2026-07-23
    owner-surface D3): per-item detail lives in the commit message, never
    behind a rerun flag. Healthy loop runs read as one line per repo."""
    repo = target.name or str(target)
    if not changed:
        out = "refresh: {} — already current".format(repo)
    else:
        parts = []
        seeded = set(plan.seeded)
        installed = [t for t, _ in plan.install if t not in seeded]
        for label, items in (("installed", installed), ("seeded", plan.seeded),
                             ("updated", plan.update),
                             ("restored", plan.restore), ("removed", plan.remove)):
            if items:
                parts.append("{} {}".format(len(items), label))
        if plan.repairs:
            parts.append("{} repaired".format(len(plan.repairs)))
        if plan.gitignore_repairs:
            parts.append(".gitignore repaired")
        where = "staged, uncommitted" if stage_only else "commit " + commit_sha
        out = "refresh: {} — {} ({}; details in the commit message)".format(
            repo, ", ".join(parts), where)
    if sync_note:
        out += " — " + sync_note
    return out


def summarize(plan: Plan, sync_note: str) -> str:
    lines = []
    seeded = set(plan.seeded)
    for label, items in (
        ("installed", [t for t, _ in plan.install if t not in seeded]),
        ("seeded", list(plan.seeded)),
        ("updated", [t for t, _ in plan.update]),
    ):
        for t in items:
            lines.append("  {}: {}".format(label, t))
    for t, _src in plan.restore:
        lines.append("  restored: {} (DRIFT: matched no shipped version; recent: {})".format(
            t, plan.drift.get(t, "")))
    for t in plan.remove:
        if t in plan.drift:
            lines.append("  removed: {} (DRIFT: matched no shipped version; recent: {})".format(
                t, plan.drift[t]))
        else:
            lines.append("  removed: {}".format(t))
    for lineno, old, _repl in plan.gitignore_repairs:
        lines.append("  .gitignore: repaired blanket rule '{}' (line {})".format(old, lineno))
    for t, note in plan.repairs:
        lines.append("  repaired: {} ({})".format(t, note))
    for t, reason in plan.flags:
        lines.append("  FLAG {}: {}".format(t, reason))
    if not lines:
        lines.append("  nothing to do - repo is current")
    if sync_note:
        lines.append("  NOTE: {}".format(sync_note))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", default=".", help="governed repo (default: cwd)")
    ap.add_argument("--toolkit", default=None, help="toolkit root (default: this script's repo)")
    ap.add_argument("--stage-only", action="store_true", help="stage reconciled paths, do not commit (first-bootstrap mode)")
    ap.add_argument("--no-sync", action="store_true", help="skip syncing the toolkit clone")
    ap.add_argument("--plan-json", default=None, metavar="PATH",
                    help="read-only: write the operation record as JSON (or - for stdout) and change nothing")
    ap.add_argument("--apply", default=None, metavar="PLAN",
                    help="apply a --plan-json record, refusing if anything drifted since it was made")
    ap.add_argument("--force", action="store_true",
                    help="replace even foreign core governance files (git history preserves "
                         "the old content); uncommitted changes are still protected")
    ap.add_argument("--no-remediate", action="store_true",
                    help="never launch a live remediation session for lint findings; "
                         "print them instead (CI and automated runs)")
    ap.add_argument("--lint-only", action="store_true",
                    help="read-only: print hygiene findings and exit (0 clean, "
                         "6 findings present); no sync, reconcile, commit, or offers")
    args = ap.parse_args(argv)

    if args.plan_json and args.apply:
        print("refresh: --plan-json and --apply are mutually exclusive", file=sys.stderr)
        return 2
    plan_record = None
    if args.apply:
        try:
            plan_record = json.loads(Path(args.apply).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print("refresh: cannot read plan {}: {}".format(args.apply, exc), file=sys.stderr)
            return 2
        args.no_sync = True  # apply never resyncs: the record is the operation

    toolkit = Path(args.toolkit).resolve() if args.toolkit else Path(__file__).resolve().parent.parent
    target = Path(args.target).resolve()

    err = worktree_root_error(target)
    if err:
        print("refresh: {} is {}".format(target, err), file=sys.stderr)
        return 2
    if args.lint_only:
        # Read-only verification (2026-07-24): print hygiene findings and
        # exit — no sync, no reconcile, no commit, no offers. Exit 6 when
        # judgment findings are present so a session can branch on it.
        warns = 0
        for rel, msg, kind in lint_governance(target):
            print("  {} {}: {}".format("NOTE" if kind == "note" else "LINT", rel, msg))
            warns += (kind != "note")
        if warns:
            print("refresh: {} hygiene finding(s) need judgment.".format(warns))
            return 6
        print("refresh: hygiene clean.")
        return 0
    if not (toolkit / "tools" / "shipped-set.json").exists():
        print("refresh: {} does not look like the toolkit (no tools/shipped-set.json)".format(toolkit), file=sys.stderr)
        return 2
    if target == toolkit:
        print("refresh: refusing to run against the toolkit repo itself ({}).".format(target), file=sys.stderr)
        print("Self-refresh is an owner-only action (2026-07-10 ruling): agents never update", file=sys.stderr)
        print("this repo's own governance while working on the toolkit.", file=sys.stderr)
        return 2

    # Preflight: the fatal reads here happen before the first write, so these
    # refusals leave the tree untouched. (Exit 5 is not such a refusal — it
    # reports a foreign core file after other artifacts may already have been
    # installed and committed.)
    policy_path = target / ".agents" / "push-policy.md"
    policy_line = None
    if policy_path.exists():
        policy_lines = policy_path.read_text(encoding="utf-8").strip().splitlines()
        if not policy_lines:
            print("refresh: {} is empty or malformed; fix the push policy before refreshing".format(policy_path), file=sys.stderr)
            return 4
        policy_line = policy_lines[-1]
    sync_note = ""
    if not args.no_sync:
        head_before = git(toolkit, "rev-parse", "HEAD").stdout.strip()
        sync_note = sync_toolkit(toolkit)
        head_after = git(toolkit, "rev-parse", "HEAD").stdout.strip()
        maybe_reexec(head_before, head_after)
    toolkit_sha = git(toolkit, "rev-parse", "--short", "HEAD").stdout.strip()

    shipped = load_shipped_set(toolkit)
    manifest_errors = validate_manifest(shipped, toolkit)
    if manifest_errors:
        print("refresh: tools/shipped-set.json failed validation:", file=sys.stderr)
        for e in manifest_errors:
            print("  " + e, file=sys.stderr)
        return 4
    plan = classify(target, toolkit, shipped)
    check_committability(target, plan, shipped)
    core = core_flags(plan, shipped)
    if args.force and core:
        # Owner override (2026-07-23, owner-surface D3): --force replaces a
        # foreign core file on demand; the dirty-tree refusal above still
        # protects uncommitted content, and git history preserves the old
        # bytes. The replacement is loud in both the summary and the commit.
        src_by_target = {a["target"]: toolkit / a["source"]
                         for a in shipped["artifacts"]}
        forced = set(core)
        plan.flags = [(t, r) for t, r in plan.flags if t not in forced]
        for t in sorted(forced):
            plan.restore.append((t, src_by_target[t]))
            plan.drift[t] = ("FORCED (--force): foreign core file replaced on "
                             "owner demand; prior content preserved in git history")
        core = []

    conflicts = dirty_conflicts(target, plan)
    if conflicts:
        print("refresh: refusing to run over uncommitted changes on paths it would touch:", file=sys.stderr)
        for line in conflicts:
            print("  " + line, file=sys.stderr)
        return 3

    if args.plan_json:
        record = build_record(toolkit, target, plan)
        payload = json.dumps(record, indent=2, sort_keys=True) + "\n"
        if args.plan_json == "-":
            sys.stdout.write(payload)
        else:
            Path(args.plan_json).write_text(payload, encoding="utf-8")
        print("governance refresh plan against toolkit {} (read-only - nothing changed)".format(toolkit_sha))
        print(summarize(plan, sync_note))
        for rel, note_msg, kind in lint_governance(target):
            print("  {} {}: {}".format("NOTE" if kind == "note" else "LINT", rel, note_msg))
        return 0

    if plan_record is not None:
        problems = verify_record(plan_record, toolkit, target, plan)
        if problems:
            print("refresh: refusing --apply; the approved plan no longer matches:", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
            return 4

    # Mechanical repairs run in every applying mode (never in read-only
    # --plan-json, which returns above) and join the refresh commit.
    repair_push_status_lines(target, plan)
    repair_moved_references(target, plan)
    repair_closed_decisions(target, plan)
    changed = bool(plan.install or plan.update or plan.restore or plan.remove
                   or plan.gitignore_repairs or plan.repairs)
    if changed:
        try:
            apply_plan(target, plan)
        except (RuntimeError, OSError) as exc:
            # OSError caught alike: a mid-loop write failure returns a clean
            # refusal instead of a traceback, and never reaches the commit.
            print("refresh: refusing unsafe write - {}".format(exc), file=sys.stderr)
            return 4
        stage(target, plan)
        if not args.stage_only:
            # Pathspec-scoped commit: unrelated pre-staged work stays staged
            # and out of the governance commit, then the created commit is
            # verified to touch exactly the planned paths.
            paths = touched_paths(plan)
            # Crash check: apply+stage must have landed every planned path in
            # the index before we commit. A partial apply that left a path
            # written but unstaged would otherwise be misread as "current" on
            # the next run and never committed; refuse here instead. Exempt in
            # --stage-only, where the bootstrap flow stages more and makes the
            # single scoped commit itself. --no-renames so a retired path whose
            # content matches a new artifact is not collapsed into a rename and
            # dropped from the staged list (same hazard as the post-commit
            # verification below).
            staged = set(git(target, "diff", "--cached", "--no-renames",
                             "--name-only", "--", *paths).stdout.splitlines())
            staged.discard("")
            if staged != set(paths):
                print("refresh: staged set does not cover the plan (expected {}; "
                      "staged {}). Nothing was committed.".format(
                          sorted(set(paths)), sorted(staged)), file=sys.stderr)
                return 4
            msg = "governance refresh: toolkit {}\n\n{}".format(toolkit_sha, summarize(plan, ""))
            if plan_record is not None:
                msg += "\n\ntoolkit-sha: {}\nplan-digest: {}".format(
                    plan_record.get("toolkit_sha", ""), plan_record.get("digest", ""))
            git(target, "commit", "-m", msg, "--", *paths)
            # --no-renames: a retired file replaced by a similar new artifact
            # (reviewloop.md -> codereview.md) collapses to one rename line
            # under default rename detection, making a correct commit look
            # like a plan mismatch (fleet-refresh field failure, 2026-07-16).
            committed = set(
                git(target, "show", "--no-renames", "--name-only", "--format=",
                    "HEAD").stdout.splitlines())
            committed.discard("")
            if committed != set(paths):
                print("refresh: the created commit does not match the plan "
                      "(expected {}; got {}). The commit exists - inspect it "
                      "before retrying.".format(sorted(set(paths)), sorted(committed)),
                      file=sys.stderr)
                return 4

    commit_sha = ""
    if changed and not args.stage_only:
        commit_sha = git(target, "rev-parse", "--short", "HEAD").stdout.strip()
    print(terse_line(target, plan, sync_note, changed, commit_sha, args.stage_only))
    if git(toolkit, "status", "--porcelain", check=False).stdout.strip():
        print("  NOTE: toolkit tree is dirty; installed bytes may not match {}".format(toolkit_sha))
    # A seeded file is the one result that needs the owner to do something
    # afterwards (choose a level, choose a push policy), so it earns a line of
    # its own past the one-line result rule (2026-07-23 owner-surface D3 —
    # which governs per-item detail, not follow-up actions). Fires only in the
    # run that seeds; the text comes from the manifest.
    if plan.seeded:
        actions = {sd["target"]: sd.get("action", "seeded (repo-owned from now on).")
                   for sd in shipped.get("seeded", [])}
        for t in plan.seeded:
            print("  ACTION: {} {}".format(t, actions.get(t, "seeded (repo-owned from now on).")))

    # Final cleanup: retiring the last file in a directory leaves the
    # directory behind, invisible to git. Ask once before removing any of
    # them (owner ruling 2026-07-25); automated runs report and remove
    # nothing. Nothing here is staged or committed - an empty directory is
    # untracked by definition, so this can never touch the plan record.
    stale_dirs = emptied_dirs(target, shipped)
    if stale_dirs:
        for d in stale_dirs:
            print("  empty: {}".format(d))
        interactive = sys.stdin.isatty() and sys.stdout.isatty() and not args.no_remediate
        if interactive and confirm_prune(len(stale_dirs)):
            for d in prune_dirs(target, stale_dirs):
                print("  pruned: {}".format(d))
        else:
            print("  (left in place; nothing was removed)")
    findings = lint_governance(target)
    warns = [(rel, msg, kind) for rel, msg, kind in findings if kind != "note"]
    for rel, msg, kind in findings:
        if kind == "note":
            print("  NOTE {}: {}".format(rel, msg))
    if warns and not args.no_remediate:
        # Judgment findings: explain why the run cannot fully converge (the
        # LINT lines), then ASK whether to launch an interactive remediation
        # session, and in which harness (2026-07-23 owner ruling: no
        # automatic launches; the "another" option keeps any harness
        # reachable). Non-TTY: print only.
        for rel, msg, _kind in warns:
            print("  LINT {}: {}".format(rel, msg))
        print("  refresh cannot remediate these itself — they need judgment.")
        code = None
        if sys.stdin.isatty() and sys.stdout.isatty():
            candidates = detect_harnesses(target=target)
            prompt = remediate_prompt(toolkit, target, warns)
            code = offer_bootstrap(candidates, prompt, target,
                                   question="Launch a remediation session now?")
        if code:
            print("  remediation session exited nonzero ({}) — findings "
                  "may remain; re-run to retry.".format(code))
    elif warns:
        for rel, msg, _kind in warns:
            print("  LINT {}: {}".format(rel, msg))

    if core:
        print(banner_block(core))
        prompt = bootstrap_prompt(toolkit, target)
        candidates = detect_harnesses(target=target)
        if candidates and sys.stdin.isatty() and sys.stdout.isatty():
            offer_bootstrap(candidates, prompt, target)
        else:
            print(non_tty_commands(candidates, prompt, target, toolkit))
        # A flagged core (replace-whole) file means the repo did not converge
        # to the shipped set: distinct exit 5 so a script can tell an
        # ungoverned repo from a clean converged run (exit 0).
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
