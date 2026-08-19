---
description: Build a weighted decision matrix to choose a target journal for a manuscript
---

Run the `journal-selector` skill on: $ARGUMENTS

If no manuscript path or topic was given above, ask for one before doing anything else.

Follow the skill's seven steps in order. Two of them are gates, not suggestions:

- **Do not research before Step 2 is answered.** The author's criteria, institutional agreements,
  APC budget, and publisher vetoes decide what is even worth looking up. Ask; do not assume.
- **Do not recommend a winner before Step 6.** A top score is not evidence the journal publishes
  this kind of work. Verify it against papers it actually published.

Every number in the matrix needs a source and a date in its note. Anything you could not verify is
`null` plus a manual-check item with the URL — never a plausible guess.
