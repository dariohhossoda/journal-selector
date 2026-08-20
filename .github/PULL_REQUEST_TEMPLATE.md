## Summary

<!-- What changed and why. If it closes an issue, say "Closes #N". -->

## Type of change

- [ ] New or corrected criterion in the catalog
- [ ] Research protocol — source moved, expired, or started blocking automated fetching
- [ ] Scorer change (`scripts/score_matrix.py`)
- [ ] Skill process change (`SKILL.md`, `commands/`)
- [ ] Templates or example input
- [ ] Documentation
- [ ] Repo plumbing (CI, packaging, metadata)

## Smoke check

Ran, with output pasted or confirmed clean:

```bash
claude plugin validate .
python3 skills/journal-selector/scripts/score_matrix.py \
  skills/journal-selector/templates/candidates.example.json --check
python3 skills/journal-selector/scripts/score_matrix.py \
  skills/journal-selector/templates/candidates.example.json | head -30
```

- [ ] `claude plugin validate .` passes
- [ ] `--check` passes on the example input with no warnings
- [ ] The example still renders, and the totals are what this PR intends

## Invariants

These are deliberate design decisions, not oversights. If this PR breaks one, argue the case in the
summary instead of ticking the box.

- [ ] **Nothing about an institution is hardcoded** — no consortium, country, library deal, or
      publisher blocklist baked into the skill or the references. Those are elicited per run.
- [ ] **No new runtime dependency** — the scorer stays stdlib Python 3.9+.
- [ ] **Unverifiable stays unverifiable** — no path added where a missing fact gets filled from
      memory instead of becoming `null` plus a manual-check item.
- [ ] **The arithmetic stays in the script** — nothing moved into prose that a reader would have to
      trust rather than rerun.

## If the scoring math changed

- [ ] The example's totals were recomputed and the new numbers are in the diff
- [ ] `references/scoring-model.md` describes the new behavior, including what the `reference` field
      anchors and in which direction
- [ ] Edge cases still behave: a value of `0` under `lower_better`, an explicit `reference` a
      candidate exceeds, a `null` score, an all-`null` criterion, weights that do not sum to 100
- [ ] Whether this changes rankings for existing input files is stated in the summary

## If a version bump is needed

The version lives in **two** files and they must match, or the marketplace advertises a version the
plugin does not report.

- [ ] `.claude-plugin/plugin.json` → `version`
- [ ] `.claude-plugin/marketplace.json` → `plugins[0].version`

## If the skill's triggering changed

- [ ] The `description` in `SKILL.md` frontmatter still carries the natural-language phrases an
      author would actually type ("where should I submit", "target journal", "compare these journals")
- [ ] `SKILL.md` and the reference files do not contradict each other on any step
- [ ] Cross-references between `SKILL.md` and `references/` still resolve

## Notes for review

<!-- Known limitations, things you are unsure about, decisions worth arguing with. -->
