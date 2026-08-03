---
name: podcast-shorts-remotion
description: 把一段播客/口播音频快速变成 1080×1920 竖屏短视频（中文字幕、章节场景、底部进度条、主题化配色）。输入是音频（+逐字稿/脚本），输出是预览 MP4。核心是"快"：并行转写、一次写对、跳过冗余校验、直达预览渲染。当用户给一个播客 mp3/音频要生成视频、说"继续 xxx项目/""把这段音频做成视频"、或要求快速批量出片时，必须使用这个 skill。
---

# Podcast Shorts Remotion

把一个中文播客/口播音频转成 1080×1920 竖屏短视频的**高速流水线**。由 talking-head-remotion 演进而来，砍掉口播人像/录屏/BGM/SFX 等重环节，聚焦：**字幕正确 + 章节场景 + 主题配色 + 快速出预览片**。

## 输入要求

- **音频（必须）**：一段播客/口播 mp3/m4a/wav。它是时间轴的唯一真相。
- **逐字稿/脚本（强烈建议）**：用于校对 Whisper 转写错误、找关键词、切章节。通常文件名是 `*_播客脚本.md`。

## 新项目：一键脚手架

```bash
python3 ./skills/podcast-shorts-remotion/scripts/scaffold_podcast_shorts_project.py \
  --project-dir "/path/to/新项目/hf" \
  --audio "/path/to/音频.mp3" \
  --script "/path/to/播客脚本.md" \
  --title "视频标题"
```

脚手架会：从 `templates/remotion-project` 复制可运行模板（src/ + public 字体 + SFX + package.json）、把音频放 `public/assets/audio/voice.mp3`、播种 4 个字幕脚本到 `work/captions/`、写 `manifest.json`（含 next_steps）。

## 高速工作流（Fast Mode）

### 阶段 0：并行启动（省 ~2 分钟）

`ffmpeg mp3→m4a` 与 `whisper 转写` **同时跑**（它们互不依赖）：

```bash
ffmpeg -y -i public/assets/audio/voice.mp3 -c:a aac -b:a 128k public/assets/audio/voice.m4a
python work/captions/01_transcribe.py
```

### 阶段 1：字幕校正 + 拆行（一次写对）

1. 转写期间就读脚本，把 `02_build_aligned.py` 的 `SEGMENTS` 一次填好：
   - 去掉片头 Coze/片尾 tag（通常是前 1-3s），口播从第一个有效句开始
   - 用脚本校对 ASR 错误（EduLab→EduLab、调言→调研、Code Code→Claude Code 这类）
   - **保留 Whisper 的 start/end 时间戳**
   - **写的时候就加逗号预防超宽**（见下），不要等超宽报告再改
2. `python work/captions/02_build_aligned.py`
3. 看 `Lines over 20 width:` 报告。**有超宽就一次性批量 Edit**，别一条条改。改的是 `02_build_aligned.py` 里的 SEGMENTS 文本，再重跑。

**拆行规则**：每行 ≤20 视觉宽（中文=1，ASCII=0.6）。天然停顿处加逗号让长句按逗号拆成 ≤20 的行。示例：
`"你直接查小红书上你关注的某个品牌最近的热度走势。"`(24宽) → 改成 `"你直接查小红书上，你关注的某个品牌最近的热度走势。"` → 拆成 11+13 两行。

### 阶段 2：关键词 + demoData（复用模板）

1. `03_gen_ts_captions.py` 填 `ACCENT` 关键词列表（项目名/技术词/数字/平台），跑出 `captions.array.ts`
2. `04_gen_demodata.py` 填 `chapters` + `scenes`（cover / list / stat / compare / outro），跑出 `src/demoData.ts`
3. **一次性改好 theme.ts 配色**（每项目一个主题色，参考下面配色表）

三个脚本都在 whisper 转写完成前写好，转写一结束立即批量执行：

```bash
python work/captions/02_build_aligned.py && python work/captions/03_gen_ts_captions.py && python work/captions/04_gen_demodata.py
```

### 阶段 3：npm install（可与阶段 1/2 并行）

```bash
npm install   # 后台跑，同时继续写脚本
```

### 阶段 4：直达预览渲染（跳过冗余校验）

```bash
TEMP=D:/video-spec-builder-main/.tmp npm run render:preview
```

**不要**跑 `npx remotion compositions`、`npx tsc --noEmit`、逐张 stills 验证。理由见"为什么快"。渲染约 8-18 分钟（硬件地板，见下）。

