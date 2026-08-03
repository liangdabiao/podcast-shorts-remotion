"""Assemble src/demoData.ts from captions.array.ts + scene definitions.

Usage:
    python work/captions/04_gen_demodata.py

Reads:  work/captions/captions.array.ts
Writes: src/demoData.ts

EDIT: fill in HEADER with project-specific:
- title, durationSeconds (from ffprobe)
- chapters (label + start time)
- scenes (cover / list / stat / compare / outro)

SCENE KINDS:
- cover:    titleLines (array of rich text arrays), subtitle
- list:     heading, items [{index, label, value, tone?, appearAt?}]
- stat:     number, unit, title (rich text), metrics [{label, value, tone?, appearAt?}]
- compare:  heading, choices [{code, title, subtitle, tone?, appearAt?}]
- outro:    title, subtitle

appearAt is seconds after scene start; items animate in sequentially.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
caption_body = (ROOT / "work/captions/captions.array.ts").read_text(encoding="utf-8").rstrip()

# EDIT: replace everything below with project-specific content
HEADER = '''import type {StudioTalkingHeadProps} from "./StudioTalkingHead";

export const demoProject: StudioTalkingHeadProps = {
  title: "__PROJECT_TITLE__",
  fps: 30,
  durationSeconds: __DURATION_SECONDS__,
  voiceAudio: "assets/audio/voice.m4a",
  talkingHeadVideo: "",
  chapters: [
    {label: "开篇", start: 0},
  ],
  scenes: [
    {
      kind: "cover",
      start: 0,
      eyebrow: "CODE AI 播客",
      titleLines: [
        [{text: "__TITLE_LINE_1__"}],
        [{text: "__TITLE_LINE_2__", tone: "accent"}],
      ],
      subtitle: "__SUBTITLE__",
    },
    {
      kind: "list",
      start: 20,
      eyebrow: "章节标签",
      heading: "两行标题\\n用 \\n 换行",
      items: [
        {index: "01", label: "标签", value: "内容", appearAt: 6.0},
        {index: "02", label: "标签", value: "内容", appearAt: 14.0},
        {index: "03", label: "标签", value: "高亮内容", tone: "accent", appearAt: 22.0},
      ],
    },
    {
      kind: "stat",
      start: 60,
      eyebrow: "数字章节",
      number: "8",
      unit: "个",
      title: [{text: "大数字标题"}],
      metrics: [
        {label: "指标1", value: "说明", appearAt: 8.0},
        {label: "指标2", value: "说明", appearAt: 16.0},
        {label: "指标3", value: "高亮", tone: "accent", appearAt: 24.0},
      ],
    },
    {
      kind: "outro",
      start: __DURATION_SECONDS__,
      eyebrow: "下期再见",
      title: "去 GitHub 试试",
      subtitle: "__PROJECT_TITLE__",
    },
  ],
'''

FOOTER = "};\n"

out = ROOT / "src/demoData.ts"
out.write_text(HEADER + caption_body + "\n" + FOOTER, encoding="utf-8")
print(f"Wrote {out}")
