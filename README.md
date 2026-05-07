# Email Triage Agent

A Claude Code sub-agent for hotel operators. It scans every inbox you configure, classifies each message (booking inquiry, OTA notification, supplier, phishing, ignorable, etc.), cross-checks claims against your PMS so it doesn't flag already-handled threads, and returns a 30-second action summary.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

---

## What it does

- **Reads every configured inbox** with a date-based filter (`after:YYYY/MM/DD`) instead of `is:unread`, catching threads that were opened on a phone but never replied to
- **Resolves state before flagging** — a four-step check (thread / PMS / body / date) ensures it never says "needs reply" for something already handled
- **Detects phishing** — fake-OTA emails, unverifiable booking claims, and unsolicited links are flagged before classification
- **Pushes guest preferences to the PMS** — bedding setup, dietary needs, arrival times, occasions: when an email mentions one, the agent appends a note to the matching reservation so check-in staff see it
- **Returns a structured summary** — Action Required, Informational, Ignorable, Recommendation

---

## What you need

- [Claude Code](https://claude.ai/code) installed
- One or more email accounts you can read programmatically (Gmail via the Google Workspace CLI is the reference setup)
- A PMS with API access — the agent calls a `lookup_guest`-style tool and a `notes`-style tool. The reference setup is Cloudbeds, but any PMS with reservation lookup + reservation-notes endpoints works.

---

## Quick start

1. **Clone the repo** into a Claude Code project:

   ```bash
   git clone https://github.com/th1-ai/email-triage-agent.git
   cd email-triage-agent
   ```

2. **Copy the env template** and fill it in:

   ```bash
   cp .env.example .env
   ```

3. **Edit [`.claude/agents/email-triage.md`](.claude/agents/email-triage.md)** — replace the placeholders described in [Customising](#customising) with the wrappers your setup uses.

4. **Open in Claude Code** from the project root:

   ```bash
   claude
   ```

5. **Invoke the agent**:

   > "Triage my emails for the last 48 hours."

   Claude Code will pick up the `email-triage` sub-agent automatically because of the front-matter `description` line.

---

## File structure

```
email-triage-agent/
├── README.md                                # This file
├── .env.example                             # Inboxes, PMS auth, etc.
├── .gitignore
├── LICENSE
└── .claude/
    ├── agents/
    │   └── email-triage.md                  # The sub-agent definition
    └── agent-memory/
        └── email-triage/
            └── example-feedback-pattern.md  # Example "memory note" — replace with your own
```

---

## Customising

The agent file uses placeholders so it can be adapted to any email + PMS stack. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{INBOX_PRIMARY}}` | Main business inbox address | `info@yourhotel.com` |
| `{{INBOX_BOOKINGS}}` | Inquiries / OTA inbox | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property / villa inbox (optional) | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Command-line wrapper to your email provider | `gws gmail` |
| `{{PMS_LOOKUP_TOOL}}` | Script that looks up reservations by name / email / confirmation # | `tools/lookup_guest.py` |
| `{{PMS_NOTES_TOOL}}` | Script that appends a note to a reservation | `tools/cloudbeds_notes.py` |

You can do this with any text editor or with one `sed` pass:

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

---

## How memory works

The agent uses Claude Code's per-agent memory at `.claude/agent-memory/email-triage/`. After each triage run, it can save:

- **Feedback** — patterns to repeat or avoid (e.g. "always read the email body for OTA-relay messages — the real guest name lives there, not in the from-line")
- **Project notes** — context that affects classification (e.g. "vendor X switched accounting firms in March — new sender domain is legitimate")
- **References** — pointers to external systems (e.g. "stale-lead chase logic lives in the CRM-pipeline agent")

[`example-feedback-pattern.md`](.claude/agent-memory/email-triage/example-feedback-pattern.md) shows the recommended format. Delete it once you have your own.

---

## Related agents

This agent works well alongside:

- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts the warm, personal reply once an inquiry is flagged
- [`email-draft-agent`](https://github.com/th1-ai/email-draft-agent) — writes one-off replies in the operator's voice
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent) — runs triage on a 15-minute schedule and logs every classification to a sheet

---

## License

MIT — see [LICENSE](LICENSE).
