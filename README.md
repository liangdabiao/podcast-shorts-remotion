# Podcast Shorts Remotion · 播客转竖屏短视频

Agent skill : 把一段播客/口播音频，变成**1080×1920 竖屏短视频**：中文字幕、章节场景、底部进度条、主题化配色。一条流水线直达预览成片。

> 真正的播客转视频，核心不是多复杂的动效，而是**字幕对、场景全、出片快**——剪完就能发。

***

## 这是什么

一套用 Whisper 转写 + Remotion 渲染的视频生产 **skill**。适合做：

- 🎙️ 开源项目安利播客（GitHub 项目介绍、工具测评）
- 📊 行业干货口播（AI 产品、市场调研、外贸技巧）
- 🧠 知识科普节目（把一段讲清楚一个主题）
- 📱 短视频号量产（同一批音频批量转竖屏成片）

**已验证案例**（全部 1080×1920 竖屏）：

https://www.bilibili.com/video/BV1TTMd6sEE7/?vd_source=86926e418c83af75f6850b5546388a79

https://www.bilibili.com/video/BV1XgMX6REpy/


***

## 怎样配置使用

前置条件很少——不需要任何生图/配音 API key，纯本地：

- **Python 3.10+**，`pip install openai-whisper`（本地转写，免费）
- **Node.js 16+**（Remotion 4 + React 19）
- **FFmpeg**（mp3→m4a、时长探测）
- **本机 Chrome**（渲染用，避免下载 113MB 的 Headless Shell）

在 codex / claude code / workbuddy 里：

> ❯ podcast-shorts-remotion skill 制作：把这段播客做成竖屏短视频： `播客音频.mp3`

把音频和逐字稿放进项目目录，剩下的交给流水线。

***

## 核心原理：为什么必须"快"

很多人做播客转视频，逐帧精修每个场景、反复渲染抽帧验收。**这样能出片，但太慢。**

真正的播客短视频，把每个环节都做减法，只有渲染时间是硬件地板：

```
并行启动(ffmpeg + whisper + npm install)    ← 三件事同时跑，互不等待
    ↓
一次写对字幕(写时就加逗号拆行)              ← 不靠"超宽报告"再回头改
    ↓
跳过冗余校验(compositions / tsc / 逐张stills) ← bundling 已含类型检查
    ↓
直达预览渲染(preview-low.mp4)                ← 12-13 fps 是唯一瓶颈
```

**速度来自流程裁剪，不是硬件。** 实测单核并发渲染最快（Chrome headless 截图是单线程瓶颈），多 worker 反而互相争抢变慢——详见下方基准表。

***

## 工具链

一条本地视频流水线，每个工具承担明确职责：

```
播客音频(voice.mp3)
        │
        ├─→ ffmpeg → voice.m4a              (AAC 渲染用音频)
        │
        ├─→ Whisper base → 转写原始字幕
        │       └─ 01_transcribe.py
        │            ↓
        │       人工校正 + 自动拆行(≤20视觉宽)
        │       └─ 02_build_aligned.py       ★核心
        │
        ├─→ 关键词强调 → captions.array.ts
        │       └─ 03_gen_ts_captions.py
        │
        └─→ Remotion (React) 场景/字幕/进度条 → 渲染 MP4
                └─ 04_gen_demodata.py → src/demoData.ts
```

| 工具                          | 职责                                  | 必需           |
| --------------------------- | ----------------------------------- | ------------ |
| **FFmpeg / ffprobe**        | mp3→m4a、时长探测                        | ✅ 核心         |
| **Whisper base**            | 本地中文转写（无需任何 API key）               | ✅ 核心         |
| **Python 3**                | 校正/拆行/关键词/生成 demoData（4 个脚本）        | ✅ 核心         |
| **Remotion 4 + React 19**   | 场景/字幕/进度条渲染 MP4                     | ✅ 核心         |
| **系统 Chrome**             | 逐帧截图渲染（跳过 Headless Shell 下载）        | ✅ 核心         |

**字幕校正原则**：以逐字稿为准修正 ASR 错误（`Code Code→Claude Code`、`调言→调研`、`Appache→Apache`），**保留 Whisper 的时间戳**，只改文字不改时间——这是音画同步的保证。

**前置条件**：

