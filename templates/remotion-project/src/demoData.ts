import type {StudioTalkingHeadProps} from "./StudioTalkingHead";

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
      kind: "outro",
      start: __DURATION_SECONDS__,
      eyebrow: "下期再见",
      title: "去 GitHub 试试",
      subtitle: "__PROJECT_TITLE__",
    },
  ],
  captions: [
    {start: 0, end: 2, parts: [{text: "字幕将由 build_aligned.py 自动生成"}]},
  ],
};
