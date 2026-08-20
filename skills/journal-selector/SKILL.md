---
name: journal-selector
description: "Choose a target journal for a manuscript through an explicit weighted decision matrix instead of a hunch. Elicits the author's own criteria and priority order, researches candidate venues (impact metrics, open special issues, APC and institutional agreements, scope fit), scores every cell with a cited note, runs a deterministic scorer, verifies the winner's scope against what the journal actually publishes, and writes an auditable decision document. Triggers on: where should I submit, journal selection, choose a journal, target journal, journal candidates, decision matrix for journals, special issue search, APC comparison, venue selection, submission target."
---

# Journal Selector

Turn "where do I submit this?" into a record someone else could audit: named criteria, declared weights, a score per cell with the evidence behind it, and an explicit note of what could not be verified.

The output is a Markdown document. It is not a recommendation the author is expected to accept blindly — it is a matrix they can re-weight and rerun.

## Non-negotiables

1. **Never invent a number.** Impact factors, APC values, special-issue deadlines, and agreement coverage are all facts to be looked up, and each one carries a note saying where it came from and as of when. A cell you could not verify is `null` with a note, not a guess.
2. **Never hardcode the author's constraints.** Institutional agreements, publisher preferences, and budget are asked at the start of every run (Step 2). There is no default institution and no default blocklist. What was true for one author last year is not true for another author now.
3. **Weights are the author's decision.** Propose numbers, show what they imply, and let the author change them. Record the weights actually used in the output.
4. **Say what is unverified.** Publisher pages block automated fetching routinely (ScienceDirect returns HTTP 403 to most tools). When that happens, say so in the cell note and list the URL under manual checks — do not silently drop the criterion or fill it from memory.

## Process

### Step 1 — Frame the manuscript

Read what exists: the manuscript, abstract, or a description from the author. Establish and state back:

- Subject and method in one or two sentences.
- The claimed contribution — what is new.
- **Alternative framings.** Most papers can be pitched to more than one community (e.g. applied hydrology vs. disaster risk reduction vs. remote sensing). Different framings reach different journals, and this decides which candidates are even eligible. Ask which framing the author wants, or carry two.
- Prior related publications by the same group. Publishing a follow-up in the journal that took the first paper is a real, nameable advantage.

### Step 2 — Elicit criteria, constraints and weights

Ask the author, in this order:

1. **Which criteria matter**, and in what priority order. Offer the catalog in `references/criteria-catalog.md` as a menu — do not impose the whole list.
2. **Institutional and publisher constraints.** Ask explicitly, every run:
   - Which read-and-publish / transformative agreements does the author's institution hold, if any? (In many countries these are national consortium deals; the author or their library knows, and the terms change yearly.)
   - Is there an APC budget, and what is the ceiling?
   - Any publisher or journal the author will not submit to — and is that a hard veto (excluded outright) or a heavy penalty (stays in the matrix with a low score)?
   - Is open access required by a funder or mandate?
3. **Weights.** If the author gave only a priority order, propose numeric weights that express it (a common translation of a three-criterion order is 50/30/20), state plainly that the numbers are your reading of their order, and ask them to confirm or adjust. Record whatever is agreed.

Do not proceed to research until the criteria and constraints are settled — they determine what is worth researching.

### Step 3 — Build the candidate list

Aim for 8–12 journals. Draw them from:

- The manuscript's own reference list — journals it already cites heavily are journals whose readers care.
- Where comparable recent papers on the same problem appeared.
- The journal that published the group's prior related work.
- Society journals in the field, plus one or two aspirational high-impact venues so the matrix has a real ceiling.
- Any journal the author names.

Include venues you expect to lose. A matrix where every candidate is plausible cannot show *why* the winner won.

### Step 4 — Research each cell

Follow `references/research-protocol.md`: what to look up for each criterion, which sources are authoritative, and what to do when a page cannot be fetched.

