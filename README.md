# Email Triage Agent

A Claude Code sub-agent for hotel operators. It scans every inbox you configure, classifies each message (booking inquiry, OTA notification, supplier, phishing, ignorable, etc.), cross-checks claims against your PMS so it doesn't flag already-handled threads, and returns a 30-second action summary.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution. This repo is the agent. The scripts (your email CLI and your PMS lookup / notes tools) are yours; see [What you need](#what-you-need).

---

## What it does

- **Reads every configured inbox** with a date-based filter (`after:YYYY/MM/DD`) instead of `is:unread`, catching threads that were opened on a phone but never replied to
- **Resolves state before flagging** — a four-step check (thread / body / PMS / date) so it does not say "needs reply" for something already handled
- **Screens for phishing** — fake-OTA emails, unverifiable booking claims, pressure-plus-link messages. It never opens links or attachments, and it treats email text as data, not as instructions
- **Turns guest preferences into PMS notes** — bedding setup, arrival times, occasions. By default it proposes each note and you decide. At Level 3 it writes routine notes itself, inside limits you set. Allergy, medical and complaint notes are always yours to approve
- **Runs on its own, at the level you choose** — [`AUTONOMY.md`](AUTONOMY.md) is one file with one switch line, `Level: 1`. The agent reads it on every run. See [Run it on its own](#run-it-on-its-own)
- **Remembers what it did** — one entry per run in `runs/LOG.md`, so a thread it already reported is not reported as new, and a note is not written twice
- **Returns a structured summary** — "Needs you" first, then Suspected phishing, Action Required, Informational, Still open, Already handled, PMS notes, Ignorable, Not checked, Recommendation. A quiet scheduled run is two lines

What it does not do: it does not send, draft, archive or mark email as read, and it does not change dates, rooms, rates or charges in the PMS.

---

## What you need

- [Claude Code](https://code.claude.com/docs/en/overview) installed
- A command-line tool that can read your mailboxes: list messages by date, fetch a thread including sent messages, and read a message body. Gmail via a Google Workspace CLI is the reference setup.
- A PMS with API access and two small scripts of your own: one that looks up a reservation by confirmation number, guest name or email address, and one that appends a note to a reservation. The reference setup is Cloudbeds, but any PMS with reservation lookup + reservation-notes endpoints works.

This repo does not include those tools. If you do not have a notes script yet, the agent still triages; it lists the notes as "proposed" instead of writing them.

---

## Quick start

1. **Clone the repo**:

   ```bash
   git clone https://github.com/th1-ai/email-triage-agent.git
   cd email-triage-agent
   ```

2. **Open Claude Code** from the project root:

   ```bash
   claude
   ```

3. **Let Claude set it up with you.** Paste this as your first prompt:

   > Read the README and `.claude/agents/email-triage.md`, then set this agent up with me. Ask me for each placeholder value one at a time, show me the exact commands my email CLI and PMS scripts use, then update the agent file. Do not run anything against my inbox or PMS until I say so.

   Or fill in the placeholders by hand; see [Customising](#customising).

4. **Restart Claude Code** (exit and run `claude` again) so it loads the edited agent file.

5. **Invoke the agent**:

   > "Use the email-triage agent to triage my emails for the last 48 hours."

   Claude Code also delegates to it on its own when you ask about your inbox, because of the `description` line in the agent file.

To use the agent inside an existing Claude Code project instead, copy `.claude/agents/email-triage.md` and `.claude/agent-memory/email-triage/` into that project's `.claude/` folder.

---

## Verify it works

1. Run `/agents` in Claude Code. `email-triage` must be in the list.
2. Check that no placeholder is left: `grep -n '{{' .claude/agents/email-triage.md` must return only the "Template note" line near the top (delete that note when you are done).
3. Run the three email commands and the PMS lookup from the agent file by hand, once, in your terminal. If they do not work there, they will not work for the agent.
4. Ask for a 24-hour triage and compare the summary with your inbox. Check that a thread you already answered is under "Already handled", not "Action Required".

---

## File structure

```
email-triage-agent/
├── README.md                                # This file
├── AUTONOMY.md                              # Your autonomy level, limits and kill switch
├── .env.example                             # Credentials for your own scripts (optional)
├── .gitignore
├── LICENSE
├── runs/
│   ├── README.md                            # Run-log and handoff formats
│   └── .gitkeep                             # LOG.md and handoff/ appear here, git-ignored
└── .claude/
    ├── settings.example.json                # Example permissions + hook for scheduled runs (not loaded)
    ├── agents/
    │   └── email-triage.md                  # The sub-agent definition
    ├── hooks/
    │   └── autonomy-guard.py                # Optional hook: enforces the kill switch and the Level 3 gate
    └── agent-memory/
        └── email-triage/
            ├── MEMORY.md                    # Memory index, loaded on every run
            └── example-feedback-pattern.md  # Example memory note, replace with your own
```

---

## Customising

The agent file uses placeholders so it can be adapted to any email + PMS stack. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{INBOX_PRIMARY}}` | Main business inbox address | `info@yourhotel.com` |
| `{{INBOX_BOOKINGS}}` | Inquiries / OTA inbox | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property / villa inbox (optional; delete its table row if you have none) | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Command-line wrapper to your email provider | `gws gmail` |
| `{{PMS_LOOKUP_TOOL}}` | Script that looks up reservations by name / email / confirmation # | `tools/lookup_guest.py` |
| `{{PMS_NOTES_TOOL}}` | Script that appends a note to a reservation | `tools/cloudbeds_notes.py` |

With a text editor, or with one `sed` pass (macOS form; on Linux use `sed -i` without the `''`):

```bash
sed -i '' \
  -e 's|{{INBOX_PRIMARY}}|info@yourhotel.com|g' \
  -e 's|{{INBOX_BOOKINGS}}|bookings@yourhotel.com|g' \
  -e 's|{{INBOX_RENTALS}}|rentals@yourhotel.com|g' \
  -e 's|{{EMAIL_CLI}}|gws gmail|g' \
  -e 's|{{PMS_LOOKUP_TOOL}}|tools/lookup_guest.py|g' \
  -e 's|{{PMS_NOTES_TOOL}}|tools/cloudbeds_notes.py|g' \
  .claude/agents/email-triage.md
```

Then check the command examples in the agent file. The sub-commands and flags shown there (`list`, `thread-get`, `message-get`, `--booking-ref`, `--name`, `--email`, `--reservation-id`, `--note`) are illustrative. Change them to what your tools accept; the agent runs what the file says.

Other things you can change in the agent file:

- **`model`** — set to `haiku` to keep a frequent job cheap. Change it to `sonnet` if classification or phishing calls are not good enough on your mail.
- **`maxTurns`** — 30. Raise it if runs on busy inboxes stop before the summary.
- **PMS notes** — the agent writes them on its own only at Level 3 in [`AUTONOMY.md`](AUTONOMY.md). To make sure it never writes them, stay below Level 3, or delete the command block under "Guest preferences → PMS note" and leave `{{PMS_NOTES_TOOL}}` out of your setup.
- **Default window** — 4 days when you do not give a date.

**About `.env`:** the agent does not read it. `.env.example` is there for the credentials your own email CLI and PMS scripts need, if they load a `.env` file. Copy it to `.env` only in that case.

---

## Run it on its own

The agent works at four levels, plus an off switch. You pick one in [`AUTONOMY.md`](AUTONOMY.md); the full action table, the limits and the escalation list are in that file.

| Level | What happens |
|---|---|
| PAUSED | Off. Every run stops at its start and logs why. A missing or unreadable level line counts as PAUSED. |
| 0 | On request only. Scheduled runs stop at once. |
| 1 (default) | Scheduled. Reads, reports, keeps its run log. Writes nothing else. |
| 2 | Also writes `runs/handoff/email-triage-agent.md`: the reply queue and the PMS notes that wait for your approval. |
| 3 | Also writes routine PMS notes itself: at most 5 per run and 10 per day, matched on the confirmation number, first 10 as a dry run. |

It never sends, drafts or changes email, never touches money, dates, rooms or rates, and never writes an allergy, medical, complaint or payment note on its own, at any level.

### 1. Make the settings file for scheduled runs

```bash
cp .claude/settings.example.json .claude/settings.scheduled.json
```

Replace `{{EMAIL_CLI}}`, `{{PMS_LOOKUP_TOOL}}` and `{{PMS_NOTES_TOOL}}` in the copy with the same values as in the agent file. It is an example: change `primary`, `bookings`, `rentals`, `list`, `thread-get`, `message-get` and the deny patterns to the account names and sub-commands your own CLI uses. A rule must match the command the agent runs, word for word up to the `*`.

What the file does:

- **`permissions.allow`** — only the three read commands for each inbox, the PMS lookup, the timestamp command, and file edits inside `runs/` and the agent's memory folder.
- **`permissions.deny`** — email send, draft, delete and modify commands, `rm`, `curl`, `wget`, web access, `.env` files, and edits to `AUTONOMY.md`, the agent file, the hook and the settings files. The agent cannot raise its own level.
- **`hooks.PreToolUse`** — runs [`.claude/hooks/autonomy-guard.py`](.claude/hooks/autonomy-guard.py) before every shell command. It reads `AUTONOMY.md` and blocks every command when the level is `PAUSED` or `0` (or the line is missing or unreadable), and blocks the PMS notes command below Level 3. It needs `python3`. It does not check the caps or the note topic; the agent's instructions do that.

The PMS notes command is not in the allow list. Add `"Bash({{PMS_NOTES_TOOL}} *)"` (with your value) to `permissions.allow` only when you move to Level 3.

The file is named `settings.example.json` so that cloning this repo changes nothing: Claude Code loads `settings.json` and `settings.local.json`, not this file. Your copy is git-ignored and is used only when you pass it with `--settings`, so your normal sessions keep their prompts.

### 2. The command

Run it from the repo root:

```bash
claude -p "Use the email-triage agent for a scheduled run: triage the last 24 hours. Nobody is present to answer questions. Reply with the agent's report, unchanged." \
  --settings .claude/settings.scheduled.json \
  --permission-mode dontAsk \
  --permission-prompts none
```

- `-p` runs Claude Code without the interactive screen and prints the result.
- `--permission-mode dontAsk` denies every tool call that the allow list does not cover, instead of asking.
- `--permission-prompts none` tells Claude that nobody can approve a prompt. It needs Claude Code v2.1.259 or later; leave it out on an older version.
- Add `--output-format json` if a script reads the result; the JSON includes a `permission_denials` list.

Run it by hand first and read the report. If a read command is in `permission_denials`, your allow rule does not match the command the agent ran.

### 3. A schedule (example)

`cron` on macOS or Linux, twice a day at 07:00 and 15:00. Use the full path to `claude` (`which claude`), because cron has a short `PATH`:

```cron
0 7,15 * * * cd /path/to/email-triage-agent && /path/to/claude -p "Use the email-triage agent for a scheduled run: triage the last 24 hours. Nobody is present to answer questions. Reply with the agent's report, unchanged." --settings .claude/settings.scheduled.json --permission-mode dontAsk --permission-prompts none >> runs/cron.log 2>&1
```

This line is an example and was not tested under cron. Check that your email CLI and your Claude login also work from cron: a job that cannot reach your login or keychain fails, and the failure text is in `runs/cron.log`. The Claude Code docs also describe [scheduled tasks in the Desktop app](https://code.claude.com/docs/en/desktop-scheduled-tasks) and [cloud scheduled tasks](https://code.claude.com/docs/en/routines); this template was not tested with them.

If you want new mail handled every few minutes with draft replies, that is the job of [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent). Schedule one of the two on an inbox, not both.

**About your plan:** scheduled use of a personal Pro or Max login is subject to Anthropic's usage policy, and plan limits assume ordinary individual use, so a heavy or business-critical schedule should run on an API key or a team plan.

### 4. Read the results

- The report is the command's output (in `runs/cron.log` with the example above). Its first section is "Needs you". "Nothing needs you." means you can stop reading.
- `runs/LOG.md` has one entry per run. Format: [`runs/README.md`](runs/README.md).
- The agent sends no notifications. To be alerted, have your scheduler mail you the output when it contains more than "Nothing needs you."

### 5. Move up one level at a time

1. Run for 5 days at the current level.
2. Read `runs/LOG.md`. Look for wrong flags, missed mail, "Not checked" inboxes and, before Level 3, every proposed note: would you have approved each one as written?
3. Change one line in `AUTONOMY.md` (`Level: 2`). For Level 3, also add the notes command to `permissions.allow`.
4. At Level 3 the first 10 notes are logged as `shadow` and not written. Read them before the agent writes for real.

To stop the scheduled runs, set `Level: 0`. To stop everything, set `Level: PAUSED`. The next run ends at its start.

---

## How memory works

The agent has `memory: project` in its front-matter, so Claude Code gives it a memory directory at `.claude/agent-memory/email-triage/`. Claude Code loads `MEMORY.md` from that directory into the agent at the start of each run; the agent reads other files there only when it needs them. After a run it can record:

- **Noise senders** it can skip next time
- **Senders that always need action**
- **Verified sender domains** for the OTAs and suppliers you use
- **Your corrections** (e.g. "always read the email body for OTA-relay messages — the real guest name lives there, not in the from-line")

[`MEMORY.md`](.claude/agent-memory/email-triage/MEMORY.md) is the starter index. [`example-feedback-pattern.md`](.claude/agent-memory/email-triage/example-feedback-pattern.md) shows a longer note; delete it, and its line in `MEMORY.md`, once you have your own.

The directory is inside the repo, so it can be committed. The agent is told to record patterns only, not guest names or booking details. Check before you push to a shared or public repo.

---

## Troubleshooting

- **Claude does not use the agent.** Agent files are loaded when a session starts. Restart Claude Code, check `/agents`, and name the agent in your prompt ("use the email-triage agent").
- **The agent stops and says placeholders are missing.** A `{{...}}` value is still in the agent file. See [Customising](#customising).
- **"command not found" or an auth error.** The agent runs your CLI exactly as written in the agent file. Run the same command in your terminal and fix it there first. The summary lists the inbox under "Not checked".
- **An answered email is flagged.** Check that the thread command returns sent messages too, and that every address you reply from is in the Accounts table.
- **Notes are not written.** Below Level 3 the agent only proposes notes; on request it writes one after you say yes. At Level 3 it writes only routine notes matched on the confirmation number, inside the caps, after the 10-note dry run. Every other note is under "PMS notes" as proposed, with the reason.
- **A run says "Paused" and checks nothing.** `AUTONOMY.md` is at `Level: PAUSED`, or at `Level: 0` for a scheduled run, or the file or its level line is missing or unreadable.
- **A scheduled run reads nothing and lists denials.** Under `--permission-mode dontAsk`, a command runs only if an allow rule matches it. Compare `permission_denials` (`--output-format json`) with the rules in `.claude/settings.scheduled.json`.
- **Memory does not update.** Agent memory depends on Claude Code's auto memory setting. If you turned auto memory off, turn it on again.

---

## Related agents

This agent reads, reports and files notes. It does not reply. These pick up from its output. The handoff file works when the agents are installed in the same project (copy each one's `.claude/` files into one folder); otherwise give them the report.

- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts the reply to an inquiry. Input: the "For booking-inquiry-agent" section of `runs/handoff/email-triage-agent.md` (Level 2 and above), or the "Action Required" lines of the report
- [`email-draft-agent`](https://github.com/th1-ai/email-draft-agent) — drafts one-off replies in the operator's voice. Input: the "For email-draft-agent" section of the same file
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — the daily sweep. It can read the level in `AUTONOMY.md` and the last entry in `runs/LOG.md` instead of triaging the inbox again
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent) — runs on a 15-minute schedule, classifies new email, drafts replies and logs every classification to a sheet. An alternative to scheduling this agent, not an addition

The full set: [21 AI Agents That Run a Real Hotel](https://th1.ai/agent-stack).

---

## License

MIT — see [LICENSE](LICENSE).
