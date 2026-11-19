"""Render an HTML page or SVG to PNG with a headless browser, for visual checks.

Usage: python -I render.py INPUT.html|INPUT.svg OUTPUT.png WIDTH HEIGHT
(For the HTML page add ~20 px to width/height for the page padding.)
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import file_url, find_browser   # noqa: E402


def render(src, png, width, height):
    cmd = [find_browser(), "--headless", "--disable-gpu", "--hide-scrollbars",
           f"--window-size={width},{height}", f"--screenshot={os.path.abspath(png)}", file_url(src)]
    subprocess.run(cmd, check=True, capture_output=True)
    if not os.path.exists(png):
        raise RuntimeError("browser did not write the screenshot")
    return png


if __name__ == "__main__":
    src, png, w, h = sys.argv[1:5]
    print(render(src, png, int(w), int(h)))
