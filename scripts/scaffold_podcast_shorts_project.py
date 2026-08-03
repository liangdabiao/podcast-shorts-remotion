#!/usr/bin/env python3
"""Scaffold a podcast-shorts Remotion project (1080x1920 vertical).

Creates a project dir from templates/remotion-project, copies the podcast
audio in as voice.mp3 + voice.m4a, seeds the caption pipeline scripts, and
writes a manifest.json describing what was created.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_DIR / "templates/remotion-project"
PIPELINE_DIR = SKILL_DIR / "templates/caption-pipeline"


def copy_tree(src: Path, dst: Path) -> None:
    for item in src.rglob("*"):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def replace_placeholders(project: Path, replacements: dict[str, str]) -> None:
    for path in project.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".mp3", ".mp4", ".m4a", ".wav", ".png", ".jpg", ".jpeg", ".ttf", ".woff2"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        changed = False
        for key, value in replacements.items():
            if key in text:
                text = text.replace(key, value)
                changed = True
        if changed:
            path.write_text(text, encoding="utf-8")


def ffprobe_duration(path: str) -> float | None:
    if not path:
        return None
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-hide_banner",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nw=1:nk=1",
                path,
            ],
            text=True,
        ).strip()
        return round(float(out), 3)
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="创建播客转竖屏短视频 Remotion 项目脚手架。")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--audio", help="播客/口播音频（mp3/m4a/wav）")
    parser.add_argument("--script", help="播客逐字稿 md")
    parser.add_argument("--title", default="Podcast Shorts Remotion")
    parser.add_argument("--duration", type=float)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = Path(args.project_dir).expanduser().resolve()
    if project.exists() and any(project.iterdir()) and not args.force:
        raise SystemExit(f"{project} already exists and is not empty. Re-run with --force to overwrite template files.")

    project.mkdir(parents=True, exist_ok=True)
    copy_tree(TEMPLATE_DIR, project)
    for src in sorted(PIPELINE_DIR.iterdir()):
        if src.is_file():
            dst = project / "work/captions" / src.name
            shutil.copy2(src, dst)

    audio_name = ""
    if args.audio:
        audio = Path(args.audio).expanduser().resolve()
        audio_dst = project / "public/assets/audio"
        audio_dst.mkdir(parents=True, exist_ok=True)
        # copy original as voice.mp3 (ASR/source)
        shutil.copy2(audio, audio_dst / "voice.mp3")
        audio_name = audio.name

    if args.script:
        shutil.copy2(Path(args.script).expanduser().resolve(), project / "work" / "script.md")

    duration = args.duration or ffprobe_duration(args.audio) or 60
    duration = round(float(duration), 3)

    replace_placeholders(project, {
        "__PROJECT_TITLE__": args.title,
        "__DURATION_SECONDS__": str(duration),
    })

    manifest = {
        "title": args.title,
        "duration": duration,
        "audio": audio_name,
        "next_steps": [
            "ffmpeg -y -i public/assets/audio/voice.mp3 -c:a aac -b:a 128k public/assets/audio/voice.m4a",
            "python work/captions/01_transcribe.py   (edit initial_prompt first)",
            "edit work/captions/02_build_aligned.py  SEGMENTS from captions.raw.json + script",
            "python work/captions/02_build_aligned.py",
            "edit work/captions/03_gen_ts_captions.py  ACCENT keywords",
            "python work/captions/03_gen_ts_captions.py",
            "edit work/captions/04_gen_demodata.py  scenes/chapters",
            "python work/captions/04_gen_demodata.py",
            "npm install",
            "npm run render:preview   (check out/preview-low.mp4)",
        ],
    }
    (project / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(project)


if __name__ == "__main__":
    main()
