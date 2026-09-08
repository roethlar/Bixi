#!/usr/bin/env python3
"""Record outgoing template hashes before committing toolkit source edits."""
import hashlib
import json
import subprocess
from pathlib import Path


def record_history(toolkit: Path, base: str = "HEAD") -> int:
    def show(path):
        return subprocess.check_output(["git", "-C", str(toolkit),
                                        "show", base + ":" + path])
    manifest = toolkit / "tools/shipped-set.json"
    current = json.loads(manifest.read_text(encoding="utf-8"))
    previous = json.loads(show("tools/shipped-set.json"))
    destinations = {item["target"]: item for item in
                    current["artifacts"] + current.get("retired", [])}
    changed = set(subprocess.check_output(
        ["git", "-C", str(toolkit), "diff", "--name-only", base, "--", "templates"]
    ).decode("utf-8").splitlines())
    added = 0
    for old in previous["artifacts"]:
        item = destinations.get(old["target"])
        if item is None:
            raise ValueError("Removed target needs a retirement entry: " + old["target"])
        if old["source"] not in changed and item.get("source") == old["source"]:
            continue
        digest = hashlib.sha256(show(old["source"]).replace(b"\r\n", b"\n")).hexdigest()
        if digest not in item.setdefault("formerly", []):
            item["formerly"].append(digest)
            added += 1
    if added:
        manifest.write_text(json.dumps(current, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    return added


if __name__ == "__main__":
    print("Recorded {} outgoing version hash(es).".format(
        record_history(Path(__file__).resolve().parent.parent)))