- Python 3.10+，`pip install openai-whisper`（首次会下载 base 模型 ~140MB）
- Node.js 16+，Remotion 4（`npm install`）
- 本机已装 Chrome
- 逐字稿/脚本（强烈建议，用于校正 ASR 和切章节）

***

## 快速开始（5 步）

### 1. 脚手架

```bash
python3 .claude/skills/podcast-shorts-remotion/scripts/scaffold_podcast_shorts_project.py \
  --project-dir "video/新项目/hf" \
  --audio "播客.mp3" \
  --script "播客脚本.md" \
  --title "视频标题"
```

脚手架自动放好音频、播种 4 个字幕脚本和 Remotion 模板，写 `manifest.json` 告诉你下一步。

### 2. 并行启动（省 2 分钟）

```bash
ffmpeg -y -i public/assets/audio/voice.mp3 -c:a aac -b:a 128k public/assets/audio/voice.m4a &
python work/captions/01_transcribe.py &
npm install &
```

三个命令**同时跑**，互不依赖。

### 3. 填字幕（一次写对）

转写期间读逐字稿，把 `02_build_aligned.py` 的 `SEGMENTS` 一次填好：

```python
SEGMENTS = [
    (8.14, 15.72, "今天刷 GitHub 时，挖到个特别实用的小项目，才 115 星。"),
    ...
]
```

**写的时候就加逗号**。每行 ≤20 视觉宽（中文=1、ASCII=0.6），天然停顿处的逗号让长句自动拆成合规行——别等超宽报告再回头改。

```bash
python work/captions/02_build_aligned.py     # 看 "Lines over 20 width: 0"
```

### 4. 关键词 + 场景

```bash
# 03_gen_ts_captions.py 填 ACCENT 关键词 → 跑出 captions.array.ts
# 04_gen_demodata.py 填 chapters + scenes → 跑出 src/demoData.ts
python work/captions/03_gen_ts_captions.py
python work/captions/04_gen_demodata.py
```

顺手改 `src/theme.ts` 配色（每项目一个主题，SKILL.md 有 6 套现成方案）。

### 5. 渲染 + 交付

```bash
TEMP=D:/video-spec-builder-main/.tmp npm run render:preview   # out/preview-low.mp4
```

**预览即成片**（540×960）。用户明确要高清才跑 `npm run render`（1080×1920）。

***

## 目录结构

```
podcast-shorts-remotion/
├── README.md                         ← 本文件（入口介绍）
├── SKILL.md                          ← 执行指令（给 agent：fast-mode 流水线 + 基准数据 + 已知坑）
├── scripts/
│   └── scaffold_podcast_shorts_project.py  一键脚手架（音频/脚本/字幕脚本全播种）
├── templates/
│   ├── caption-pipeline/             ← 4 个字幕脚本（带 EDIT 注释）
│   │   ├── 01_transcribe.py           whisper 转写（改 initial_prompt 项目词表）
│   │   ├── 02_build_aligned.py  ★     校正 + 拆行（≤20 视觉宽）
│   │   ├── 03_gen_ts_captions.py      关键词强调
│   │   └── 04_gen_demodata.py         scenes/chapters → demoData.ts
│   └── remotion-project/             ← 竖屏模板（1080×1920）
│       ├── package.json               remotion 4 + react 19（render:preview 已配 concurrency=1）
│       ├── remotion.config.ts         系统 Chrome + jpeg（已配好）
│       └── src/
│           ├── StudioTalkingHead.tsx  🔒所有场景+字幕渲染器
│           ├── demoData.ts            ✏️数据（04_gen_demodata.py 生成）
│           └── theme.ts               ✏️每项目配色（6 套现成方案）
```

**🔑 关键纪律**：🔒 `StudioTalkingHead.tsx` 是渲染器，改它影响所有项目；✏️ 数据层面只改 `demoData.ts` 和 `theme.ts`。

***

## 关键概念速查

### 字幕拆行规则（最常遇到）

每行 **≤20 视觉宽**：中文=1、ASCII 字符=0.6（所以 `GitHub`、`API` 这类英文占得少）。

```
MAX_CHARS = 20
"你直接查小红书上你关注的某个品牌最近的热度走势。"  ← 24 宽，超了
"你直接查小红书上，你关注的某个品牌最近的热度走势。" ← 加逗号 → 拆成 11+13 两行 ✓
```

