---
name: review-and-qc
description: >-
  Use when checking a rendered cut before delivery: frames, jitter, beats,
  loudness, safe areas, and platform checks.
---

# Review and QC

Judge the rendered frames and the measured file. Do not sign off on what the edit was supposed to do.

Paths such as `scripts/check.py` are relative to the repository root.

## Gates

1. Render about 30 seconds that includes a still with movement, a clip, and a transition (`videos/<slug>/renders/test/`). Stop there. The user checks look and colour before the full render.
2. Pull consecutive frames around fast moves and transitions. Judge jitter from motion across those frames, not from a single still. `scripts/insert.py --zoom-method smooth` (the default) should not step on whole pixels. `--zoom-method zoompan` is faster and can: the picture holds, then jumps. If you see that, switch the still to `smooth` or keep `zoompan` only after the contact sheet looks steady.
3. List the three worst defects with timestamps. Fix only those sections. For a hard section, render two or three short variants and pick the best.
4. Check the sound. Cuts land on beats. Dialogue is clear and the music ducks under it. The ending resolves with the music. Loudness is about -16 LUFS when no platform is named, or the platform target (`scripts/loudness.py`, `scripts/check.py --platform NAME`). True peak is at or under -1 dBTP. Room tone was not boosted to a speech level.
5. Watch the full cut, then offer section-by-section refinement.

## What the scripts can check

`scripts/check.py OUTPUT --platform NAME` is the delivery check. Format rows (codec, pixel format, size, true peak, colour tags, variable frame rate) are safe to fix. Judgement rows (duration, aspect, frame rate, loudness) change the content. Fix those only when the request implies the answer. Otherwise state the choice and its cost. Mention warnings. Do not chase them.

`scripts/look.py OUTPUT --tiles 3x2` is how you see the picture. Add `--safe tiktok` (or `reels`, `shorts`, `youtube`) to shade the area the app covers. Captions and titles stay inside that area. A file can pass every `check.py` row and still hide the words under the buttons. Fractions: `references/gotchas.md#platform-safe-zones`.

When the picture changed, name the contact sheet you actually looked at. If you cannot view images, say the pixels were not inspected. Do not claim you saw the frame.

## Colour

Mixed cameras need one grade, or no grade. iPhone HDR that was flattened into BT.709 looks wrong next to a phone SDR clip. The `ffmpeg-tools` skill has the HDR rules. If the test render's colour is off, fix it before the full render.

## Deliver

The published file is `published/vN.mp4`. Do not overwrite an earlier version. With it: a title, a description that credits the music (title, artist, licence, link), and a 1280x720 thumbnail with bold text that is still readable small, under 2 MB.
