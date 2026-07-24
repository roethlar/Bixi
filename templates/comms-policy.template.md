<!-- comms-level: 3 -->
Owner-communication level for this repo. It tunes the register of
owner-facing output only — chat answers, summaries, decision asks, and
plan-document prose. It never changes any safety, approval, or
verification rule, and the Owner Gates structural contract (a line of
context, the question, what changes under each option, the recommended
option and why) is level-independent: every gate still carries all of
those, whatever the level.

The active level is the number in the marker comment on the first line;
change the level by editing that number.

Levels:
1 — explain like I'm five: no jargon at all; short sentences; define every
    term; one idea at a time.
2 — plain English, one decision at a time: no devops jargon; each owner
    decision presented on its own, roughly 25-50 plain words.
3 — normal user: plain language with common technical terms; concise, no
    hand-holding.
4 — devops shorthand: technical jargon and abbreviations acceptable;
    density over ceremony.
5 — devops / jargon, terse: maximal shorthand; assumes deep familiarity.