拆行脚本按标点拆、长度不足 5 的段会并入相邻段、过长的行再按空格拆。**写字幕时就预防，比事后修快得多。**

### 场景类型（demoData 里可用）

| kind      | 内容                                    | 典型位置      |
| --------- | ------------------------------------- | --------- |
| `cover`   | 大标题（titleLines 多行）+ 副标题                | 片头        |
| `list`    | 小标题 + 3 项（index/label/value），逐项进场      | 主体章节      |
| `stat`    | 大数字 + 3 指标（适合"8 个技能""12 平台"）          | 强调数字      |
| `compare` | 二选一对比（适合 vs 型内容）                        | 对比章节      |
| `outro`   | 收尾标题 + 副标题                               | 片尾        |

每项 `appearAt` 控制进场时刻（秒，相对场景起点），第三项通常 `tone: "accent"` 高亮。

### cover 标题长度

每行视觉宽 ≤8 中文（或 8-10 英文含空格）。英文长名拆 3-4 行：

```
TikHub API
Skill
一键调 12 平台 社交数据
```

***

## FAQ

**Q: 为什么 `--concurrency=1` 反而最快？**
A: 实测基准（i5-12450H / 16GB，540×960 预览）：

| 并发 | 300帧耗时 | 帧率 |
| -- | ------ | -- |
| **c1** | **44s** | **12.5** |
| c4 | 51s | 9.7 |
| c8 | 54s | 8.8 |

Chrome headless 逐帧截图是单线程瓶颈，多 worker 互相争抢变慢。**模板已默认 concurrency=1。**

**Q: 一个 7 分钟播客要渲多久？**
A: 渲染 ~10-13 fps 是硬件地板，7.5 分钟音频 = 13710 帧 ≈ **18 分钟**。这是正常速度，不是卡住。3 分钟音频 ≈ 8 分钟。流程裁剪只能省那 3-5 分钟的启动/校验开销，渲染本身省不了。

**Q: 为什么有时候长视频越渲越慢？**
A: C 盘 99% 满时 Chrome 临时文件写满导致降速（实测 300帧 12.5fps → 900帧 10.2fps）。渲染时加 `TEMP=D:/video-spec-builder-main/.tmp` 绕开，并提醒用户清理 C 盘。

**Q: 为什么跳过 `tsc --noEmit` 和逐张 stills？**
A: Remotion 渲染时 bundling 会做类型检查（报错会失败）；stills 每张都要重启 Chrome 浪费 ~5s。fast-mode 只在 cover/outro 各抽一帧看标题，或直接看预览片。

**Q: 转写错得离谱怎么办？**
A: Whisper base 对中文专业名词错得很固定（`EduLab→EduLab`、`sympy→SIMPIE`）。两个办法：① `01_transcribe.py` 的 `initial_prompt` 写满项目词表（人名/技术栈/数字，效果立竿见影）；② 转写后对照逐字稿逐段校正 `02_build_aligned.py` 的 SEGMENTS——**保留时间戳只改文字**。

**Q: 能复用已有项目的模板吗？**
A: 能。每个新项目都从同一模板脚手架，主题色按 SKILL.md 的 6 套现成方案挑一个微调，场景结构照 demoData 的 list/stat 套路写。已验证 6 个项目全走同一条流水线。

***

## 进一步阅读

- **执行指令**（给 agent）：[`SKILL.md`](SKILL.md) — fast-mode 流水线 + 实测基准 + 已知坑
- **模板 README**：`templates/remotion-project/README.md` — 项目内各脚本怎么跑
- **字幕流水线脚本**：`templates/caption-pipeline/` — 4 个脚本带 EDIT 注释
- **已验证案例**：`video/股票/hf`、`geo-skill/hf`、`外贸ai/hf`、`edulab/hf`、`tikhub项目/hf`（各项目的 `out/preview-low.mp4` 即成品）

***

## 适用范围

只要输入是一段播客/口播音频 + 一份能切章节的内容，就能用这套流程。不限于开源安利——产品介绍、知识科普、行业干货、课程讲解都适用。真正让播客短视频能发出去的，不是多复杂的动效，而是字幕对得上、场景跟得上、出片赶得上热点。



感谢 https://linux.do 社区支持