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
"""End-to-end tests: build synthetic footage, run every script, verify with probe.

    python3 tests/test_all.py

The cases live one module per tool group, plus test_skills.py for this
repository's skill files. Each group module is also runnable on its own.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_accel  # noqa: E402
import test_analysis  # noqa: E402
import test_asr  # noqa: E402
import test_skills  # noqa: E402
import test_audio  # noqa: E402
import test_cut_copy  # noqa: E402
import test_delivery  # noqa: E402
import test_editing  # noqa: E402
import test_orchestration  # noqa: E402
import test_picture  # noqa: E402

MODULES = (test_analysis, test_editing, test_cut_copy, test_audio, test_picture, test_delivery, test_orchestration, test_accel,
           test_asr, test_skills)


def load_tests(loader, tests, pattern):
    """unittest calls this instead of scanning this module: the cases are in the nine group
    modules, and naming them here keeps the set (and the order groups run in) explicit."""
    suite = unittest.TestSuite()
    for module in MODULES:
        suite.addTests(loader.loadTestsFromModule(module))
    return suite


if __name__ == "__main__":
    unittest.main(verbosity=2)
