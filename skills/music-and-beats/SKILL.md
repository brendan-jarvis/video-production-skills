---
name: music-and-beats
description: >-
  Use when choosing music, mapping a song's structure, detecting beats, or
  ducking music under voice for a montage or directed video.
---

# Music and beats

Use only music the user has rights to. Default to CC0 or CC BY tracks, for example the Openverse API (`https://api.openverse.org/v1/audio/?license=cc0,by`). Do not use copyrighted music for YouTube. Content ID does not care that the edit was a personal montage.

Write the credit next to the cut: title, artist, licence, and a link.

## Structure before cuts

Map the song (intro, build, drop, outro) and say where those sections sit in seconds. Put the strongest shots on the big moments. Change sections on downbeats. Cut on beats.

`edit.json` in the video project records each shot's beat index. The `video-production` skill owns that file. Change the music edit by changing `edit.json` and re-rendering.

## Finding the beats

Prefer librosa or aubio. Both are optional. If neither is installed, say so. You can still cut to a structure you can hear, or ask for one of those libraries. Do not invent a confident BPM from a guess.

Check the grid is not on the off-beat. Compare energy under 120 Hz (the kick) on the detected beats with the energy halfway between them. If the off-beat is stronger, shift the grid.

The scripts can measure a grid too:

```
python3 scripts/scenes.py TRACK --beats --json
python3 scripts/cut.py INPUT --segments ... --snap beats --snap-source beats.json
```

`--snap beats` moves a cut onto the nearest beat inside the tolerance. Read the confidence. If it is low, say so and do not pretend the cuts landed on the music.

Paths are relative to the repository root.

## Mix

Mute the clip audio by default. A race or a crowd can keep a little of it when the user wants the place to be heard. Dialogue and voiceover stay clear.

Duck the music under speech with `scripts/audio.py`:

```
python3 scripts/audio.py INPUT --music BED --duck --fade-out 3
```

`--duck-amount`, `--duck-threshold`, `--duck-attack` and `--duck-release` change how hard and how fast the music dips. An effects stem (`--effects`) is not ducked.

Normalise the finished mix with `scripts/loudness.py`. About -16 LUFS is the default for a montage when no platform is named. Platform presets are often -14 LUFS for social video, -16 for a podcast, -23 for broadcast, with true peak at or under -1 dBTP (`scripts/check.py --platform NAME`, `templates/`). Do not lift room tone or near-silence up to a speech target. Detail: `references/gotchas.md#loudness-and-ambience`.

The ending should resolve with the music. Do not cut the song off in the middle of a phrase unless the style is a hard stop and the user asked for it.
