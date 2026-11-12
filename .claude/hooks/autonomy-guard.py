#!/usr/bin/env python3
"""PreToolUse hook for scheduled runs of the email-triage agent.

Reads the one `Level: <value>` line in AUTONOMY.md in the project root
(value 0, 1, 2, 3 or PAUSED) and blocks Bash calls the level does not allow:

  PAUSED, or the file is missing, or the line is missing, repeated or
  has any other value            -> block every Bash call
  Level 0 (on request only)      -> block every Bash call (this hook is
                                    installed for scheduled runs only)
  Level 1 or 2                   -> block the PMS notes command
  Level 3                        -> allow

Usage (see .claude/settings.example.json):
  python3 autonomy-guard.py "<PMS notes command>"

Exit 0 = no decision (normal permission flow). Exit 2 = block; stderr is
shown to the model as the reason.
"""
import json
import os
import re
import sys


def read_level(project_dir):
    """Return (level, reason). level is 0-3, or None for PAUSED."""
    try:
        with open(os.path.join(project_dir, "AUTONOMY.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None, "AUTONOMY.md is missing or unreadable"
    values = re.findall(r"^[ \t]*Level:[ \t]*(.*?)[ \t]*$", text, re.MULTILINE)
    if len(values) != 1:
        return None, "AUTONOMY.md has %d 'Level:' lines, expected 1" % len(values)
    if values[0] in ("0", "1", "2", "3"):
        return int(values[0]), ""
    if values[0] == "PAUSED":
        return None, "Level: PAUSED"
    return None, "unknown value 'Level: %s'" % values[0][:20]


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def main():
    notes_cmd = sys.argv[1].strip() if len(sys.argv) > 1 else ""
    try:
        event = json.load(sys.stdin)
    except ValueError:
        block("autonomy-guard: could not read the hook input; blocked to be safe.")
    if event.get("tool_name") != "Bash":
        sys.exit(0)
    command = (event.get("tool_input") or {}).get("command") or ""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or "."
    level, reason = read_level(project_dir)

    if level is None:
        block("autonomy-guard: paused (%s). Do nothing; log why and stop." % reason)
    if level == 0:
        block("autonomy-guard: Level: 0 is on request only and this is a "
              "scheduled run. Do nothing; log why and stop.")
    if notes_cmd and notes_cmd in command and level < 3:
        block("autonomy-guard: PMS notes need Level 3; AUTONOMY.md is at Level %d. "
              "List the note as proposed instead." % level)
    sys.exit(0)


if __name__ == "__main__":
    main()
