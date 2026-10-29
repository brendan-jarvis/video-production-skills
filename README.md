# Video production skills

Agent skills for making videos, with local FFmpeg tools you run on your own machine.

Two kinds of job:

- A **montage**: photos, Live Photos and clips set to music (a trip, an event, a race).
- A **directed piece**: a short film, music video, explainer, promo, or Short/Reel, planned from a brief. Footage can be the user's, generated, or both.

The skills are Markdown files with a short YAML header. Any agent that can read a skill and run local commands can use them, including Claude Code, Cursor, and Codex.

## Install

Clone this repository and copy each directory under `skills/` into the skills folder your agent reads:

```bash
git clone https://github.com/brendan-jarvis/video-production-skills.git
cd video-production-skills
mkdir -p ~/.cursor/skills
cp -a skills/video-production skills/ffmpeg-tools skills/music-and-beats skills/review-and-qc ~/.cursor/skills/
```

Other agents use a different folder. Claude Code often reads `~/.claude/skills/`. Codex often reads `~/.codex/skills/`. Copy the same four directories there.

Keep the clone. The skills run `scripts/`, `templates/` and `references/` by paths relative to the repository root, so commands need that directory as the working directory.

## Requirements

- **ffmpeg** and **ffprobe** on `PATH`. 6.1 or newer is recommended. 5.x still runs; the tools print a deprecation warning.
- **python3**, standard library only. 3.10 or newer is recommended. 3.9 still runs and prints a deprecation warning.
- Optional: **librosa** or **aubio**, for beat detection.
- Optional: a local speech engine (whisper.cpp, faster-whisper, or parakeet) only if you want transcription.

On macOS, Homebrew's `ffmpeg` formula is lean (no drawtext or subtitles filter). `ffmpeg-full` is keg-only:

```bash
brew install ffmpeg-full
export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"
```

On Windows, if the build is missing drawtext, subtitles, or zscale, use the full [Gyan.FFmpeg](https://www.gyan.dev/ffmpeg/builds/) build.

`python3 scripts/_contract.py doctor` reports what this machine can do, including `ffmpeg_security` advisories from a table shipped with the scripts. It does not contact the network.

## Skills

| Skill | Use it when |
| --- | --- |
| `video-production` | You want a video made or edited: a montage set to music, or a directed piece from a brief. |
| `ffmpeg-tools` | You are running local FFmpeg: probe first, call the scripts, verify the output, handle iPhone HDR, avoid keyframe-cut mistakes. |
| `music-and-beats` | You are choosing music, mapping a song, detecting beats, or ducking music under voice. |
| `review-and-qc` | You are checking a rendered cut: frames, jitter, beats, loudness, safe areas, platform checks. |

`video-production` is the one to start with. It calls the other three.

## Example

Someone hands over a folder of trip photos and a CC0 track and wants a vertical reel.

1. `video-production` opens `videos/<slug>/`, writes a short brief (9:16, 25-45 seconds, hook in the first two seconds), and shows a storyboard before any full render.
2. `music-and-beats` checks the track's licence, maps the drop, and detects beats with librosa or aubio when one of those is installed.
3. `ffmpeg-tools` probes each file, keeps or converts iPhone HDR on purpose, and assembles the cut with `scripts/` (for example `scripts/cut.py`, `scripts/render.py`, `scripts/loudness.py`). It does not hand-write an ffmpeg command for a step a script already covers.
4. `review-and-qc` stops after a 30 second test render, then checks safe areas, beats, and loudness before `published/v1.mp4`.

A single file check, with no project around it:

```bash
python3 scripts/probe.py clip.mov --json
python3 scripts/check.py cut.mp4 --platform reels
```

## Tools

`scripts/` is the local editor: probe, cut, join, fit, scenes, colour (including HDR to SDR and LUTs), stabilize, straighten, speed changes, freeze frames, crop, overlay, captions, loudness, music ducking, render, and export. `templates/` holds platform presets (YouTube, Shorts, Reels, TikTok, and others). `references/` holds the longer notes (gotchas, devices, the flag list).

The same scripts are available over MCP (stdio):

```bash
python3 mcp/server.py
```

The server name is `video-tools`. `tools/list` advertises a core set; set `FFMPEG_SKILL_MCP_FULL=1` to list every script. The environment variables the scripts already read keep the `FFMPEG_SKILL_*` names.

## Inspiration and credits

These skills pull together techniques and guides from a lot of creators. Inspiration includes:

- [kajisho5 / ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) — the source of the FFmpeg tool scripts, platform templates and reference notes, used under MIT. The copyright and permission notice, and the file list, are in [NOTICE](NOTICE).
- [Ashe (@ashebytes)](https://x.com/ashebytes/status/2115215620279263329) — video-editing workflow tips.
- The Director video bot template — the pitch-concepts, style line, key frames, takes and versioned-cut process.
- [Filip Skrzesinski (@uptightchill)](https://x.com/uptightchill/status/2115497754021786060) — search [Subframe Motion](https://www.subframe.com/motion) for inspiration, then pull a working example before building an animation.

and many other creators whose posts and guides shaped this workflow.

## Tests

```bash
python3 tests/test_all.py
python3 tests/test_contract.py
```

GitHub Actions runs the same commands. ffmpeg must be installed.
