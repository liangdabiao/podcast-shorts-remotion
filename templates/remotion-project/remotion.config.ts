import {Config} from "@remotion/cli/config";

// Use system Chrome to avoid storage.googleapis.com chrome-headless-shell download.
// Edge no longer works (old-headless removed); use stable Chrome only.
Config.setBrowserExecutable("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe");
Config.setVideoImageFormat("jpeg");
