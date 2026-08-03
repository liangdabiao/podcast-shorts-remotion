"""Whisper base local transcription with Chinese initial_prompt.

Usage:
    python work/captions/01_transcribe.py

Reads:  public/assets/audio/voice.mp3
Writes: work/captions/captions.raw.json
"""
import json
from pathlib import Path
import whisper

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "public/assets/audio/voice.mp3"
OUT = ROOT / "work/captions/captions.raw.json"

model = whisper.load_model("base")
result = model.transcribe(
    str(AUDIO),
    language="zh",
    word_timestamps=True,
    initial_prompt=(
        # EDIT: fill with project-specific terms, names, tech stack, numbers
        "以下是普通话播客。"
    ),
    verbose=False,
)

segs = []
for s in result["segments"]:
    segs.append({
        "start": round(float(s["start"]), 2),
        "end": round(float(s["end"]), 2),
        "text": s["text"].strip(),
    })

OUT.write_text(json.dumps({"segments": segs, "text": result["text"]}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Wrote {OUT}")
print(f"  segments: {len(segs)}")
print(f"  duration: {segs[-1]['end']:.1f}s")
for s in segs[:10]:
    print(f"  [{s['start']:.1f}-{s['end']:.1f}] {s['text']}")
