# journal-selector

A Claude Code plugin that turns "where should I submit this paper?" into a decision you can audit:
named criteria, declared weights, a score per cell with the evidence behind it, and an explicit list
of what could not be verified.

It does not pick a journal for you. It produces a matrix you can re-weight and rerun.

## Install

```
/plugin marketplace add dariohhossoda/journal-selector
/plugin install journal-selector
```

Or point at a local clone:

```
/plugin marketplace add /path/to/journal-selector
/plugin install journal-selector
```

## Use

```
/journal-select submission/article.tex
/journal-select a paper on urban flood nowcasting from weather radar, ML-based early warning
```

Or just ask — the skill triggers on "where should I submit this", "choose a target journal",
"compare these journals", and similar.

The run is interactive by design. It asks which criteria matter and in what order, which
institutional agreements your library holds, whether there is an APC ceiling, and whether any
publisher is off the table. Nothing about your institution is hardcoded, because those terms change
every year and differ per author.

## What you get

A Markdown document with:

- the scoring model, including where the weights came from and that they are adjustable
- the full matrix, raw value → 0–10 score per criterion, weighted total
- an evidence line per cell: value, source, date
- vetoed candidates listed separately with the score they would have had
- a Top 3 with the criteria that actually decided each position
- near-ties flagged automatically, because a 0.07 gap is a coin flip and not a ranking
- a scope verification of the winner against papers it actually published recently
- a manual-checks list — every URL that blocked automated fetching, every unconfirmed deadline

## How scoring works

Criteria are weighted (renormalized to 100%) and each is mapped to 0–10:

- `scale` — you assign 0–10 directly, with the anchors written into the criterion so a reader knows
  what a 6 means.
- `numeric` — linear normalization, `higher_better` (impact factor) or `lower_better` (APC, days to
  decision), against the best in the set or an explicit reference.

A **veto** removes a candidate from contention entirely — predatory-publishing flags, wrong indexing,
a length limit the manuscript cannot meet. A **low score** expresses a strong preference while keeping
the candidate visible, so you can see what the preference cost you.

The arithmetic runs in `scripts/score_matrix.py` — stdlib Python 3.9+, no dependencies — so the
numbers are reproducible rather than model-generated:

```bash
python3 skills/journal-selector/scripts/score_matrix.py candidates.json --check
python3 skills/journal-selector/scripts/score_matrix.py candidates.json -o journal_candidates.md
```

`skills/journal-selector/templates/candidates.example.json` is a real filled-in case (10 journals,
3 criteria) you can copy and edit.

## Design decisions

**Nothing about your institution is baked in.** Read-and-publish agreements are scoped by acceptance
date, by title list, and often by author role; they are renegotiated annually. A hardcoded list would
be wrong for most users and quietly wrong for you next year. So the skill asks, every run.

**Unverified is a state, not a gap.** Publisher pages block bots — ScienceDirect returns HTTP 403 to
most automated requests, and it does so on exactly the special-issue and calls-for-papers pages that
matter. When that happens the cell is `null` with a note, and the URL goes on the manual-checks list
with the specific question to answer. A number that is plausible is worse than a hole that is honest.

**Include candidates you expect to lose.** A matrix where every option is viable cannot show why the
winner won.

**Lookups are delegated; judgement is not.** Fetching the published facts for ten journals is
mechanical and voluminous, so it runs on a cheap subagent (`agents/venue-fact-finder.md`, one per
candidate, `WebSearch` and `WebFetch` only). That keeps forty publisher pages out of the main
context. But the agent's output has no score field, deliberately: turning "APC is 3,600 USD" into a
0–10 value needs the anchors agreed with the author, and a weak model asked for a number is exactly
the thing that invents one. It reports a `fetch_status` per fact, and anything short of `fetched`
travels into the cell note as a caveat. The facts behind the Top 3 get re-verified by hand before
anything is recommended — an error in row nine is noise, the same error in row one sends the
manuscript to the wrong journal.

**A high score is not evidence of fit.** Aims-and-scope statements are marketing. The skill verifies
the winner against 3–5 papers it published in the last few years on the same problem — and reports it
plainly when no close precedent exists, since that cuts both ways.

## Layout

```
.claude-plugin/           plugin.json, marketplace.json
.github/                  issue forms and PR checklist
agents/
  venue-fact-finder.md    cheap retrieval subagent, one per candidate journal
commands/
  journal-select.md       /journal-select
skills/journal-selector/
  SKILL.md                the seven-step process
  references/
    criteria-catalog.md   criteria menu: how to measure each, how each goes wrong
    research-protocol.md  where the facts live; known fetch blocks
    scoring-model.md      the math, input schema, veto vs penalty, sensitivity
  scripts/
    score_matrix.py       deterministic scorer and Markdown renderer
  templates/
    candidates.example.json
    decision-matrix.template.md
```

## Provenance

Extracted from an actual journal-selection run for a manuscript on radar-based urban flood
nowcasting: ten candidate journals, three weighted criteria, a scope verification of the winner, and
a manual-check list of everything the publisher's own site refused to serve to a bot. The example
input reproduces that matrix.

## License

MIT — see [LICENSE](LICENSE).
