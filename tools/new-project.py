#!/usr/bin/env python3
"""new-project: one-command greenfield install of the governance toolkit.

`new-project <path> [hint]` — create <path> if needed, `git init` there,
install the shipped governance set (staged, uncommitted, via refresh.py
--stage-only), then offer to launch a detected agent harness in the new
repo with a kickoff prompt pointing at procedures/setup.md. When a hint
is given it primes the kickoff, so the setup conversation opens with a
confirmation, not an interrogation. The owner never sees a Python error:
the tools/new-project shell launcher owns the interpreter.

Owner ruling 2026-07-23 (owner-surface redesign D1/D2/D2a).
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refresh import detect_harnesses, launch_argv, render_cmd  # noqa: E402


def kickoff_prompt(toolkit: Path, target: Path, hint: str) -> str:
    prompt = (
        "Read {} in full and run the greenfield setup procedure in this "
        "repo ({}). The governance set is installed and staged; you own "
        "the judgment files, the setup questions, and the first commit."
    ).format(toolkit / "procedures" / "setup.md", target)
    if hint:
        prompt += (' The owner describes this project as: "{}" — confirm '
                   "that, don't interrogate.".format(hint))
    return prompt


def offer_launch(candidates, prompt: str, target: Path,
                 input_fn=input, launch_fn=None):
    """One question at a real TTY; a valid number launches that harness
    interactively in the new repo with the kickoff prompt; anything else
    (q, empty, EOF, out-of-range) declines. Returns the harness exit code,
    or None when declined. Callers gate on isatty — never reached
    non-interactively."""
    menu = "  ".join("[{}] {}".format(i + 1, name)
                     for i, (name, _shape) in enumerate(candidates))
    try:
        choice = input_fn("Launch an agent here to finish setup? Installed "
                          "harnesses: {}  [q] no\n> ".format(menu)).strip()
    except EOFError:
        return None
    if not choice.isdigit() or not (1 <= int(choice) <= len(candidates)):
        return None
    _name, shape = candidates[int(choice) - 1]
    argv = launch_argv(shape, prompt)
    if launch_fn is None:
        launch_fn = lambda a: subprocess.call(a, cwd=str(target))
    return launch_fn(argv)


def print_launch_lines(candidates, prompt: str, target: Path, toolkit: Path) -> None:
    """Non-interactive fallback: never prompt, never hang — print the exact
    ready-to-paste launch command per detected harness (or the procedure
    path when nothing is installed)."""
    if not candidates:
        print("  no known harness CLI found on PATH; finish setup by pointing")
        print("  any agent at the procedure:")
        print("  {}".format(toolkit / "procedures" / "setup.md"))
        return
    print("  to finish setup, launch one of these in {}:".format(target))
    for _name, shape in candidates:
        print("    " + render_cmd(launch_argv(shape, prompt)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", help="project directory to create and set up")
    ap.add_argument("hint", nargs="*", default=[],
                    help="optional one-line project description (primes the setup agent)")
    args = ap.parse_args(argv)
    hint = " ".join(args.hint).strip()

    toolkit = Path(__file__).resolve().parent.parent
    target = Path(args.path).resolve()

    if (target / "AGENTS.md").exists() or (target / ".agents").is_dir():
        print("new-project: {} already has governance (AGENTS.md or .agents/).".format(target),
              file=sys.stderr)
        print("This is a fresh-install command. To update existing governance,", file=sys.stderr)
        print("run the refresh there instead:", file=sys.stderr)
        print("  {}".format(render_cmd([sys.executable,
                                        str(toolkit / "tools" / "refresh.py"), str(target)])),
              file=sys.stderr)
        return 2

    target.mkdir(parents=True, exist_ok=True)
    if not (target / ".git").is_dir():
        proc = subprocess.run(["git", "-C", str(target), "init"],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            print("new-project: git init failed in {}: {}".format(
                target, proc.stderr.strip()), file=sys.stderr)
            return 2
        print("  initialized git repo: {}".format(target))

    refresh = [sys.executable, str(toolkit / "tools" / "refresh.py"),
               str(target), "--stage-only", "--no-sync", "--no-remediate"]
    proc = subprocess.run(refresh, capture_output=True, text=True)
    if proc.returncode != 0:
        print("new-project: governance install failed:", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    print("  governance set installed and staged (uncommitted).")

    prompt = kickoff_prompt(toolkit, target, hint)
    candidates = detect_harnesses(target=target)
    if sys.stdin.isatty() and sys.stdout.isatty() and candidates:
        code = offer_launch(candidates, prompt, target)
        if code is not None:
            return code
    print_launch_lines(candidates, prompt, target, toolkit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
