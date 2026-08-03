import {staticFile} from "remotion";

const fontFiles = [
  {family: "Noto Sans SC", file: "assets/fonts/NotoSansSC-400.ttf", weight: "400"},
  {family: "Noto Sans SC", file: "assets/fonts/NotoSansSC-700.ttf", weight: "700"},
  {family: "Noto Sans SC", file: "assets/fonts/NotoSansSC-900.ttf", weight: "900"},
  {family: "Space Grotesk", file: "assets/fonts/SpaceGrotesk-400.ttf", weight: "400"},
  {family: "Space Grotesk", file: "assets/fonts/SpaceGrotesk-700.ttf", weight: "700"},
] as const;

if (typeof document !== "undefined" && !document.getElementById("studio-font-faces")) {
  const style = document.createElement("style");
  style.id = "studio-font-faces";
  style.textContent = fontFiles
    .map(
      (font) => `@font-face {
  font-family: "${font.family}";
  src: url("${staticFile(font.file)}") format("truetype");
  font-weight: ${font.weight};
  font-style: normal;
  font-display: swap;
}`,
    )
    .join("\n");
  document.head.appendChild(style);
}

// Default theme: warm cream + indigo + amber (EduLab style).
// Per project: pick a near variant from SKILL.md theme table and tweak.
export const colors = {
  canvas: "#f5f1e8",
  ink: "#1f1a30",
  muted: "#5d5577",
  weak: "#a99fc0",
  line: "rgba(31,26,48,0.10)",
  lineStrong: "rgba(31,26,48,0.16)",
  accent: "#5b4bff",
  gold: "#e08a1e",
  topbar: "#1f1a30",
  topbarMuted: "rgba(255,255,255,0.58)",
  topbarSeparator: "#6a6080",
  gridLine: "rgba(40,30,70,0.22)",
  gridLineStrong: "rgba(91,75,255,0.28)",
  gridWarm: "rgba(224,138,30,0.28)",
  glass: "rgba(255,255,255,0.74)",
  white: "#ffffff",
};

export const fonts = {
  sans: '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
  mono: '"Space Grotesk", "SFMono-Regular", "Menlo", "Consolas", monospace',
};

export const layout = {
  width: 1080,
  height: 1920,
  fps: 30,
  topbarHeight: 88,
  safeTop: 240,
  safeX: 80,
  safeBottom: 440,
  pipSize: 206,
  pipRight: 104,
  pipBottom: 150,
  captionBottom: 200,
  captionMaxWidth: 940,
};
