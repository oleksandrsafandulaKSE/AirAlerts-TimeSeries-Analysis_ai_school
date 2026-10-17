#!/usr/bin/env python3
"""Compile results/*.json into report.md, following outline.yaml order and fields.yaml structure.

Skips any value containing [uncertain], any field named in the item's `uncertain` array,
and empty values. Fields present in a JSON but absent from fields.yaml go under "Other Info".
"""
import json
import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
OUTLINE = yaml.safe_load((HERE / "outline.yaml").read_text(encoding="utf-8"))
FIELDS = yaml.safe_load((HERE / "fields.yaml").read_text(encoding="utf-8"))["fields"]
RESULTS = (HERE / OUTLINE["execution"]["output_dir"].replace("./air-alert-forecasting-research/", "")).resolve()

TOC_FIELDS = ["target_type", "peer_review_status", "year", "popularity"]
INTERNAL = {"_source_file", "uncertain"}

# fields.yaml category key -> display title + JSON keys that may hold that category's sub-dict
CATEGORY_MAPPING = {
    "basic_info": ("Basic Info", ["basic_info", "Basic Info"]),
    "problem_framing": ("Problem Framing", ["problem_framing", "Problem Framing"]),
    "data": ("Data", ["data", "Data"]),
    "method": ("Method", ["method", "Method"]),
    "evaluation": ("Evaluation", ["evaluation", "Evaluation"]),
    "leakage_and_hygiene": ("Leakage & Hygiene", ["leakage_and_hygiene", "leakage", "Leakage & Hygiene"]),
    "results": ("Results", ["results", "Results"]),
    "reproducibility": ("Reproducibility", ["reproducibility", "Reproducibility"]),
    "relevance": ("Relevance", ["relevance", "Relevance"]),
}
NESTED_KEYS = {k for _, keys in CATEGORY_MAPPING.values() for k in keys}
DEFINED = {f["name"] for flist in FIELDS.values() for f in flist}


def lookup(data, category, field):
    """Top level -> mapped category sub-dict -> any nested dict."""
    if field in data:
        return data[field]
    for key in CATEGORY_MAPPING.get(category, ("", []))[1]:
        sub = data.get(key)
        if isinstance(sub, dict) and field in sub:
            return sub[field]
    for v in data.values():
        if isinstance(v, dict) and field in v:
            return v[field]
    return None


def is_uncertain(value):
    return "[uncertain]" in json.dumps(value, ensure_ascii=False)


def is_empty(value):
    return value is None or (isinstance(value, str) and not value.strip()) or value in ([], {})


def fmt(value, depth=0):
    """Markdown for a field value: lists of dicts one per line, short lists inline, long text as blockquote."""
    if isinstance(value, dict):
        parts = [f"**{k}**: {fmt(v, depth + 1)}" for k, v in value.items() if not is_empty(v)]
        return "; ".join(parts) if depth else "\n\n".join(f"- {p}" for p in parts)
    if isinstance(value, list):
        if value and all(isinstance(x, dict) for x in value):
            return "\n".join("- " + " | ".join(f"{k}: {fmt(v, depth + 1)}" for k, v in x.items()) for x in value)
        items = [fmt(x, depth + 1) for x in value]
        if depth or (len(items) <= 4 and sum(len(i) for i in items) < 120):
            return ", ".join(items)
        return "\n".join(f"- {i}" for i in items)
    text = str(value)
    if depth == 0 and len(text) > 100:
        return "> " + text.replace("\n", "\n> ")
    return text


def short(value, limit=45):
    """First clause of a prose value, for the TOC."""
    text = re.split(r" \(|; |\. | — | - ", str(value), maxsplit=1)[0].strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def main():
    items = OUTLINE["items"]
    loaded = []
    for item in items:
        path = RESULTS / f"{item['id']}.json"
        if not path.exists():
            raise FileNotFoundError(f"missing result for {item['id']}: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        loaded.append((item, data, set(data.get("uncertain", []))))
    print(f"loaded {len(loaded)} results from {RESULTS}")

    out = [f"# {OUTLINE['topic']}", "",
           f"Compiled {len(loaded)} items. Values marked [uncertain] are omitted; each item lists its "
           "uncertain fields at the end.", "", "## Table of Contents", ""]
    for i, (item, data, unc) in enumerate(loaded, 1):
        bits = []
        for f in TOC_FIELDS:
            v = lookup(data, "basic_info", f) if f != "target_type" else lookup(data, "problem_framing", f)
            if not is_empty(v) and not is_uncertain(v) and f not in unc:
                bits.append(f"{f.replace('_', ' ').capitalize()}: {short(v)}")
        tail = " - " + " | ".join(bits) if bits else ""
        out.append(f"{i}. [{item['name']}](#{item['id']}){tail}")
    out.append("")

    skipped = 0
    for i, (item, data, unc) in enumerate(loaded, 1):
        out += ["---", "", f'<a id="{item["id"]}"></a>', f"## {i}. {item['name']}", "",
                f"*Category: {item['category']}* — {item['note']}", ""]
        for cat, flist in FIELDS.items():
            block = []
            for f in flist:
                v = lookup(data, cat, f["name"])
                if is_empty(v) or f["name"] in unc or is_uncertain(v):
                    skipped += 1
                    continue
                block += [f"**{f['name'].replace('_', ' ').capitalize()}**", "", fmt(v), ""]
            if block:
                out += [f"### {CATEGORY_MAPPING.get(cat, (cat.title(),))[0]}", ""] + block
        extra = {k: v for k, v in data.items()
                 if k not in DEFINED and k not in INTERNAL and k not in NESTED_KEYS
                 and not is_empty(v) and not is_uncertain(v)}
        if extra or unc:
            out += ["### Other Info", ""]
            for k, v in extra.items():
                out += [f"**{k}**", "", fmt(v), ""]
            if unc:
                out += ["**Uncertain fields (omitted above)**", ""] + [f"- {u}" for u in sorted(unc)] + [""]

    report = HERE / "report.md"
    report.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {report} ({len(out)} lines); skipped {skipped} uncertain/empty field values")


if __name__ == "__main__":
    main()
