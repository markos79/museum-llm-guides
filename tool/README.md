# explicit-record

Make documented absence explicit in museum records before an LLM-based guide answers from them.

Companion tool to: Markos Konstantakis (2026), *Confidently Wrong about the Long Tail: Popularity, Grounding
and Language in Multilingual LLM Museum Guides* (manuscript submitted to ACM JOCCH). Preregistration: OSF ANX4T.

## Why
In the study, four LLMs answered questions about 110 museum objects with the object's Europeana record in their
context. When the record did not contain the answer (no maker, no date of making), 18.4% of answers still asserted
one. Most of these errors did not come from nowhere: a coin's issuing emperor listed as *creator* became the maker,
a period label such as "Reign of George I" became a date range. When the record stated the absence explicitly and
labelled such fields for what they are, the rate fell to 2.5% for the same questions (exploratory experiment,
912 paired answers, all four models).

## What it does
Fixed, transparent rules. Nothing is inferred about the object and no model is called.

1. **Absence lines** — for each core field that is empty, a line is added after the title:
   - no creator → `Maker: not recorded in this record.`
   - no date → `Date of making: not recorded in this record.`
2. **Role labels (optional, per collection)** — a JSON file relabels fields whose content you know is not the
   maker or the date of making, e.g. for coins `{"Creator": "Issuing authority (not the maker)"}` or for folk
   objects dated by period `{"Date": "Period label (not a date of making)"}`. A relabelled field also gets the
   matching absence line.

## What was and was not tested
The study tested rules 1 and 2 applied to the records of the questions asked (unanswerable questions only).
**The question-independent use of rule 1 alone was not tested**, nor the effect of the added lines on questions
the record can answer. Test on your own collection and questions, including answerable ones, before deployment.

## Use
Python 3.8+, standard library only.

```
python3 explicit_record.py --text examples/sample_records.json
python3 explicit_record.py --text examples/sample_records.json --roles examples/roles_coins.json
python3 explicit_record.py --europeana items.jsonl.gz --out explicit.json
python3 test_explicit_record.py
```

- `--text`: a JSON object `{id: "record text"}` with one `Label: value` per line (format of the study's
  `rag_contexts.json`).
- `--europeana`: Europeana Search API items, one JSON object per line (optionally gzipped). The record text is
  built with the same fields as in the study: title, creator, date (year or time-span label), object type,
  institution, description.

The example records are Europeana metadata, released under CC0.

## Licence
MIT (see LICENSE). Please cite the article and this software (CITATION.cff).
