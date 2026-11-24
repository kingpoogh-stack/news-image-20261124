"""Entry point for the news-image-20261124 submission.

The front page is rendered ahead of time by tools/render_page.py and
committed at assets/final-page.png, so this entry point has one job:
put that page into the directory the competition reads its deliverable
from. It uses nothing outside the standard library, and the page is
copied byte for byte, so the printed edition is exactly the file that
was committed.
"""

import os
from pathlib import Path

ENTRY_NAME = "entry.png"
PAGE_FILE = Path(__file__).resolve().parent / "assets" / "final-page.png"


def deliver():
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    page_bytes = PAGE_FILE.read_bytes()
    (target_dir / ENTRY_NAME).write_bytes(page_bytes)
    print(f"delivered {ENTRY_NAME} ({len(page_bytes)} bytes)")


if __name__ == "__main__":
    deliver()
