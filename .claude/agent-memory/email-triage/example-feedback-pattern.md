---
name: Date-based scan catches already-read-but-unhandled threads
description: Scanning inboxes with `after:YYYY/MM/DD` (not `is:unread`) reveals emails that were opened but not replied to
type: feedback
---

> **Example pattern.** This file shows the *shape* of a useful agent-memory note. Replace it with your own learnings as the agent runs.

When triaging a 48-hour window with a date-based query (e.g. `after:2026/04/29`), the agent should expect to find threads that look like:

- Staff scheduling reply asking the operator to confirm specific dates
- Guest extension request asking about availability + add-on services
- Upgrade-acceptance reply asking about check-in window
- Early check-in request following an arrival logistics email
- OTA-relay arrival-time notification (e.g. "arriving at 8pm")

All of these typically have been **read** (so they fall outside the `is:unread` filter) but **have not yet been replied to**. They are live, open threads requiring action.

**Why:** `is:unread` is insufficient because operators routinely scan emails on their phone and the messages get marked read before the operator has time to reply. A date-based scan catches these.

**How to apply:** Always use `after:YYYY/MM/DD` filters for triage, never rely on `is:unread`. Then check thread status (latest message from guest or from us?) before flagging anything as "needs action".
