"""Build corrected + line-split captions from whisper timestamps.

Usage:
    python work/captions/02_build_aligned.py

Reads:  work/captions/captions.raw.json (for timestamps reference)
Writes: work/captions/captions_aligned.json
        work/captions/captions_aligned.txt

WORKFLOW:
1. Run 01_transcribe.py first
2. Read captions.raw.json and the podcast script
3. Fill SEGMENTS below with (start, end, corrected_text) tuples
   - Drop Coze/intro tags (first 1-3s)
   - Correct ASR errors against the script
   - Keep whisper's start/end timestamps
   - Add commas at natural pauses to preempt long lines (see note below)
4. Run this script; it reports lines over MAX_CHARS width
5. If lines are over, add commas in SEGMENTS and re-run

LINE WIDTH NOTE:
MAX_CHARS=20 visual width (CJK=1.0, ASCII=0.6). If a segment exceeds this,
the splitter breaks on punctuation. To avoid ugly mid-sentence breaks, insert
commas at natural pauses when writing SEGMENTS. Example:
  Bad:  "你直接查小红书上你关注的某个品牌最近的热度走势。"  (24 width)
  Good: "你直接查小红书上，你关注的某个品牌最近的热度走势。"  (splits to 12+12)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# EDIT: fill with corrected segments from captions.raw.json + script
# (start, end, corrected_text)
SEGMENTS = [
    (0.0, 2.0, "替换为校正后的字幕段。"),
]

MAX_CHARS = 20
PUNCT = "，。！？、；："


def visual_len(s: str) -> float:
    n = 0.0
    for ch in s:
        n += 0.6 if ord(ch) < 128 else 1.0
    return n


def split_long(text: str):
    if visual_len(text) <= MAX_CHARS:
        return [text]
    parts = []
    buf = ""
    for ch in text:
        buf += ch
        if ch in PUNCT and visual_len(buf) >= 6:
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    merged = []
    for p in parts:
        if merged and visual_len(merged[-1] + p) <= MAX_CHARS:
            merged[-1] += p
        else:
            merged.append(p)
    final = []
    for chunk in merged:
        if visual_len(chunk) <= MAX_CHARS:
            final.append(chunk)
            continue
        words = chunk.split(" ")
        line = ""
        for w in words:
            candidate = w if not line else line + " " + w
            if visual_len(candidate) <= MAX_CHARS:
                line = candidate
            else:
                if line:
                    final.append(line)
                line = w
        if line:
            final.append(line)
    return final


def distribute_time(start, end, chunks):
    weights = [max(1, visual_len(c)) for c in chunks]
    total = sum(weights)
    dur = end - start
    bounds = []
    t = start
    for i, w in enumerate(weights[:-1]):
        t += dur * w / total
        bounds.append(t)
    bounds.append(end)
    out = []
    cur = start
    for c, b in zip(chunks, bounds):
        out.append((round(cur, 2), round(b, 2), c))
        cur = b
    return out


caption_lines = []
for s, e, t in SEGMENTS:
    chunks = split_long(t)
    changed = True
    while changed and len(chunks) > 1:
        changed = False
        for i, c in enumerate(chunks):
            if visual_len(c) < 5:
                if i > 0:
                    chunks[i - 1] += c
                    del chunks[i]
                else:
                    chunks[i + 1] = c + chunks[i + 1]
                    del chunks[i]
                changed = True
                break
    if len(chunks) == 1:
        caption_lines.append((s, e, chunks[0]))
    else:
        caption_lines.extend(distribute_time(s, e, chunks))

aligned = {"subtitles": [{"start": s, "end": e, "text": t} for s, e, t in caption_lines]}
out_json = ROOT / "work" / "captions" / "captions_aligned.json"
out_json.write_text(json.dumps(aligned, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {out_json}  ({len(caption_lines)} lines)")

out_txt = ROOT / "work" / "captions" / "captions_aligned.txt"
out_txt.write_text(
    "\n".join(f"[{s:7.2f} - {e:7.2f}] {t}" for s, e, t in caption_lines),
    encoding="utf-8",
)
print(f"Wrote {out_txt}")
over = [(s, e, t) for s, e, t in caption_lines if visual_len(t) > MAX_CHARS]
print(f"Lines over {MAX_CHARS} width: {len(over)}")
for s, e, t in over[:20]:
    print(f"  {s:.2f}-{e:.2f} ({visual_len(t):.1f}) {t}")
