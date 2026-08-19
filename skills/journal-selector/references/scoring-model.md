# Scoring model

What `scripts/score_matrix.py` computes, and how to set up its input.

## Input file

JSON, stdlib-only parsing. See `../templates/candidates.example.json` for a filled example.

```json
{
  "title": "Journal candidates — decision matrix",
  "date": "2026-07-22",
  "topic": "one or two sentences on the manuscript",
  "criteria": [
    {
      "id": "impact",
      "label": "Impact Factor",
      "weight": 50,
      "type": "numeric",
      "direction": "higher_better",
      "measures": "what this criterion measures, shown in the output"
    }
  ],
  "candidates": [
    {
      "journal": "Journal of Hydrology",
      "publisher": "Elsevier",
      "scores": {
        "impact": {"value": 7.3, "note": "JCR 2025."}
      }
    }
  ]
}
```

### Criterion fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Key used in each candidate's `scores`. Must be unique. |
| `label` | no | Column heading. Defaults to `id`. |
| `weight` | yes | Any non-negative number. Renormalized to 100%, so 50/30/20 and 5/3/2 are the same model. |
| `type` | no | `scale` (default) or `numeric`. |
| `direction` | no | `higher_better` (default) or `lower_better`. Only affects `numeric`. |
| `reference` | no | Anchor for `numeric`. See below. |
| `measures` | no | Prose shown in the scoring-model table. Write it — it is what makes the matrix auditable. |

### Score entries

Either a bare number, or an object:

```json
"impact": 7.3
"impact": {"value": 7.3, "note": "JCR 2025."}
"impact": {"value": null, "note": "No JCR entry; not indexed in WoS."}
```

`null` means **unknown**. It contributes 0 to the total and renders as `—`, so an unknown never
inflates a rank. A missing key is treated the same way but also emits a warning — prefer explicit
`null` with a note.

### Candidate fields

`journal` (required), `publisher`, `scores`, `veto`, `veto_reason`.

## The math

Every criterion is mapped onto 0–10, then the total is a weighted mean:

```
total = Σ (score_i × weight_i / Σ weight)
```

**`type: "scale"`** — the value is already 0–10 and is used as given. Values outside 0–10 are an
error, not a clamp. Anchor your scale in the criterion's `measures` text so the numbers mean
something to a reader (e.g. "10 = APC fully covered; 4 = no agreement; 1 = publisher excluded by the
author").

**`type: "numeric"`** — linear, anchored at zero:

- `higher_better`: `score = value / reference × 10`. `reference` defaults to the **highest** value in
  the set, so the best candidate scores 10 and a value of 0 scores 0. Set `reference` explicitly to
  score against a fixed external anchor instead of the field of candidates.
- `lower_better`: `score = (1 − value / reference) × 10`. `reference` defaults to the **highest**
  value in the set, so the most expensive candidate scores 0 and a cost of 0 scores 10.

Both are clamped to 0–10, so an explicit `reference` that some candidate exceeds does not produce a
negative or >10 score.

Note the consequence of the default: **normalizing against the set makes scores relative to the
candidate list.** Adding a higher-IF journal lowers everyone else's impact score. That is usually
what you want for a comparison, but it means the totals are not comparable across two different runs
with different candidate lists. Use an explicit `reference` when you want stable numbers.

## Veto vs. penalty

A **veto** (`"veto": true, "veto_reason": "..."`) sinks the candidate below every non-vetoed one
regardless of score, and lists it under "Excluded by veto" with the score it would have had.

Use a veto for a genuine disqualification: predatory-publishing flags, not indexed where the author
needs to be indexed, a length limit the manuscript cannot meet, an OA mandate the journal cannot satisfy.

Use a **low score on a criterion** for a strong preference: a publisher the author would rather
avoid, an APC above budget but not impossible. A penalty keeps the candidate visible and shows what
the preference cost — if a journal the author dislikes would otherwise have won by two points, the
author should get to see that and decide, rather than have it deleted from the matrix.

## Running it

```bash
python3 scripts/score_matrix.py candidates.json --check              # validate, no output
python3 scripts/score_matrix.py candidates.json                      # Markdown to stdout
python3 scripts/score_matrix.py candidates.json -o matrix.md         # Markdown to a file
python3 scripts/score_matrix.py candidates.json --format json        # scores as JSON
python3 scripts/score_matrix.py candidates.json --tie-margin 0.25    # widen the near-tie flag
```

Warnings (weights that do not sum to 100, missing scores) go to stderr and do not stop the run.
Input errors exit with status 2 and a single message.

## Near-ties

Consecutive non-vetoed candidates whose totals differ by at most `--tie-margin` (default 0.15) are
flagged. Treat a flagged pair as unordered: the inputs are estimates with real uncertainty, and a
0.07 gap is a coin flip dressed as a ranking. In the write-up, name what would actually break the
tie — usually the paper's framing, or one deadline the author still has to confirm.

## Sensitivity

If the author is unsure about the weights, rerun with a different set and see whether the top choice
changes. A winner that survives 50/30/20, 40/40/20, and 60/20/20 is a robust choice. A winner that
only holds at one weighting is really a statement about the weights, and the author should be told so.
