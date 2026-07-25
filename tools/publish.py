#!/usr/bin/env python3
"""publish: release the toolkit to the clean public product repo.

Copies the publish set — whole paths, no lists (owner ruling 2026-07-23):
tools/, templates/, procedures/, assets/, and the product README — from this
development repo into the clean product-repo checkout, mirrors it exactly
(stale files removed), makes one release commit, and pushes. The owner runs
it directly; no git knowledge needed. The product repo path is given once
(`publish <path>`) and recorded in .agents/machines.md for later runs.

Each entry maps a development-repo source to its product-repo target. The
two differ for the README: the product repo's front page is written for
someone arriving cold at the released toolkit, while this repo's README.md
is written for someone working on it. Mirroring means the product repo
cannot keep a file of its own — everything but .git is cleared before the
copy — so a product-only file lives here, under product/, and publishes to
its own name there.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PUBLISH_PATHS = [
    ("tools", "tools"),
    ("templates", "templates"),
    ("procedures", "procedures"),
    ("product/README.md", "README.md"),
    # Ships for the same reason as the README: mirroring clears the product
    # repo, and without it OS junk lands untracked and blocks the next
    # release through the dirty-tree refusal.
    ("product/.gitignore", ".gitignore"),
    # The front page references these by relative path; mirroring clears the
    # product repo first, so an unpublished asset is a broken image.
    ("assets", "assets"),
]


def git(repo: Path, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=check)


def recorded_product_repo(dev_repo: Path) -> "Path | None":
    machines = dev_repo / ".agents" / "machines.md"
    if not machines.exists():
        return None
    import re
    m = re.search(r"product-repo:\s*(\S+)",
                  machines.read_text(encoding="utf-8", errors="replace"))
    return Path(m.group(1)).expanduser() if m else None


def record_product_repo(dev_repo: Path, product: Path) -> None:
    import datetime
    machines = dev_repo / ".agents" / "machines.md"
    machines.parent.mkdir(parents=True, exist_ok=True)
    text = (machines.read_text(encoding="utf-8")
            if machines.exists() else "# Machines\n")
    line = "- product-repo: {} (recorded {}, first publish)\n".format(
        product, datetime.date.today().isoformat())
    if not text.endswith("\n"):
        text += "\n"
    machines.write_text(text + line, encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("product_repo", nargs="?", default=None,
                    help="clean product-repo checkout (only needed the first time)")
    ap.add_argument("--no-push", action="store_true",
                    help="commit the release locally; do not push")
    args = ap.parse_args(argv)

    dev = Path(__file__).resolve().parent.parent
    if args.product_repo:
        product = Path(args.product_repo).expanduser().resolve()
    else:
        product = recorded_product_repo(dev)
        if product is None:
            print("publish: no product repo recorded yet.", file=sys.stderr)
            print("Run once with the path:  tools/publish /path/to/product-repo",
                  file=sys.stderr)
            return 2

    if not (product / ".git").is_dir():
        print("publish: {} is not a git repo (expected the clean product-repo "
              "checkout).".format(product), file=sys.stderr)
        return 2
    dirty = git(product, "status", "--porcelain", check=False).stdout.strip()
    if dirty:
        print("publish: the product repo has uncommitted changes; refusing "
              "to run over them:", file=sys.stderr)
        print(dirty, file=sys.stderr)
        return 2

    # Preflight the whole publish set BEFORE touching the product repo:
    # every refusal above and below this point leaves it byte-identical.
    for src_rel, _dst_rel in PUBLISH_PATHS:
        if not (dev / src_rel).exists():
            print("publish: {} is missing from the development repo — "
                  "refusing to publish a partial set.".format(src_rel), file=sys.stderr)
            return 2

    # Mirror the publish set exactly: clear everything except .git, then copy.
    for child in product.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    copied = 0
    for src_rel, dst_rel in PUBLISH_PATHS:
        src = dev / src_rel
        dst = product / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst,
                            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
            copied += sum(1 for f in dst.rglob("*") if f.is_file())
        else:
            shutil.copy2(src, dst)
            copied += 1

    git(product, "add", "-A")
    staged = git(product, "status", "--porcelain", check=False).stdout.strip()
    if not staged:
        print("publish: the product repo already matches — nothing to release.")
        return 0
    import datetime
    stamp = datetime.date.today().isoformat()
    git(product, "commit", "-q", "-m", "release {}".format(stamp))
    sha = git(product, "rev-parse", "--short", "HEAD").stdout.strip()

    if args.product_repo:
        record_product_repo(dev, product)

    pushed = False
    if not args.no_push:
        remotes = git(product, "remote", check=False).stdout.split()
        if remotes:
            proc = git(product, "push", check=False)
            if proc.returncode != 0:
                print("publish: push failed — the release commit {} is local. "
                      "Fix the remote and push by hand or re-run.".format(sha),
                      file=sys.stderr)
                return 3
            pushed = True

    print("publish: {} files released as {} ({}){}.".format(
        copied, stamp, sha, " and pushed" if pushed else ", not pushed"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
