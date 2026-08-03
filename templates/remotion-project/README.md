# Podcast Shorts Remotion

1080×1920 竖屏短视频模板：把播客/口播音频变成带中文字幕、章节场景、底部进度条的视频。

## 快速开始

```bash
npm install
ffmpeg -y -i public/assets/audio/voice.mp3 -c:a aac -b:a 128k public/assets/audio/voice.m4a
# 字幕流水线（顺序执行，各脚本头有说明）：
python work/captions/01_transcribe.py
# 编辑 02_build_aligned.py 填 SEGMENTS
python work/captions/02_build_aligned.py
# 编辑 03_gen_ts_captions.py 填 ACCENT
python work/captions/03_gen_ts_captions.py
# 编辑 04_gen_demodata.py 填 scenes
python work/captions/04_gen_demodata.py
npm run render:preview   # out/preview-low.mp4
```

## 脚本

- `npm run studio` — Remotion studio 预览
- `npm run render:preview` — 540×960 低清预览（crf=28, concurrency=1）
- `npm run render` — 1080×1920 最终（很慢，用户明确要求才跑）

## 结构

- `src/StudioTalkingHead.tsx` — 场景 + 字幕渲染器（不要改，除非要改动效）
- `src/demoData.ts` — 数据（由 04_gen_demodata.py 生成）
- `src/theme.ts` — 配色/字体/布局（每项目改主题色）
- `work/captions/` — 字幕流水线脚本 + 中间产物
- `public/assets/audio/` — voice.mp3（源）+ voice.m4a（渲染用）+ SFX
