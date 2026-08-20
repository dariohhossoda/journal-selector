# Research protocol

How to fill each cell so a reader can check it, and what to do when the source will not load.

## Rules

1. **Every cell carries a note with a source and a date.** The date matters as much as the value:
   impact factors, APCs, agreements, and deadlines all expire. Write "JCR 2025" or
   "publisher APC page, checked 2026-07-22", not "high impact".
2. **Unverified is a state, not a gap.** If you cannot confirm a value, set the score to `null`, put
   what you tried in the note, and add the URL to the manual-checks list. A `null` that is honest is
   worth more than a number that is plausible.
3. **Prefer the primary source.** The publisher's own page for APCs and calls for papers; the index
   itself for metrics; the institution's library for agreements. Aggregator sites and blog posts go
   stale silently.
4. **Search results are not a fetch.** A search snippet quoting an impact factor is weaker evidence
   than the journal's own metrics page. When you only have the snippet, say so in the note.

## Where each fact lives

| Fact | Primary source | Notes |
|---|---|---|
| Impact factor | Journal Citation Reports (Clarivate); the journal's own "Journal Insights" / metrics page | New edition mid-year. Record the edition. |
| CiteScore | Scopus source page | Different scale from IF — never mix them in one criterion. |
| SJR / quartile | SCImago Journal Rank | Free to browse; quartile is field-relative. |
| APC | Publisher's price list or the journal's OA page | Record currency and date. Hybrid titles have a free closed route. |
| Institutional agreement | The author's library page; the publisher's agreement lookup | **Ask the author first.** Scoped by acceptance date, title list, and author role. |
| Open access licence / embargo | The journal's OA policy page | Needed when a funder mandates immediate OA. |
| Special issues | The journal's calls-for-papers page | Record the deadline and whether you confirmed it. |
| Editorial precedent | A search of the journal's recent volumes for the paper's method and problem | Cite titles and years, not counts. |
| Guide for authors | The journal's author instructions | Word/figure caps, reference style, LaTeX support, required forms. |
| Time to decision | The journal's reported medians, or received/accepted dates on several recent papers | One article is not a sample. |
| Indexing | Web of Science Master List, Scopus title list, DOAJ | DOAJ absence plus an APC is a red flag. |
| Integrity screens | DOAJ, COPE/OASPA membership, Think-Check-Submit | Treat a hit as a veto, not a penalty. |

## Fetch blocks to expect

Several major publisher domains reject automated requests. Encountering one is normal; hiding it is not.

- **ScienceDirect / Elsevier** — routinely returns **HTTP 403** to non-browser requests. This hits
  the very pages that matter most: journal calls-for-papers, special-issue pages, and guides for
  authors. Expect to fall back on search snippets, and expect not to be able to confirm deadlines.
- **Wiley, Taylor & Francis, Springer** — bot protection appears intermittently on call-for-papers pages.
- **Copernicus, MDPI, most society publishers** — usually fetch fine, including special-issue
  windows and deadlines.

When a page is blocked, the cell note must say three things: what you were trying to confirm, that
the fetch failed and how (status code), and what you used instead. Then put the URL in the
manual-checks list with the specific question the author needs to answer, e.g.:

> Confirm the submission deadline for "Real-time Flood Forecasting and Early Warning Systems in
> Urban Areas" — https://www.sciencedirect.com/special-issue/10X1TVPTT8B (403 to automated fetch;
> open in a browser).

"Verify on the website" is not a checklist item. A URL plus the question is.

## Delegating the lookups

Most of this protocol is mechanical: one journal, a handful of published facts, a URL each. That is
what `agents/venue-fact-finder.md` is for — dispatch one per candidate, in parallel. It runs on a
cheap model, has only `WebSearch` and `WebFetch`, and returns structured records rather than prose.

It reports a `fetch_status` per fact, and the status is part of the evidence:

| `fetch_status` | What it means for the cell |
|---|---|
| `fetched` | Read from the primary source. Use the value; note the source and date. |
| `search_only` | Value came from a search snippet; the primary source would not load. Usable, but the note must say the primary source was not reached. |
| `blocked` | The source refused the request. The cell is `null`, and the URL goes on the manual-checks list with the status code. |
| `not_found` | Looked, not published. The cell is `null` with that stated — this is a real finding, not a gap. |
| `not_attempted` | Out of scope for that dispatch. |

The agent does not score, and its output has no score field. Turning a raw fact into a 0–10 value
needs the anchors and criteria agreed with the author, which the agent never saw. Do that conversion
yourself, and spot-check the facts behind the Top 3 against the URLs it reported before recommending
anything.

## Sequence

1. Ask the author about institutional agreements, budget, publisher vetoes, and OA mandates
   (Step 2 of the skill) — before researching, so you know which criteria to research at all.
2. Build the candidate list from the manuscript's references, comparable recent papers, the group's
   prior venue, and society journals in the field.
3. For each candidate: metrics, then cost/agreement, then open special issues.
4. For the top few by provisional score: guide for authors, and the editorial-precedent search.
5. For the winner only: the full Step 6 scope verification.

Front-loading depth on candidates that will place tenth is wasted work. Score the whole set shallowly,
then go deep on the contenders.
