#!/usr/bin/env python3
# Copyright (c) 2026 kajisho5
#
# Derived from https://github.com/kajisho5/ffmpeg-skill
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Reverse a video (and its audio, unless dropped).

Uses ffmpeg's `reverse` (video) and `areverse` (audio) filters, which decode
and buffer the whole clip in memory -- long inputs cost real time and RAM,
which is why there is no length limit baked in here: it is the caller's job
to keep this to clips it makes sense to reverse (a few seconds to a couple of
minutes), not a workaround this tool applies for you.

Examples:
  python3 reverse.py input.mp4
  python3 reverse.py input.mp4 --no-audio -o backwards.mp4
"""
import argparse
import sys

from _common import add_common, apply_common, aac_args, cfr_args, default_output, die, emit, ffmpeg_base, info, probe, run, video_args, X264_PRESETS, fmt_secs
from _common.emit import warn


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--output", help="output file (default: <name>_reverse.<ext>)")
    ap.add_argument("--no-audio", action="store_true", help="drop audio instead of reversing it")
    ap.set_defaults(crf=18)  # --quality's default (the --crf alias was removed in 2.0)
    ap.add_argument("--preset", default="medium", choices=X264_PRESETS, help="x264 preset")
    add_common(ap)
    args = ap.parse_args()
    apply_common(args)

    meta = probe(args.input)
    if not meta.get("video"):
        die("input has no video stream")
    has_audio = bool(meta.get("audio")) and not args.no_audio

    output = args.output or default_output(args.input, "reverse")
    if (meta.get("duration") or 0) > 60:
        warn(f"reverse buffers every decoded frame in memory; {meta['duration']:.0f}s of "
             f"{meta['video']['width']}x{meta['video']['height']} can exhaust RAM -- cut the part to reverse first (cut.py)",
             "memory_heavy", duration=meta["duration"])
    cmd = ffmpeg_base() + ["-i", args.input, "-vf", "reverse"]
    if has_audio:
        cmd += ["-af", "areverse"]
    cmd += video_args(meta, args.crf, args.preset)
    cmd += cfr_args(meta)
    if has_audio:
        cmd += aac_args()
    else:
        cmd += ["-an"]
    cmd.append(output)
    run(cmd)

    result = probe(output, role="output")
    info(f"wrote {output} ({fmt_secs(result['duration'])}, {result['video']['width']}x{result['video']['height']})")
    emit(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
