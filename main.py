"""Entry point for the news-image-20261124 submission.

The front page itself is drawn ahead of time by tools/render_page.py
and committed to this repository as assets/final-page.png. All this
program does is place a copy of that image at entry.png in the
output directory — the directory named by the MAKEFUN_OUTPUT_DIR
environment variable when it is set, and /output otherwise.

Nothing beyond the Python standard library is used, so the program
runs unchanged in the grading sandbox with no network. Because it
only ever copies the same committed bytes, the two grading runs
produce byte-identical output, from any working directory.
"""

import os
import shutil
from pathlib import Path


def deliver() -> Path:
    here = Path(__file__).resolve().parent
    source = here / "assets" / "final-page.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    return target


if __name__ == "__main__":
    deliver()
