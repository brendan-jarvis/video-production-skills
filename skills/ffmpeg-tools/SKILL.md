---
name: ffmpeg-tools
description: >-
  Use when running local FFmpeg for a video edit: probe before planning, call
  the repository scripts instead of hand-writing ffmpeg, verify the output,
  handle iPhone HDR and colour, and avoid keyframe-cut mistakes.
---

# FFmpeg tools

The repository scripts in `scripts/` are the editor. Paths below are relative to the repository root. Run `python3 scripts/<name>.py --help` before guessing a flag. The long flag list is `references/scripts.md`. Device notes are `references/devices.md`. The long form of the rules below is `references/gotchas.md`.

Do not hand-write `ffmpeg` or `ffprobe` for a step a script already covers. A raw command skips the checks the scripts make. If none of the scripts can do the job, say so and name the closest script.

`python3 scripts/_contract.py doctor` answers what this machine can do after a failure, or when asked. Do not start every job with it.

## Probe first

Run `scripts/probe.py` on each input you plan from: duration, size, fps, codecs, channels, rotation, `variable_frame_rate_suspected`, `hdr`, `bt2020_or_hdr`. Plan from those numbers. A writing script's `--json` already probes its own output, so you do not need a separate probe before every edit.

## Verify after every step

A step is done only when the script exits 0 and the output probe matches the request (duration, size, fps, audio). A non-zero exit, a missing or empty file, or a probe that contradicts the request is a failure. Report the script's error. Do not describe a fix you did not run.

Before a delivery, run `scripts/check.py OUTPUT --platform NAME`. Format rows (codec, pixel format, size, true peak, colour tags, variable frame rate) are safe to fix. Judgement rows change the content: duration, aspect, frame rate, loudness. Fix those only when the request implies the answer. Otherwise state the choice and its cost. Mention warnings. Do not chase them.

When the picture changed (crop, scale, colour, captions, overlays, a join that scales a clip to the first frame), run `scripts/look.py OUTPUT --tiles 3x2` and look at the PNG. A probe cannot see a caption on a face. For audio-only work, say that a picture check is not needed.

## Plan, then execute

Use `--dry-run --json` before a long encode. Trust the JSON, not a one-line summary. Writing tools write nothing under `--dry-run`. These still measure, and they do not write the finished file: `sync`, `multicam`, `scenes`, `report`, `cropdetect`, `silence`, `loudness`, `check`, `stabilize`, and `overlay` when it is measuring a multi-line title on some FFmpeg 8 builds. `probe.py` still runs ffprobe. `verify.py` accepts the flag and ignores it. The `dry_run` field of `python3 scripts/_contract.py --json` is the exact list.

Never point `-o` at a file you did not create in this job unless the user asked for it to be replaced. `--overwrite` is the only way to replace an existing output. Never overwrite the user's original.

## Order

Colour first (HDR to SDR, or a LUT), then cut, join, fit, captions and overlays, then audio and loudness, then export. Frame changes before text, so captions are sized for the final frame. Re-encode as few times as possible. Three or more steps belong in one `scripts/render.py` project rather than a chain of one-off commands. A delivery with no other editing can be one template: `scripts/render.py --template NAME INPUT` (`--list-templates`).

## HDR, iPhone, and log

SDR outputs are H.264 tagged BT.709. When `probe.py` reports `bt2020_or_hdr`, the editing scripts keep a 10-bit HEVC path and the source colour tags. That includes iPhone Dolby Vision and HLG. Do not tag BT.709 onto BT.2020 pixels.

- Keep HDR when the destination can show it (YouTube, phones). `scripts/export.py --preset youtube-hdr` keeps it.
- For an SDR-only destination, a LUT, or an H.264 file, run `scripts/color.py --to-sdr` first. `export.py` platform presets are SDR and warn on HDR input. Retagging is not a conversion.
- A BT.2020 file that is not HDR (`hdr` false, `bt2020_or_hdr` true) still has wide-gamut primaries. It needs `--to-sdr` before a BT.709 delivery.
- Log footage (S-Log, V-Log, C-Log) looks grey and is tagged SDR. `scripts/probe.py --analyze` sets `looks_like_log`. Apply the manufacturer's `.cube` with `scripts/color.py --lut` before anything else.
- 10-bit is not HDR. Trust `hdr`, not bit depth. GoPro 10-bit SDR should not be tone-mapped.
- iPhone movies carry extra metadata tracks. Scripts use the first audio track.
- Detail: `references/gotchas.md#hdr-and-colour`, `references/gotchas.md#log-footage`, `references/devices.md`.

