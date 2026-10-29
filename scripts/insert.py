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
"""Turn a still image into a silent, timed video clip.

Produces a fixed-duration, constant-frame-rate video from one image -- for
example a title card, an end slate, or a placeholder to slot into join.py
alongside real footage. The output has no audio track: pair it with audio.py
or export.py's own audio handling if the surrounding edit needs sound under
the still.

--width/--height set the output frame size the same way fit.py does: give
one and the other follows the image's own aspect; give both for an exact
frame (the image is scaled to fill it, centre-cropping any excess -- never
distorted). Omit both to keep the image's native size (evened for 4:2:0).

--zoom in|out applies a Ken Burns effect: a slow, linear zoom across the
clip's duration (--zoom-amount sets the end/start zoom factor, default 1.3 =
30% zoomed in by the end). --pan left|right|up|down drifts the visible
window across the image while zoomed (it needs --zoom -- panning uses the
extra image area a zoom exposes).

--zoom-method smooth|zoompan chooses how that move is sampled. smooth
(the default) scales an oversampled canvas with eval=frame and places it
with a per-frame offset, so a slow zoom or pan does not step on whole
output pixels. zoompan is the older filter: faster, and it rounds the
window to integer pixels, which can wobble. Check a contact sheet or
consecutive frames if you use it.

Examples:
  python3 insert.py title.png --duration 3
  python3 insert.py slate.jpg --duration 5 --width 1920 --height 1080 --fps 30 -o slate.mp4
  python3 insert.py photo.jpg --duration 6 --zoom in --pan right --width 1920 --height 1080
  python3 insert.py photo.jpg --duration 6 --zoom in --zoom-method zoompan
"""
import argparse
import math
import sys

from _common import add_common, apply_common, default_output, die, emit, ffmpeg_base, info, parse_time, probe, run, video_args, X264_PRESETS, time_arg, fmt_secs


def even(n: float) -> int:
    v = int(round(n))
    return v if v % 2 == 0 else v + 1


# Output pixels of headroom for --zoom-method smooth. A one-pixel step on this
# canvas is 1/SMOOTH_OVERSAMPLE of an output pixel after the final scale down.
SMOOTH_OVERSAMPLE = 4


def _ken_burns_z(zoom: str, amount: float, frames: int) -> str:
    """FFmpeg expression for the zoom factor on frame n. Frame 0 is the start."""
    step = (amount - 1) / frames
    if zoom == "in":
        return f"min(1+n*{step:.8f},{amount:.8f})"
    return f"max({amount:.8f}-n*{step:.8f},1)"


def _smooth_offset(base: int, z: str, frames: int, pan: str, toward_end: str, toward_start: str) -> str:
    """Top-left of the oversampled window. toward_end reveals that side by the last frame."""
    span = f"{base}*(1-({z}))"
    if pan == toward_end:
        return f"({span})*n/{frames}"
    if pan == toward_start:
        return f"({span})*(1-n/{frames})"
    return f"({span})/2"


def _smooth_graph(out_w: int, out_h: int, fps: float, zoom: str, amount: float, frames: int, pan: str) -> str:
    z = _ken_burns_z(zoom, amount, frames)
    base_w, base_h = out_w * SMOOTH_OVERSAMPLE, out_h * SMOOTH_OVERSAMPLE
    x = _smooth_offset(base_w, z, frames, pan, "right", "left")
    y = _smooth_offset(base_h, z, frames, pan, "down", "up")
    rate = f"{fps:.8g}"
    return (
        f"[0:v]scale={base_w}:{base_h}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={base_w}:{base_h},"
        f"scale=w='trunc(iw*({z})/2)*2':h='trunc(ih*({z})/2)*2':eval=frame:flags=lanczos[zoomed];"
        f"color=c=black:s={base_w}x{base_h}:r={rate}[canvas];"
        f"[canvas][zoomed]overlay=x='{x}':y='{y}':eval=frame:format=auto,"
        f"scale={out_w}:{out_h}:flags=lanczos,setsar=1,fps={rate}[v]"
    )


