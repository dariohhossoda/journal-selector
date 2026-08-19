# Criteria catalog

A menu, not a checklist. Offer it in Step 2 and use the criteria the author picks. Three to five
criteria is usually enough; past six, the weights get so thin that the ranking is driven by noise.

Each entry says what it measures, how to score it, and how it goes wrong.

---

## Reach and prestige

### Impact factor (JCR)
- **Type:** `numeric`, higher better. Normalized against the highest IF in the candidate set.
- **Source:** Journal Citation Reports (Clarivate), released mid-year. If the newest edition has no
  value for a title, use the previous one and **say which edition in the note** — comparing a 2025 IF
  against a 2024 IF without flagging it makes the matrix look more precise than it is.
- **Failure mode:** IF varies by an order of magnitude between fields, so it only compares journals
  inside one field. It also rewards review journals over primary-research journals.

### CiteScore / SJR / SNIP
- **Type:** `numeric`, higher better.
- **Source:** Scopus (CiteScore), SCImago (SJR, SNIP).
- **Use when:** a candidate has no JCR IF — common for newer or regional journals. Do not mix IF and
  CiteScore in one criterion; they are different scales. Give them separate criteria, or convert the
  whole set to one metric.

### Quartile / ranking tier
- **Type:** `scale`. E.g. Q1 = 10, Q2 = 7, Q3 = 4, Q4 = 1.
- **Use when:** the author's institution or funder evaluates output by tier rather than raw metric —
  then the tier, not the decimal, is what actually counts.

### Field-specific ranking
- **Type:** `scale`, mapped from whatever list applies (ABDC, CORE, Qualis, a national list).
- **Use when:** promotion or thesis rules reference a specific list. Ask which one and score against it.

---

## Cost and access

### APC in currency
- **Type:** `numeric`, lower better. `reference` = the value that scores 0 (default: the most
  expensive in the set); 0 scores 10.
- **Source:** the publisher's own APC page. State the currency and the date — these rise annually.
- **Note:** hybrid journals have both a closed (free) route and an open one. If the author would
  publish closed, the APC is 0 and the relevant cost is loss of reach, not money.

### Institutional agreement coverage
- **Type:** `scale`. A workable anchoring: 10 = APC fully covered by an agreement the author's
  institution holds and the author is eligible under; 5 = partial discount, or a support programme
  the author might not qualify for; 4 = no agreement, author pays or publishes closed; 0–1 = a
  publisher the author has decided against.
- **Source:** the institution's library page, plus the publisher's own agreement lookup. **Ask the
  author** — they or their library know which deals apply, and the terms change every year.
- **Failure mode:** agreements are usually scoped by acceptance date, journal list (often only
  hybrid titles), and author role (corresponding author only). "The publisher has a deal" does not
  mean "this article is covered". Record the scope in the note.

### Open-access mandate compliance
- **Type:** `scale`, or a **veto** when a funder requires immediate OA and the journal cannot provide it.
- **Source:** the funder's policy, plus the journal's licence and embargo terms.

---

## Fit

### Special issue fit
- **Type:** `scale`. 0 = no open issue on topic; ~6 = a broad-scope issue that would accept the
  paper; 8–9 = a call that names this paper's exact subject; 10 = reserve for an invitation.
- **Source:** the journal's calls-for-papers page. **Always record the deadline and its
  confirmation status** — an issue that closed last month is worth 0, and a call page that could not
  be fetched is a manual check, not a score.
- **Failure mode:** a special issue is worth something only if the paper is genuinely on its topic.
  A physics-based-modelling issue does not fit a data-driven paper, however adjacent the title reads.

### Scope fit / editorial precedent
- **Type:** `scale`, backed by the Step 6 evidence — count and closeness of comparable papers the
  journal published in the last ~3 years.
- **Failure mode:** the aims-and-scope statement is marketing. What the journal actually published
  in the last three years is the evidence.

### Audience match
- **Type:** `scale`. Does the readership include the people who would act on this paper —
  practitioners, an agency, a specific research community?
- **Use when:** the paper is applied and the point is uptake rather than citations.

---

## Process

### Time to first decision
- **Type:** `numeric`, lower better, in days.
- **Source:** the journal's own reported median, or the "received / accepted" dates printed on its
  recent articles (sample several — one article proves nothing).
- **Use when:** a thesis deadline, grant report, or contract date is real and near.

### Acceptance rate
- **Type:** `numeric`, higher better.
- **Source:** rarely published; do not estimate one. Leave the cell `null` with a note rather than
  inventing a plausible percentage.

### Format and length limits
- **Type:** `scale`, or a **veto** if the manuscript cannot be cut to the limit.
- **Source:** the guide for authors — word cap, figure cap, whether LaTeX is accepted, reference style.

### Review model
- **Type:** `scale`. Single-blind, double-blind, open review, published referee reports.
- **Use when:** the author has a stated preference, or anonymity matters for this paper.

---

## Integrity screens

### Indexing
- **Type:** `scale`, or a **veto**. Is the journal in the indexes that count for the author
  (Web of Science, Scopus, PubMed, DOAJ for OA venues)?
- **Failure mode:** unindexed work can be invisible to the evaluation systems the author is judged by.

### Predatory / quality flags
- **Type:** almost always a **veto**, not a low score.
- **Signals:** not in DOAJ despite charging APCs, no named editorial board, solicitation by spam
  email, implausible turnaround promises, a title that mimics an established journal.
- **Source:** DOAJ, the publisher's COPE/OASPA membership, Think-Check-Submit.
