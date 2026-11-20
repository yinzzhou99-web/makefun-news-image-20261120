#!/usr/bin/env python3
"""Entry point for the news-image-20261120 make.fun entry.

The front page is drawn at build time by draw.py (Pillow) and the
result committed as preview.png. Grading runs in a bare sandbox
with no third-party packages available, so this program uses only
the standard library: it copies the committed preview.png into the
output directory as entry.png, byte for byte.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "preview.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, target)
    print("wrote %s (%d bytes)" % (target, os.path.getsize(target)))


if __name__ == "__main__":
    main()
