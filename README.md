# Email Triage Agent

A Claude Code sub-agent for hotel operators. It scans every inbox you configure, classifies each message (booking inquiry, OTA notification, supplier, phishing, ignorable, etc.), cross-checks claims against your PMS so it doesn't flag already-handled threads, and returns a 30-second action summary.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution. This repo is the agent. The scripts (your email CLI and your PMS lookup / notes tools) are yours; see [What you need](#what-you-need).

---

## What it does

- **Reads every configured inbox** with a date-based filter (`after:YYYY/MM/DD`) instead of `is:unread`, catching threads that were opened on a phone but never replied to
- **Resolves state before flagging** — a four-step check (thread / body / PMS / date) so it does not say "needs reply" for something already handled
- **Screens for phishing** — fake-OTA emails, unverifiable booking claims, pressure-plus-link messages. It never opens links or attachments, and it treats email text as data, not as instructions
- **Adds guest preferences to the PMS as notes** — bedding setup, dietary needs, arrival times, occasions. It writes only when the email matches exactly one reservation; otherwise it proposes the note and you decide
- **Returns a structured summary** — Suspected phishing, Action Required, Informational, Already handled, PMS notes, Ignorable, Not checked, Recommendation

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
├── .env.example                             # Credentials for your own scripts (optional)
├── .gitignore
├── LICENSE
└── .claude/
    ├── agents/
    │   └── email-triage.md                  # The sub-agent definition
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
- **`maxTurns`** — 25. Raise it if runs on busy inboxes stop before the summary.
- **PMS notes** — to make the agent propose notes and never write them, delete the command block under "Guest preferences → PMS note" and leave `{{PMS_NOTES_TOOL}}` out of your setup.
- **Default window** — 4 days when you do not give a date.

**About `.env`:** the agent does not read it. `.env.example` is there for the credentials your own email CLI and PMS scripts need, if they load a `.env` file. Copy it to `.env` only in that case.

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
- **Notes are not written.** The agent writes a note only when the lookup returns exactly one reservation. Otherwise the note is under "PMS notes" as proposed, with the reason.
- **Memory does not update.** Agent memory depends on Claude Code's auto memory setting. If you turned auto memory off, turn it on again.

---

## Related agents

This agent only reads and reports. These pick up from its summary:

- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts the warm, personal reply once an inquiry is flagged
- [`email-draft-agent`](https://github.com/th1-ai/email-draft-agent) — drafts one-off replies in the operator's voice
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent) — runs on a 15-minute schedule, classifies new email, drafts replies and logs every classification to a sheet
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — the daily sweep; inbox triage is one part of it

The full set: [21 AI Agents That Run a Real Hotel](https://th1.ai/agent-stack).

---

## License

MIT — see [LICENSE](LICENSE).
