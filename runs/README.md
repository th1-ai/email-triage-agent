# runs/

The agent's own record. Everything here except this file and `.gitkeep` is git-ignored, because it can hold guest data.

| File | Written at | What it is |
|---|---|---|
| `LOG.md` | every level | One entry per run, newest last. The last entry is the latest run summary; other agents read it there. The agent reads the last entries before it acts, so it does not report or write the same thing twice. |
| `handoff/email-triage-agent.md` | Level 2 and 3 | The reply queue for the drafting agents and the PMS notes that wait for your approval. Replaced on each run. |

## `LOG.md` entry format

```
## 2026-01-15T07:00Z | scheduled | Level 1
- Checked: primary 14, bookings 9, rentals 0 | window since 2026-01-14
- Not checked: none
- Flagged: thread <id> booking-inquiry; thread <id> needs-attention
- Notes written: res <id> "<note text>" verified
- Notes shadow: none
- Notes proposed: res <id> allergy (sensitive)
- Errors: none
- Needs you: 1 - allergy note proposed for res <id>
```

Use thread, message and reservation ids, counts and categories. Do not put guest names, addresses or message text in the log.

A run that stops at the kill switch writes one line: `## <timestamp> | scheduled | Level PAUSED | stopped: <why>`, where the reason is the value found, for example `Level: PAUSED`, `Level: 0 and the run is scheduled`, or `AUTONOMY.md missing`.

## `handoff/email-triage-agent.md` format

```
# email-triage handoff - 2026-01-15T07:00Z - Level 2

## For booking-inquiry-agent
- thread <id> | [bookings] | <guest name> | <dates> | <party size> | "<body excerpt>"

## For email-draft-agent
- thread <id> | [primary] | <sender> | <the ask> | PMS: res <id> or "not verified"

## PMS notes awaiting approval
- res <id> | "<note text>" | <why it was not written> | <exact notes command>
```

The two drafting sections are read by [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) and [`email-draft-agent`](https://github.com/th1-ai/email-draft-agent) when they are installed in the same project. Suspected-phishing mail never goes in this file.
