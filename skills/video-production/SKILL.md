---
name: video-production
description: >-
  Use when the user wants a video made or edited: a photo/video montage set to
  music (trip, event, race), or a directed piece from a brief (short film, music
  video, explainer, ad, promo, Short/Reel), from their own footage, generated
  shots, or both.
---

# Video production: montages and directed videos

One pipeline for two modes. Pick the mode first, then follow the shared steps. Use the `ffmpeg-tools`, `music-and-beats`, and `review-and-qc` skills when you reach cutting, music, or a review gate.

- **Montage:** the user's own photos, Live Photos and clips set to music. The default when they hand over media.
- **Directed:** a brief turned into a planned piece (short film, music video, explainer, ad, promo). It can use their footage, generated shots, or a mix. Generate only when the brief needs shots that do not exist, and say so before spending on generation.

Script paths such as `scripts/probe.py` are relative to the root of this repository. Run them from that directory.

## 0. Project folder and resume

Each video gets `videos/<slug>/` containing `brief.md`, `style.md`, `plan.tsv` (the shot list), `edit.json` (the cut list, the single source of truth for assembly), `NOTES.md`, `sources/`, `selects/`, `music/`, `style-refs/`, `shots/` (generated only), `renders/test/`, and `published/vN.mp4`.

- `NOTES.md` stays under 8 KB, with sections What this is, Decisions, Feedback, State and Next. Update it after every step, and on return resume from it without redoing finished work.
- Version every finished cut (v1, v2, ...) and never overwrite an earlier one.
- Back up selected sources, music and every published cut to durable storage the user already uses, as soon as they exist.
- Run heavy renders on the machine the user designates, with a script and a short test mode.

## 1. Brief

Ask only the questions that would change the result: purpose and audience, length, aspect ratio (16:9 for YouTube, 9:16 for Shorts/Reels), must-include or must-exclude people and shots, and vibe.

- **Directed mode:** pitch two or three one-line concepts and let the user pick one. Then write `script.md` (beats, any on-screen text or voiceover) and lock one style line for the look.
- Pick a format preset and record it in `style.md`:
  - **Race/event recap:** 60-90 s, fast cuts, energetic track.
  - **Trip:** 3-5 min, slower holds, sections by place or day.
  - **Short/Reel:** vertical, 25-45 s, hook in the first 2 s, captions in the safe area.
  - **Music video:** cut to the song's structure, with performance or B-roll.
  - **Explainer/promo:** script-led, titles or captions carry the message, music ducked under voice.
- `style.md` also holds motion rules (pan/zoom speed, hold times), Live Photo speed, transitions, title font and the grade. Use natural, ungraded colour unless a look is asked for. If there is a look, apply one consistent grade to every source so mixed cameras match.
- If `style-refs/` has example videos the user likes, study their pacing, transitions and titles and copy them.

## 2. Select or create shots

- **Montage:** build contact sheets (`scripts/look.py`), drop duplicates, weak or excluded shots, and show the selection before rendering. Convert HEIC to JPEG if the render machine cannot decode it.
- **Directed:** map each script beat to an existing clip or a shot to generate. For generated shots, draw a key frame first with the host's image tool, get a yes, then generate takes with the host's video tool. If the host cannot generate media, say so and use footage the user supplies. Review each take and keep the best. Reuse the locked style line and reference images so characters and look stay consistent.
- Before the first render, show a storyboard with one still per shot in order.

## 3. Music and sound

Follow the `music-and-beats` skill. Use only music the user has rights to. Mute clip audio by default. Duck music under dialogue or voiceover. Normalise to about -16 LUFS unless a platform preset names another target, and write credits (title, artist, licence, link).

## 4. Assemble and render

Follow the `ffmpeg-tools` skill. Build `edit.json` (source, in/out, duration, motion, transition, beat index), then assemble with the repository scripts. Make edits by changing `edit.json` and re-rendering, not by hand-editing a command.

- Use straight cuts unless the style calls for transitions.
- For a still with a zoom or pan, use `scripts/insert.py --zoom`. The default `--zoom-method smooth` keeps the move off whole-pixel steps. `--zoom-method zoompan` is faster and can jitter; check the contact sheet before keeping it. Do not hand-write a `zoompan` filter. Set fps explicitly on the input and the output (30).
- Live Photos: avoid frame-blending slow motion, which melts the picture. Play at native speed or slow down by repeating frames. Deshake only shaky clips (`scripts/stabilize.py`).
- Keep captions and titles inside the platform safe area (`references/gotchas.md#platform-safe-zones`).
- Encode the final file as HEVC when the destination allows it. If `hevc_nvenc` is available, constant quality around 19 is a reasonable choice. Otherwise use `scripts/export.py --preset h265` (CPU libx265) or the scripts' default H.264. CPU is the fallback whenever the GPU encoder is missing or fails.

## 5. Review gates

Follow the `review-and-qc` skill. Judge rendered frames, not intentions. Pause after the short test render so the user can check look and colour before the full render.

## 6. Deliver

- Deliver `published/vN.mp4`, a title and description with music credits, and a 1280x720 thumbnail (bold readable text, checked at small size, under 2 MB).
- Talk to the user in plain words, without file names, shot numbers or tool names.
- After a result the user is happy with, write what worked into the project's `style.md`, so the next video improves.
- Offer to clean up working files, keeping the published cuts and backups.
