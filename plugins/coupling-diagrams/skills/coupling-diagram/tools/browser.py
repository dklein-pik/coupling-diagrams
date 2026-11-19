"""Locate a Chromium-based browser (Edge or Chrome) for headless rendering and text measurement."""
import os
import shutil

CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
NAMES = ["msedge", "microsoft-edge", "google-chrome", "chromium", "chromium-browser", "chrome"]


def find_browser():
    """Path of the browser: env var COUPLING_DIAGRAM_BROWSER, known install paths, or PATH."""
    env = os.environ.get("COUPLING_DIAGRAM_BROWSER")
    if env and os.path.exists(env):
        return env
    for p in CANDIDATES:
        if os.path.exists(p):
            return p
    for n in NAMES:
        p = shutil.which(n)
        if p:
            return p
    raise RuntimeError("no Edge/Chrome found; set COUPLING_DIAGRAM_BROWSER to the browser executable")


def file_url(path):
    p = os.path.abspath(path).replace("\\", "/")
    return "file:///" + p.lstrip("/").replace(" ", "%20")
