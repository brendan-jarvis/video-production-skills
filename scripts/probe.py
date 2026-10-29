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
"""Inspect a media file and print a compact JSON summary.

Reports duration, fps (and whether variable frame rate is suspected), resolution,
codecs, pixel format / color space, audio channels and sample rate.

Examples:
  python3 probe.py input.mp4
  python3 probe.py a.mp4 b.mov --compact
  python3 probe.py input.mp4 --field duration
"""
import argparse
import sys

from _common import add_common, analyze_levels, apply_common, print_json, probe


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="media file(s) to inspect")
    ap.add_argument("--compact", action="store_true", help="one human-readable line per file instead of JSON")
    ap.add_argument("--field", help="print only this top-level field (e.g. duration) or dotted path (video.fps)")
    ap.add_argument("--analyze", action="store_true", help="also sample picture levels (first 20 s) and flag Log-looking footage")
    add_common(ap)  # --json / --dry-run / --fast / --progress accepted for uniformity; output is JSON already
    args = ap.parse_args()
    apply_common(args)

    results = [probe(p) for p in args.inputs]
    if args.analyze:
        for r in results:
            if r.get("video"):
                r["levels"] = analyze_levels(r["file"])

    if args.field:
        for r in results:
            cur = r
            for key in args.field.split("."):
                cur = cur.get(key) if isinstance(cur, dict) else None
            print(cur if cur is not None else "")
        return 0

    if args.compact:
        for r in results:
            v, a = r.get("video") or {}, r.get("audio") or {}
            dur = r.get("duration")
            line = f"{r['file']}: {dur:.3f}s" if dur is not None else f"{r['file']}: ?s"
            if v:
                line += f" | {v.get('width')}x{v.get('height')} @ {v.get('fps')}fps {v.get('codec')} {v.get('pix_fmt')}"
                if v.get("variable_frame_rate_suspected"):
                    line += " (VFR?)"
                if v.get("bt2020_or_hdr"):  # hdr_format also names the BT.2020 SDR case
                    line += f" [{v.get('hdr_format')}]"
                if r.get("levels", {}).get("looks_like_log"):
                    line += " [Log?]"
            else:
                line += " | no video"
            if a:
                line += f" | audio {a.get('codec')} {a.get('channels')}ch {a.get('sample_rate')}Hz"
            else:
                line += " | no audio"
            print(line)
        return 0

    print_json(results[0] if len(results) == 1 else results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
