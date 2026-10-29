<!--
Copyright (c) 2026 kajisho5
Derived from https://github.com/kajisho5/ffmpeg-skill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-->

# ffmpeg listing fixtures

Captured or constructed stdout of `ffmpeg -hide_banner -filters / -encoders / -bsfs`, used by
`tests/test_contract.py` to prove that capability detection (`doctor`) reads every layout FFmpeg
has printed. CI uploads each runner's listings and `doctor --json` as the `ffmpeg-listings-<os>`
artifact; copy a new layout from there into this directory and add it to the test table.

| File | Origin |
|---|---|
| `ffmpeg_filters_6.1.txt`, `ffmpeg_encoders_6.1.txt`, `ffmpeg_bsfs_6.1.txt` | **captured** from FFmpeg 6.1.1 (Ubuntu 24.04 apt; same output as the ubuntu-latest CI runner) |
| `ffmpeg_filters_8.1.2_macos.txt`, `ffmpeg_encoders_8.1.2_macos.txt`, `ffmpeg_bsfs_8.1.2_macos.txt` | **captured** from FFmpeg 8.1.2 (Homebrew bottle, macos-latest CI runner). This build has no libfreetype / libass / libzimg, so `drawtext`, `subtitles`, `ass` and `zscale` are absent from the listing; the tests expect `doctor` to report exactly those as missing |
| `ffmpeg_filters_9.0.1_windows.txt`, `ffmpeg_encoders_9.0.1_windows.txt`, `ffmpeg_bsfs_9.0.1_windows.txt` | **captured** from FFmpeg 9.0.1 (gyan.dev essentials build, windows-latest CI runner, CRLF line endings kept as captured) |
| `ffmpeg_filters_7.1_constructed.txt` | **constructed**: the 6.1 capture unchanged, kept under its own name so the version matrix names FFmpeg 7 explicitly (7.x prints the 6.x layout: three flag characters `T.. .S. ..C`). Not a capture of an FFmpeg 7 binary. |
| `ffmpeg_filters_garbage.txt` | not a listing at all: must yield `unknown`, never `missing` |

What the FFmpeg 8.1.2 and 9.0.1 captures show (an earlier constructed 8.0 file had guessed a
different legend and was replaced by the capture): the legend still prints three-character keys
(`T.. = Timeline support`, `.S. = Slice threading`) while the rows carry two (` TS aap  AA->A`),
and a ` ------` separator line follows the legend. The parser keys on the io-spec token (`A->A`,
`AA->A`, `|->V`, `N->N`) and ignores the flag column and the legend.

The 7.1 file is the one remaining construction: it reproduces the 6.x row format with the 6.1
filter set and is not a capture of an FFmpeg 7 binary. Replace it with a capture when one is at
hand and keep the name so the tests keep working.

## mcp_tools.json

Not an ffmpeg listing: the frozen 1.x MCP/CLI surface (per tool, the argument names and which are required), read by `tests/test_contract.py`'s `test_mcp_tool_surface_matches_the_frozen_1x_snapshot`. Regenerate with `UPDATE_MCP_SNAPSHOT=1 python3 tests/test_contract.py` only for additions. Adding a tool or an optional argument is allowed once the snapshot is updated. Removing or renaming an argument is a breaking change.
