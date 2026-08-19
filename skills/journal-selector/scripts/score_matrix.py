#!/usr/bin/env python3
"""Score journal candidates against weighted criteria and render a decision matrix.

Stdlib only. Input is a JSON file (see ../templates/candidates.example.json);
output is Markdown on stdout by default, or JSON with --format json.

Usage:
    python3 score_matrix.py candidates.json
    python3 score_matrix.py candidates.json --format json
    python3 score_matrix.py candidates.json --tie-margin 0.2
    python3 score_matrix.py candidates.json --check      # validate only, no render
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

SCALE_MAX = 10.0


class InputError(Exception):
    """Raised for any malformed input; message is shown to the user verbatim."""


# --------------------------------------------------------------------------- #
# Loading and validation
# --------------------------------------------------------------------------- #

def load(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        raise InputError(f"input file not found: {path}")
    except json.JSONDecodeError as exc:
        raise InputError(f"{path} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise InputError("top level of the input must be a JSON object")
    return data


def normalize_entry(entry: Any, criterion_id: str, journal: str) -> tuple[float | None, str]:
    """A score entry is either a bare number or {"value": ..., "note": "..."}.

    Returns (value, note). value is None when the entry is explicitly null,
    which marks the criterion as unknown for that candidate.
    """
    if entry is None:
        return None, ""
    if isinstance(entry, bool):
        raise InputError(f"{journal}: score for '{criterion_id}' must be a number, not a boolean")
    if isinstance(entry, (int, float)):
        return float(entry), ""
    if isinstance(entry, dict):
        value = entry.get("value")
        note = str(entry.get("note", ""))
        if value is None:
            return None, note
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError(f"{journal}: 'value' for '{criterion_id}' must be a number")
        return float(value), note
    raise InputError(
        f"{journal}: score for '{criterion_id}' must be a number, null, or an object with 'value'"
    )


def validate(data: dict[str, Any]) -> tuple[list[dict], list[dict], list[str]]:
    """Returns (criteria, candidates, warnings). Raises InputError on hard problems."""
    warnings: list[str] = []

    criteria = data.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise InputError("'criteria' must be a non-empty list")

    seen_ids: set[str] = set()
    for crit in criteria:
        if not isinstance(crit, dict):
            raise InputError("each entry of 'criteria' must be an object")
        cid = crit.get("id")
        if not isinstance(cid, str) or not cid:
            raise InputError("every criterion needs a string 'id'")
        if cid in seen_ids:
            raise InputError(f"duplicate criterion id: {cid}")
        seen_ids.add(cid)
        crit.setdefault("label", cid)
        crit.setdefault("type", "scale")
        crit.setdefault("direction", "higher_better")
        if crit["type"] not in ("scale", "numeric"):
            raise InputError(f"{cid}: 'type' must be 'scale' or 'numeric'")
        if crit["direction"] not in ("higher_better", "lower_better"):
            raise InputError(f"{cid}: 'direction' must be 'higher_better' or 'lower_better'")
        weight = crit.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight < 0:
            raise InputError(f"{cid}: 'weight' must be a non-negative number")

    total_weight = sum(float(c["weight"]) for c in criteria)
    if total_weight <= 0:
        raise InputError("the criteria weights sum to zero — nothing to score")
    if abs(total_weight - 100.0) > 1e-6 and abs(total_weight - 1.0) > 1e-6:
        warnings.append(
            f"weights sum to {total_weight:g}, not 100 (or 1) — they are renormalized to 100%, "
            "which changes each criterion's effective share; state this in the write-up."
        )

    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise InputError("'candidates' must be a non-empty list")

    for cand in candidates:
        if not isinstance(cand, dict):
            raise InputError("each entry of 'candidates' must be an object")
        name = cand.get("journal")
        if not isinstance(name, str) or not name:
            raise InputError("every candidate needs a string 'journal'")
        scores = cand.get("scores")
        if not isinstance(scores, dict):
            raise InputError(f"{name}: 'scores' must be an object keyed by criterion id")
        unknown = set(scores) - seen_ids
        if unknown:
            raise InputError(f"{name}: scores reference unknown criteria: {sorted(unknown)}")
        for cid in seen_ids:
            if cid not in scores:
                warnings.append(f"{name}: no score for '{cid}' — treated as unknown (0)")

    return criteria, candidates, warnings


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #

def scale_values(crit: dict, raw: dict[str, float | None]) -> dict[str, float]:
    """Map raw per-candidate values for one criterion onto a 0-10 score."""
    cid = crit["id"]
    present = {k: v for k, v in raw.items() if v is not None}
    scaled: dict[str, float] = {k: 0.0 for k in raw}

    if crit["type"] == "scale":
        for key, value in present.items():
            if not 0.0 <= value <= SCALE_MAX:
                raise InputError(
                    f"{key}: '{cid}' is type 'scale' so the value must be within 0-10, got {value:g}"
                )
            scaled[key] = value
        return scaled

    # type == "numeric": normalize against a reference, or against the worst/best in the set.
    #   higher_better: 'reference' is the value that scores 10 (default: the highest in the set),
    #                  and 0 scores 0.
    #   lower_better:  'reference' is the value that scores 0 (default: the highest in the set),
    #                  and 0 scores 10.
    # Both are linear and anchored at 0, so a candidate at zero cost is perfect rather than a
    # division by zero.
    if not present:
        return scaled
    reference = crit.get("reference")
    if reference is not None:
        if isinstance(reference, bool) or not isinstance(reference, (int, float)) or reference <= 0:
            raise InputError(f"{cid}: 'reference' must be a positive number")
        ref = float(reference)
    else:
        ref = max(present.values())
    if ref <= 0:
        raise InputError(
            f"{cid}: every candidate scores 0 or less, so there is nothing to normalize against — "
            "set an explicit 'reference' or use type 'scale'"
        )

    for key, value in present.items():
        if crit["direction"] == "higher_better":
            score = value / ref * SCALE_MAX
        else:
            score = (1.0 - value / ref) * SCALE_MAX
        scaled[key] = max(0.0, min(score, SCALE_MAX))
    return scaled


def score(criteria: list[dict], candidates: list[dict], tie_margin: float) -> dict[str, Any]:
    total_weight = sum(float(c["weight"]) for c in criteria)
    rows: list[dict[str, Any]] = []

    per_criterion: dict[str, dict[str, float]] = {}
    raw_by_criterion: dict[str, dict[str, float | None]] = {}
    notes: dict[str, dict[str, str]] = {}

    for crit in criteria:
        cid = crit["id"]
        raw: dict[str, float | None] = {}
        crit_notes: dict[str, str] = {}
        for cand in candidates:
            name = cand["journal"]
            value, note = normalize_entry(cand["scores"].get(cid), cid, name)
            raw[name] = value
            if note:
                crit_notes[name] = note
        raw_by_criterion[cid] = raw
        notes[cid] = crit_notes
        per_criterion[cid] = scale_values(crit, raw)

    for cand in candidates:
        name = cand["journal"]
        vetoed = bool(cand.get("veto"))
        weighted = 0.0
        detail = {}
        for crit in criteria:
            cid = crit["id"]
            s = per_criterion[cid][name]
            share = float(crit["weight"]) / total_weight
            weighted += s * share
            detail[cid] = {
                "raw": raw_by_criterion[cid][name],
                "score": round(s, 2),
                "note": notes[cid].get(name, ""),
            }
        rows.append({
            "journal": name,
            "publisher": cand.get("publisher", ""),
            "criteria": detail,
            "total": round(weighted, 2),
            "veto": vetoed,
            "veto_reason": cand.get("veto_reason", ""),
        })

    # Vetoed candidates are ranked last regardless of score, and never win.
    rows.sort(key=lambda r: (r["veto"], -r["total"]))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i

    live = [r for r in rows if not r["veto"]]
    near_ties: list[dict[str, str]] = []
    for i in range(len(live) - 1):
        gap = live[i]["total"] - live[i + 1]["total"]
        if gap <= tie_margin:
            near_ties.append({
                "a": live[i]["journal"],
                "b": live[i + 1]["journal"],
                "gap": round(gap, 2),
            })

    return {
        "criteria": [
            {
                "id": c["id"],
                "label": c["label"],
                "weight_pct": round(float(c["weight"]) / total_weight * 100, 1),
                "type": c["type"],
                "direction": c["direction"],
                "reference": c.get("reference"),
                "measures": c.get("measures", ""),
            }
            for c in criteria
        ],
        "rows": rows,
        "near_ties": near_ties,
        "tie_margin": tie_margin,
    }


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def fmt(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:g}"


def render_markdown(data: dict[str, Any], result: dict[str, Any]) -> str:
    out: list[str] = []
    title = data.get("title") or "Journal candidates — decision matrix"
    out.append(f"# {title}")
    out.append("")
    if data.get("date"):
        out.append(f"**Research date:** {data['date']}")
    if data.get("topic"):
        out.append("")
        out.append(f"**Manuscript topic:** {data['topic']}")
    out.append("")

    out.append("## Scoring model")
    out.append("")
    out.append("| Criterion | Weight | Type | What it measures |")
    out.append("|---|---|---|---|")
    for crit in result["criteria"]:
        kind = crit["type"]
        if kind == "numeric":
            ref = crit["reference"]
            basis = f"reference {fmt(ref)}" if ref is not None else "highest in set"
            anchor = "scores 10" if crit["direction"] == "higher_better" else "scores 0"
            kind = (
                f"numeric, {crit['direction'].replace('_', ' ')}, "
                f"linear ({basis} {anchor})"
            )
        out.append(
            f"| **{crit['label']}** | {crit['weight_pct']:g}% | {kind} | {crit['measures'] or '—'} |"
        )
    out.append("")

    header = ["#", "Journal", "Publisher"]
    for crit in result["criteria"]:
        header.append(f"{crit['label']} ({crit['weight_pct']:g}%)")
    header.append("**Total**")
    out.append("## Matrix")
    out.append("")
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "---|" * len(header))
    for row in result["rows"]:
        cells = [str(row["rank"]), f"**{row['journal']}**", row["publisher"] or "—"]
        for crit in result["criteria"]:
            detail = row["criteria"][crit["id"]]
            raw = detail["raw"]
            if crit["type"] == "numeric" and raw is not None:
                cells.append(f"{fmt(raw)} → {detail['score']:.2f}")
            elif raw is None:
                cells.append("—")
            else:
                cells.append(f"{detail['score']:.2f}")
        total = f"**{row['total']:.2f}**"
        if row["veto"]:
            total += " (vetoed)"
        cells.append(total)
        out.append("| " + " | ".join(cells) + " |")
    out.append("")

    evidence = [
        (row, crit, row["criteria"][crit["id"]]["note"])
        for row in result["rows"]
        for crit in result["criteria"]
        if row["criteria"][crit["id"]]["note"]
    ]
    if evidence:
        out.append("## Evidence per cell")
        out.append("")
        for row, crit, note in evidence:
            out.append(f"- **{row['journal']} — {crit['label']}:** {note}")
        out.append("")

    vetoed = [r for r in result["rows"] if r["veto"]]
    if vetoed:
        out.append("## Excluded by veto")
        out.append("")
        for row in vetoed:
            reason = row["veto_reason"] or "no reason recorded"
            out.append(f"- **{row['journal']}** — {reason} (would have scored {row['total']:.2f})")
        out.append("")

    live = [r for r in result["rows"] if not r["veto"]]
    if live:
        out.append("## Top 3")
        out.append("")
        out.append("| Position | Journal | Weighted total | Why |")
        out.append("|---|---|---|---|")
        for row in live[:3]:
            out.append(
                f"| **{row['rank']}** | **{row['journal']}** | **{row['total']:.2f}** | "
                "<!-- fill in: the one or two criteria that decided it --> |"
            )
        out.append("")

    if result["near_ties"]:
        out.append(
            f"**Near-ties (gap <= {result['tie_margin']:g}, inside the noise of these estimates):**"
        )
        out.append("")
        for tie in result["near_ties"]:
            out.append(f"- {tie['a']} vs {tie['b']} — {tie['gap']:.2f} apart")
        out.append("")

    out.append("## Decision")
    out.append("")
    out.append("<!-- Target journal chosen, date, and what still has to be verified by hand -->")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="path to the candidates JSON file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--tie-margin",
        type=float,
        default=0.15,
        help="flag consecutive candidates whose totals differ by at most this much (default 0.15)",
    )
    parser.add_argument("--check", action="store_true", help="validate the input and exit")
    parser.add_argument("-o", "--output", help="write to this file instead of stdout")
    args = parser.parse_args(argv)

    try:
        data = load(args.input)
        criteria, candidates, warnings = validate(data)
        result = score(criteria, candidates, args.tie_margin)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if args.check:
        print(f"ok: {len(candidates)} candidates, {len(criteria)} criteria", file=sys.stderr)
        return 0

    if args.format == "json":
        text = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        text = render_markdown(data, result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
