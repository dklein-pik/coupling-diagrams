"""Measure real text widths in the browser (Arial) and compute line breaks; estimates are not reliable enough.

Usage:
  python -I measure.py width  SIZE BOLD "text 1" ["text 2" ...]      -> width in px of each text
  python -I measure.py wrap   SIZE BOLD WIDTH "paragraph"            -> JSON list of lines (greedy, word-wise)
  python -I measure.py fit    BOLD AVAILABLE "text 1" ["text 2" ...] -> largest font size at which every text fits
BOLD is 0 or 1. Prints JSON. Temporary files go to a "_measure" folder next to the current working directory.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser import file_url, find_browser   # noqa: E402

PAGE = """<!DOCTYPE html><html><body><svg id="s" width="4000" height="200"></svg><pre id="out"></pre><script>
const job = %s;
const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
t.setAttribute("font-family", "Arial"); t.setAttribute("y", "100"); document.getElementById("s").appendChild(t);
const width = (str, size, bold) => { t.setAttribute("font-size", size); t.setAttribute("font-weight", bold ? "bold" : "normal");
  t.textContent = str; return t.getComputedTextLength(); };
let res;
if (job.mode === "width") res = job.texts.map(s => width(s, job.size, job.bold));
else if (job.mode === "fit") res = Math.min(...job.texts.map(s => job.avail / width(s, 1000, job.bold) * 1000));
else { res = []; let cur = "";
  for (const w of job.texts[0].split(" ")) { const c = cur ? cur + " " + w : w;
    if (cur && width(c, job.size, job.bold) > job.avail) { res.push(cur); cur = w; } else cur = c; }
  res.push(cur); }
document.getElementById("out").textContent = JSON.stringify(res);
</script></body></html>"""


def run(job):
    tmp = os.path.join(os.getcwd(), "_measure")
    os.makedirs(tmp, exist_ok=True)
    page = os.path.join(tmp, "measure.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(PAGE % json.dumps(job))
    dom = subprocess.run([find_browser(), "--headless", "--disable-gpu", "--dump-dom", file_url(page)],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    os.remove(page)
    os.rmdir(tmp)
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    return json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "width":
        job = dict(mode=mode, size=float(sys.argv[2]), bold=sys.argv[3] == "1", texts=sys.argv[4:])
    elif mode == "wrap":
        job = dict(mode=mode, size=float(sys.argv[2]), bold=sys.argv[3] == "1", avail=float(sys.argv[4]),
                   texts=[sys.argv[5]])
    elif mode == "fit":
        job = dict(mode=mode, bold=sys.argv[2] == "1", avail=float(sys.argv[3]), texts=sys.argv[4:])
    else:
        sys.exit(__doc__)
    print(json.dumps(run(job), ensure_ascii=False, indent=1))
