#!/usr/bin/env python3
"""
explicit_record.py — make documented absence explicit in museum records before they are given to an LLM.
Companion tool to "Confidently Wrong about the Long Tail" (Konstantakis, 2026). No network access, no model calls.

What it does (fixed, transparent rules; nothing is inferred about the object):
  1. ABSENCE   — for every core field that is empty in the record, add a line stating that it is not recorded:
                   no creator  -> "Maker: not recorded in this record."
                   no date     -> "Date of making: not recorded in this record."
                 (extend ABSENCE_FIELDS for other fields, e.g. place of making)
  2. ROLES     — optional, per collection: relabel a field whose content is known NOT to be the maker or a date
                 of making, using a JSON mapping you write for your own data, e.g. for a coin cabinet:
                   {"Creator": "Issuing authority (not the maker)"}
                 or for folk objects whose date field holds period labels:
                   {"Date": "Period label (not a date of making)"}
                 When a field is relabelled, the matching absence line is also added.

Evidence: in the study, rule 1 + rule 2 written for the questions asked reduced hallucination on unanswerable
questions from 18.4% to 2.5% (four models, 912 paired answers; exploratory). The generic, question-independent
use of rule 1 alone was NOT tested; test it on your own collection and questions before deployment, including
questions the record can answer.

Input formats:
  --text  FILE.json    {"id": "record text with 'Label: value' lines", ...}  (as in the study's rag_contexts.json)
  --europeana FILE.jsonl[.gz]   Europeana Search/Record API items, one JSON object per line
Output: JSON {"id": "amended record text"} to --out (default: stdout)

Examples:
  python3 explicit_record.py --text rag_contexts.json --out explicit.json
  python3 explicit_record.py --europeana items.jsonl.gz --roles coin_roles.json --out explicit.json
"""
import argparse
import gzip
import json
import sys

ABSENCE_FIELDS = [("Creator", "Maker: not recorded in this record."),
                  ("Date", "Date of making: not recorded in this record.")]
ABSENCE_FOR = dict(ABSENCE_FIELDS)


def _vals(item, field):
    out = []
    la = item.get(field + "LangAware")
    if isinstance(la, dict):
        for vs in la.values():
            out += [v for v in (vs if isinstance(vs, list) else [vs]) if isinstance(v, str)]
    if not out:
        p = item.get(field)
        out = p if isinstance(p, list) else ([p] if p else [])
    res = []
    for v in out:
        v = str(v).strip()
        if v and not v.startswith("http") and v not in res:
            res.append(v)
    return res


def europeana_text(item):
    """Same field selection as the study (HM_runner.record_text)."""
    def line(label, vals):
        return f"{label}: {'; '.join(vals)}" if vals else None
    date = [str(y) for y in (item.get("year") or [])] or _vals(item, "edmTimespanLabel")[:3]
    lines = [line("Title", _vals(item, "dcTitle") or [str(t) for t in (item.get("title") or [])]),
             line("Creator", _vals(item, "dcCreator")),
             line("Date", date),
             line("Object type", _vals(item, "dcType")[:3]),
             line("Institution", (item.get("dataProvider") or [None])[:1] if item.get("dataProvider") else []),
             line("Description", _vals(item, "dcDescription"))]
    return "\n".join(l for l in lines if l)


def make_explicit(text, roles=None):
    roles = roles or {}
    lines = text.split("\n")
    present = {l.split(":", 1)[0] for l in lines if ":" in l}
    add = []
    out = []
    for l in lines:
        label = l.split(":", 1)[0] if ":" in l else None
        if label in roles:
            l = roles[label] + ":" + l.split(":", 1)[1]
            if label in ABSENCE_FOR:
                add.append(ABSENCE_FOR[label])
        out.append(l)
    for field, sentence in ABSENCE_FIELDS:
        if field not in present:
            add.append(sentence)
    i = next((k for k, l in enumerate(out) if l.startswith("Title:")), -1)
    return "\n".join(out[:i + 1] + add + out[i + 1:])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text"); g.add_argument("--europeana")
    ap.add_argument("--roles", help="JSON mapping {field label: new label}")
    ap.add_argument("--out")
    a = ap.parse_args()
    roles = json.load(open(a.roles, encoding="utf-8")) if a.roles else {}
    if a.text:
        recs = json.load(open(a.text, encoding="utf-8"))
    else:
        op = gzip.open if a.europeana.endswith(".gz") else open
        recs = {}
        with op(a.europeana, "rt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    it = json.loads(line)
                    recs[it.get("id")] = europeana_text(it)
    res = {k: make_explicit(v, roles) for k, v in recs.items()}
    changed = sum(res[k] != recs[k] for k in res)
    s = json.dumps(res, ensure_ascii=False, indent=1)
    (open(a.out, "w", encoding="utf-8").write(s) if a.out else sys.stdout.write(s + "\n"))
    print(f"{len(res)} records, {changed} amended", file=sys.stderr)


if __name__ == "__main__":
    main()