**Delegate the lookups.** Dispatch one `venue-fact-finder` subagent per candidate journal, in parallel — send them in a single message so they run concurrently. Each one gets its journal name, the manuscript topic in one sentence (so it can judge which special issues are plausibly related), and the list of facts you actually need for the criteria agreed in Step 2. It returns a JSON object: one record per fact, each with a value or `null`, a source URL, a `fetch_status`, and the date checked.

That agent runs on a cheap model and does retrieval only. Two consequences:

- **It never scores, and neither should you take its word as a score.** Its output has no score field. Converting "APC is 3,600 USD" or "special issue exists, deadline unconfirmed" into a 0–10 value needs the anchors and criteria from Step 2, which the agent was never given. That conversion is yours.
- **A `fetch_status` other than `fetched` is not a value.** `search_only` is weaker evidence and must be labelled as such in the cell note. `blocked` and `not_found` mean the cell is `null` plus a manual-check item — not a number you fill in from what sounds right.

Doing the fetches yourself is fine for a two-candidate comparison. Past that, the delegation is what keeps forty publisher pages out of the main context.

Write the scores into a JSON file shaped like `templates/candidates.example.json` — one object per candidate, one entry per criterion, each with a `note` recording the source and the date. Carry the agent's `source_url`, `date_checked`, and any `fetch_status` caveat into that note. The note field is not optional decoration; it is the audit trail, and the renderer emits it as an evidence list.

### Step 5 — Score

```bash
python3 scripts/score_matrix.py candidates.json --check          # validate first
python3 scripts/score_matrix.py candidates.json -o journal_candidates.md
```

Stdlib Python 3.9+, no dependencies. The scoring math and the meaning of each field are in `references/scoring-model.md`. Run the script rather than doing the arithmetic in your head — the point of a deterministic scorer is that a reader can rerun it and get the same numbers.

The rendered document has `<!-- fill in -->` placeholders. Fill them.

### Step 6 — Spot-check the Top 3, then verify the winner's scope

**Spot-check first.** Re-verify by hand the facts behind the top three rows — impact metric, cost, and any special issue that moved a candidate up. Three journals is cheap, and it is where an error would actually change the decision: a wrong value in row nine is noise, the same error in row one sends the manuscript to the wrong journal. Open the `source_url` the agent reported and confirm the value is there. If a spot-check contradicts the matrix, fix the input and rerun Step 5 rather than patching the rendered table.

A high score is not evidence a journal will consider the paper. Before recommending the top candidate, confirm it publishes this kind of work *in practice*:

- Find 3–5 papers it published in the last ~3 years on the same problem or with the same method, and cite them by title and year.
- Check the aims-and-scope for anything that disqualifies the paper outright (e.g. a physics-based-modelling-only special issue when the paper is data-driven).
- Say plainly if you find **no** close precedent. That cuts both ways — it strengthens the novelty claim and weakens the bet on acceptance. The author needs both halves.

If Step 6 disqualifies the winner, go back to the matrix rather than quietly recommending #2.

### Step 7 — Report and hand off

The document ends with:

- **Top 3**, each with the one or two criteria that actually decided its position.
- **Near-ties**, which the scorer flags automatically. A 0.07 gap is not a ranking, it is a coin flip — name it as one and say which framing would break the tie.
- **Manual checks before submitting** — every URL that returned 403, every deadline marked "to confirm", every agreement whose terms the author should verify with their library. Be specific: a checklist item without a URL is not actionable.
- **Decision**, with the date, once the author picks.

Then tell the author what was written and where, and stop. Choosing the venue is theirs.

## Files

- `../../agents/venue-fact-finder.md` — cheap retrieval subagent, one per candidate (Step 4).
- `scripts/score_matrix.py` — deterministic scorer and Markdown renderer.
- `templates/candidates.example.json` — a filled-in real example (10 candidates, 3 criteria).
- `templates/decision-matrix.template.md` — the document skeleton, if writing it by hand.
- `references/criteria-catalog.md` — criteria menu and how to measure each one.
- `references/research-protocol.md` — where the facts come from, and known fetch blocks.
- `references/scoring-model.md` — the math, weight elicitation, veto vs. penalty.