**可选最轻校验**：只在 cover 和 outro 两个时间点各渲 1 张 still 看标题/布局，或者直接看预览片抽 2-3 帧。cover 标题超宽时拆成 3-4 行（中文行 ≤8 字或英文行按词拆）。

### 阶段 5：交付

- 预览片在 `out/preview-low.mp4`（540×960，crf=28）
- **preview 即成片**：默认交付 preview，不自动跑 1080p 最终渲染。用户明确要高清才跑 `npm run render`（1080×1920，约 20-40 分钟）。
- 汇报时给：预览路径、时长、章节数、字幕条数、超宽数、ASR 纠错亮点。

## 场景与章节设计要点

- **章节**：每个场景开头设一个章节标签（≤3 字），顶部进度条显示。
- **场景节奏**：一个 scene 对应播客一个逻辑块。典型结构：
  cover（标题）→ 是什么 list → 痛点 list → 核心本事 list → stat 大数字 → 分块 list（1-3 个）→ 架构/技术 list → 适合谁 list → outro。
- **cover 标题**：每行视觉宽 ≤8 中文（或 8-10 英文含空格）。英文长名拆 3-4 行。例：`TikHub API / Skill / 一键调 12 平台 社交数据`。
- **list 场景**：3 项，`appearAt` 6s/14s/22s 依次进场；第三项 `tone: "accent"` 做强调。
- **stat 场景**：大数字 + 3 个指标。
- **所有 heading**：注意模板不渲染 `\n` 换行（会变成软换行），heading 文字要短到单行放得下（约 9-10 中文内），或接受自然换行。

## 每项目主题配色（已沉淀）

| 项目 | 主题 | canvas / accent / gold / topbar |
|---|---|---|
| 股票尽调 | 红+金 | #fdf3ef / #d9270d / #e08a1e / #1a1020 |
| seekmoney | 翠绿+金 | #f0f7f2 / #0d8a4f / #e08a1e / #0b2416 |
| geo-skill | 靛蓝+青 | #eef2f8 / #3b5bff / #00a3c7 / #0c1a2e |
| 外贸ai | 青绿+琥珀 | #eef5f2 / #0d9488 / #d97706 / #0a2a28 |
| edulab | 米色+靛蓝 | #f5f1e8 / #5b4bff / #e08a1e / #1f1a30 |
| tikhub | 亮粉+青 | #f6f3fb / #ff2d77 / #00b8d4 / #1a1230 |

新项目挑一个接近的微调，别从零配。

## 为什么这么快（实测基准）

硬件 i5-12450H / 16GB：`--concurrency=1` 单核渲染最快（300帧：c1=44s, c4=51s, c8=54s）。Chrome headless 截图是单线程瓶颈，多 worker 反而争抢变慢。GPU 已在用（--gl=angle）。**渲染速度 ~10-13 fps 是硬件地板**，无法突破，只能砍流程开销：

| 砍掉的步骤 | 省多少 |
|---|---|
| `remotion compositions`（多此一举） | ~30s |
| `tsc --noEmit`（bundling 已含类型检查） | ~10s |
| 12 张 stills 逐张渲（每次重启 Chrome ~5s） | ~60s+ |
| 逐条 Edit 超宽行 | 分钟级 |
| 串行跑 ffmpeg/whisper/install | ~2-3 min |

> 机器实测：3.5 分钟音频全流程 ~20 分钟（其中渲染 ~10 min）；7.5 分钟音频渲染 ~18 min。这是**正常速度**，不是卡住。

## 已知坑

- **C 盘 99% 满会拖慢长渲染**（300帧 12.5fps → 900帧 10.2fps）。渲染时 `TEMP=D:/video-spec-builder-main/.tmp`。提醒用户清理 C 盘。
- 模板 `remotion.config.ts` 已设 `Config.setBrowserExecutable(系统 Chrome)`，不要改成 playwright/chrome-headless-shell（中国网络下下载会卡死）。
- 字幕 CAPTION 用底部居中安全区，模板已处理竖屏 shrink-to-fit（`left:0;right:0;margin:auto`），不要改回 `left:50%;translate`。
- Windows 下跑 python 一律 `python`（不是 python3）；路径含中文没关系。
- 不要自动启动 1080p 最终渲染（`render`），preview 确认后问用户。

## 模板文件位置

- 模板项目：`templates/remotion-project/`（src/StudioTalkingHead.tsx 是全部场景+字幕渲染器，demoData.ts 是数据，theme.ts 是配色/字体/布局）
- 字幕流水线：`templates/caption-pipeline/01_transcribe.py` ~ `04_gen_demodata.py`
- 脚手架：`scripts/scaffold_podcast_shorts_project.py`