def _zoompan_filters(out_w: int, out_h: int, fps: float, zoom: str, amount: float, frames: int, pan: str) -> list:
    if zoom == "in":
        zexpr = f"if(eq(on,0),1,min(zoom+{(amount - 1) / frames:.8f},{amount:g}))"
    else:
        zexpr = f"if(eq(on,0),{amount:g},max(zoom-{(amount - 1) / frames:.8f},1))"
    pan_x = {
        "left": f"(iw-iw/zoom)*(1-on/{frames})",
        "right": f"(iw-iw/zoom)*on/{frames}",
    }.get(pan, "iw/2-(iw/zoom/2)")
    pan_y = {
        "up": f"(ih-ih/zoom)*(1-on/{frames})",
        "down": f"(ih-ih/zoom)*on/{frames}",
    }.get(pan, "ih/2-(ih/zoom/2)")
    # zoompan samples integer pixels. Scale up first so a zoomed-in crop still
    # has real pixels, which is the behaviour this method keeps.
    upscale = max(2, math.ceil(amount * 2))
    return [
        f"scale={out_w * upscale}:{out_h * upscale}:force_original_aspect_ratio=increase",
        f"crop={out_w * upscale}:{out_h * upscale}",
        f"zoompan=z='{zexpr}':x='{pan_x}':y='{pan_y}':d={frames}:s={out_w}x{out_h}:fps={fps:g}",
        "setsar=1",
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="still image (PNG/JPG/...)")
    ap.add_argument("-o", "--output", help="output file (default: <name>_insert.mp4)")
    ap.add_argument("--duration", required=True, help="clip duration (seconds or mm:ss)")
    ap.add_argument("--width", type=int, help="output width in px; with --height also given, both are used directly")
    ap.add_argument("--height", type=int, help="output height in px; with --width also given, both are used directly")
    ap.add_argument("--fps", type=float, default=30.0, help="output frame rate (default 30)")
    ap.add_argument("--zoom", choices=["in", "out"], help="Ken Burns: slow linear zoom in or out across the clip")
    ap.add_argument("--zoom-amount", type=float, default=1.3, help="end (zoom in) or start (zoom out) zoom factor, > 1.0 (default 1.3)")
    ap.add_argument("--zoom-method", choices=["smooth", "zoompan"], default="smooth",
                    help="smooth (default): sub-pixel scale and per-frame placement, no whole-pixel wobble. "
                         "zoompan: the older integer-pixel filter, faster, can jitter")
    ap.add_argument("--pan", choices=["left", "right", "up", "down"], help="drift the visible window this direction while zoomed (needs --zoom)")
    ap.set_defaults(crf=18)  # --quality's default (the --crf alias was removed in 2.0)
    ap.add_argument("--preset", default="medium", choices=X264_PRESETS, help="x264 preset")
    add_common(ap)
    args = ap.parse_args()
    apply_common(args)

    target = time_arg(args.duration, "--duration", args.fps)
    if target <= 0:
        die("--duration must be > 0")
    if args.fps <= 0:
        die("--fps must be > 0")
    if args.zoom_amount <= 1.0:
        die(f"--zoom-amount must be > 1.0, got {args.zoom_amount}")
    if args.pan and not args.zoom:
        die("--pan needs --zoom in|out")

    meta = probe(args.input)
    if not meta.get("video"):
        die("input has no image/video stream")
    if (meta.get("duration") or 0) > 0.5 or meta.get("audio"):
        die(f"{args.input} is a video, not a still image; insert.py animates a still (Ken Burns). "
            f"For a clip use broll.py (cutaway) or cut.py/join.py")
    sw, sh = meta["video"]["width"], meta["video"]["height"]
    ratio = sw / sh

    if args.width and args.height:
        out_w, out_h = even(args.width), even(args.height)
    elif args.width:
        out_w = even(args.width)
        out_h = even(out_w / ratio)
    elif args.height:
        out_h = even(args.height)
        out_w = even(out_h * ratio)
    else:
        out_w, out_h = even(sw), even(sh)

    frames = max(1, round(target * args.fps))
    output = args.output or default_output(args.input, "insert", "mp4")
    cmd = ffmpeg_base() + ["-loop", "1", "-i", args.input, "-t", f"{target:.3f}"]
    if args.zoom and args.zoom_method == "smooth":
        cmd += ["-filter_complex", _smooth_graph(out_w, out_h, args.fps, args.zoom, args.zoom_amount, frames, args.pan),
                "-map", "[v]"]
    elif args.zoom:
        vf = _zoompan_filters(out_w, out_h, args.fps, args.zoom, args.zoom_amount, frames, args.pan)
        cmd += ["-vf", ",".join(vf)]
    else:
        vf = [
            f"scale={out_w}:{out_h}:force_original_aspect_ratio=increase",
            f"crop={out_w}:{out_h}",
            "setsar=1",
            f"fps={args.fps:g}",
        ]
        cmd += ["-vf", ",".join(vf)]
    # the SDR line, whatever the image is; its RGB (PNG) or BT.601 (JPEG) pixels are converted to
    # the BT.709 that line is tagged with
    cmd += video_args(None, args.crf, args.preset, source=meta)
    cmd += ["-an", output]
    run(cmd)

    result = probe(output, role="output")
    v = result["video"]
    info(f"wrote {output} ({fmt_secs(result['duration'])}, {v['width']}x{v['height']}, {v['fps']:g}fps)")
    emit(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
