"""Generate the TS captions array from captions_aligned.json.

Usage:
    python work/captions/03_gen_ts_captions.py

Reads:  work/captions/captions_aligned.json
Writes: work/captions/captions.array.ts

Splits each line on accent keywords (longest-first) so the keyword is rendered
as a bold accent-color part while surrounding text is default ink.

EDIT: add project-specific keywords to ACCENT below.
Good candidates: project names, tech terms, numbers, platforms, key verbs.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
src = json.loads((ROOT / "work/captions/captions_aligned.json").read_text(encoding="utf-8"))

# EDIT: project-specific accent keywords (longest first for matching priority)
ACCENT = [
    # "Project Name",
    # "GitHub",
    # "Claude Code",
    # "API",
    # "开源",
]


def split_parts(text: str):
    low = text.lower()
    parts = []
    i = 0
    while i < len(text):
        matched = None
        for kw in ACCENT:
            if low[i:i + len(kw)] == kw.lower():
                matched = kw
                break
        if matched is None:
            j = i + 1
            while j < len(text):
                hit = False
                for kw in ACCENT:
                    if low[j:j + len(kw)] == kw.lower():
                        hit = True
                        break
                if hit:
                    break
                j += 1
            parts.append({"text": text[i:j]})
            i = j
        else:
            parts.append({"text": text[i:i + len(matched)], "tone": "accent"})
            i += len(matched)
    merged = []
    for p in parts:
        if merged and "tone" not in merged[-1] and "tone" not in p:
            merged[-1]["text"] += p["text"]
        else:
            merged.append(p)
    return merged


lines = []
for c in src["subtitles"]:
    parts = split_parts(c["text"])
    parts_json = json.dumps(parts, ensure_ascii=False)
    lines.append(
        f"    {{start: {c['start']}, end: {c['end']}, parts: {parts_json}}},"
    )

out = ROOT / "work/captions/captions.array.ts"
out.write_text("  captions: [\n" + "\n".join(lines) + "\n  ],\n", encoding="utf-8")
print(f"Wrote {out} ({len(lines)} captions)")