Use one grade for every source in the piece so mixed cameras match. Natural, ungraded colour is the default when nobody asked for a look.

## Keyframe cuts and variable frame rate

A lossless `scripts/cut.py` cut can start up to one GOP earlier than asked (`start_snapped`). The script re-encodes when that gap is over 0.5 seconds. `--edit-list` on a single-segment `.mp4`, `.m4v` or `.mov` hides the pre-roll in the edit list. A player that ignores edit lists shows it. The end still lands on a packet boundary.

Open-GOP HEVC (iPhone High Efficiency) re-encodes a `--segments` join. So does a B-frame `.mp4` or `.mov` join whose later piece starts between keyframes. Start on a keyframe, or write `.mkv`, if you need a stream copy.

Phone and screen recordings are often variable frame rate (`variable_frame_rate_suspected`). Re-encodes conform to a constant rate. `cut.py` re-encodes on that by default. `--accurate` is the frame-exact path.

Detail: `references/gotchas.md#keyframe-cuts`, `references/gotchas.md#variable-frame-rate`.

## Safe area, loudness, captions

Platform safe fractions and loudness targets live in `scripts/_platforms.py` and `templates/`. Roughly: TikTok covers the bottom 22 percent, the right 14 percent and the top 10 percent; Reels about 20/12/8; Shorts about 18/12/6. YouTube, X, LinkedIn and Facebook use a 5 percent title-safe border. `scripts/caption.py --platform NAME`, `scripts/graphics.py --platform NAME` and `scripts/look.py --safe NAME` use that table. A file can pass `check.py` and still hide the caption under the app's buttons.

Fit to the delivery size before burning captions. Captions burned small and then scaled go soft.

Loudness targets in the presets are about -14 LUFS for most social video, -16 for podcast, -23 for broadcast, true peak at or under -1 dBTP. The montage default when no platform is named is about -16 LUFS. Do not normalise room tone or near-silence up to a speech target. Detail: `references/gotchas.md#loudness-and-ambience`, `references/gotchas.md#platform-safe-zones`.

## Still zoom and pan

`scripts/insert.py --zoom in|out` (optional `--pan`) is the Ken Burns move on a photo. `--zoom-method smooth` is the default: an oversampled scale with `eval=frame` and a per-frame placement, so a slow move does not step on whole output pixels. `--zoom-method zoompan` keeps the older filter. It is faster, and it rounds the window to integer pixels, which can jitter. If you choose it, check `scripts/look.py` or consecutive frames before you keep the shot. Detail: `references/gotchas.md#ken-burns-zoom`.

## Encode

Default SDR re-encodes are x264. HDR stays HEVC Main10. `scripts/export.py --preset h265` is CPU HEVC (libx265). `--hw` is Apple VideoToolbox only, and a GPU encode is not CRF-equivalent. The scripts fall back to the CPU when VideoToolbox refuses the job.

On NVIDIA, a final HEVC encode with `hevc_nvenc` at constant quality around 19 is an option when `doctor` lists that encoder. If it is missing or the encode fails, use `--preset h265` or the default H.264. Do not rebuild the whole edit as a hand-written ffmpeg command to reach the GPU.

## Shared flags

`--json`, `--json-brief`, `--dry-run`, `--fast`, `--progress`, `--timeout SECONDS` (`0` means no limit), `--overwrite`, `--plan FILE`. Re-encoding tools also take `--codec h264|hevc|av1|prores` and `--quality N`. `h264` refuses an HDR source. ProRes needs `-o NAME.mov`.

Environment variables the scripts already read keep these names: `FFMPEG_SKILL_HW`, `FFMPEG_SKILL_TIMEOUT`, `FFMPEG_SKILL_MCP_FULL`, `FFMPEG_SKILL_ASR_ENGINE`, `FFMPEG_SKILL_ASR_MODEL`.
