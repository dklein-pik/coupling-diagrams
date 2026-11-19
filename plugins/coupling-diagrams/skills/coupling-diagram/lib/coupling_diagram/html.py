"""HTML backend: drawing primitives as a self-contained dark-theme page with code links and excerpts on hover.

Every text line is scanned for the link patterns of a LinkTable. A match becomes a link to the call site (or to the
code if no call site is given); if a call site exists, a "↪" marker after it links to the definition. Hovering shows
the referenced lines with CONTEXT lines around them, read via `git show` from the local clones at the pinned commits.
The build fails if a referenced file or line range does not exist and warns about patterns that match nothing.
"""
import datetime
import json
from html import escape

from . import styles as S

MAX_EXCERPT = 40   # max. number of linked lines shown
CONTEXT = 5        # context lines shown above and below the linked lines


def dark(c):
    return S.DARK.get(c.lower(), c) if c != "none" else "none"


def ref_info(table, ref, role):
    repo, path, a, b = ref
    r = table.repos[repo]
    lines = r.lines(path)                 # also verifies that the file exists at the commit
    plain = "?plain=1" if path.endswith((".csv", ".md")) else ""
    url = f'{r.url}/blob/{r.commit}/{path}{plain}'
    if a:
        if b > len(lines):
            raise ValueError(f"{repo}:{path} has only {len(lines)} lines, link asks for {b}")
        url += f"#L{a}" + (f"-L{b}" if b != a else "")
        last = min(b, a + MAX_EXCERPT - 1)                 # linked lines shown (highlighted)
        lo = max(1, a - CONTEXT)
        hi = min(len(lines), last + CONTEXT) if last == b else last
        excerpt = [[n, lines[n - 1], a <= n <= b] for n in range(lo, hi + 1)]
        more = b - last
        span = f"L{a}" + (f"-{b}" if b != a else "")
    else:
        excerpt, more, span = [], 0, "whole file"
    return dict(url=url, role=role, repo=repo, path=path, span=span,
                commit=r.commit[:9], excerpt=excerpt, more=more)


def is_word(ch):
    return ch.isalnum() or ch == "_"


def find_matches(links, s, y):
    """Return non-overlapping (start, end, spec) for one text line; earlier link entries win."""
    taken, found = [False] * len(s), []
    for spec in links:
        pat, _, _, cond = spec
        if cond and ("y" in cond and cond["y"] != y or "ctx" in cond and cond["ctx"] not in s):
            continue
        i = s.find(pat)
        while i >= 0:
            j = i + len(pat)
            ok_left = i == 0 or not (is_word(s[i - 1]) and is_word(pat[0]))
            ok_right = j == len(s) or not (is_word(s[j]) and is_word(pat[-1]))
            if ok_left and ok_right and not any(taken[i:j]):
                for k in range(i, j):
                    taken[k] = True
                found.append((i, j, spec))
            i = s.find(pat, i + 1)
    return sorted(found, key=lambda m: m[0])


def write(path, prims, W, H, table, title="Coupling diagram", note_xy=None, author=None, author_email=None,
          hint_xy=None):
    """Write the page. note_xy: right-aligned "Created by <author> <date>" line; hint_xy: two-line link legend."""
    refs, svg = [], []

    def add_ref(ref, role):
        refs.append(ref_info(table, ref, role))
        return len(refs) - 1

    used, markers = set(), set()
    for pr in prims:
        if pr[0] == "rect":
            _, x, y, w, h, fill, stroke, dash, rx, sw = pr
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{dark(fill)}" '
                       f'stroke="{dark(stroke)}" stroke-width="{sw}"{" stroke-dasharray=\"6,4\"" if dash else ""}/>')
        elif pr[0] == "arrow":
            _, pts, color, dash, width = pr
            d = "M " + " L ".join(f"{px} {py}" for px, py in pts)
            markers.add(dark(color))
            svg.append(f'<path d="{d}" fill="none" stroke="{dark(color)}" stroke-width="{width}"'
                       f'{" stroke-dasharray=\"7,4\"" if dash else ""} marker-end="url(#arr{dark(color)[1:]})"/>')
        elif pr[0] == "text":
            _, x, y, s, size, bold, family, color, italic = pr
            for old, new in table.relabel.items():
                s = s.replace(old, new)
            attrs = (f'x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{dark(color)}"'
                     f'{" font-weight=\"bold\"" if bold else ""}{" font-style=\"italic\"" if italic else ""}')
            parts, pos = [], 0
            for i, j, spec in find_matches(table.links, s, y):
                used.add(id(spec))
                parts.append(escape(s[pos:i]))
                # name -> call site (or code if there is no separate call site), marker -> definition
                k = add_ref(spec[2], "call site") if spec[2] else add_ref(spec[1], "code")
                parts.append(f'<a class="lk" href="{escape(refs[k]["url"])}" target="_blank" data-ref="{k}">'
                             f'<tspan>{escape(s[i:j])}</tspan></a>')
                if spec[2]:
                    c = add_ref(spec[1], "definition")
                    parts.append(f'<a class="call" href="{escape(refs[c]["url"])}" target="_blank" data-ref="{c}">'
                                 f'<tspan dx="2">↪</tspan></a>')
                pos = j
            parts.append(escape(s[pos:]))
            svg.append(f'<text {attrs} xml:space="preserve">{"".join(parts)}</text>')

    unused = [spec[0] for spec in table.links if id(spec) not in used]
    if unused:
        print("WARNING: link patterns not found in diagram:", unused)

    if hint_xy:     # two-line legend of the link types
        hx, hy = hint_xy
        svg.append(f'<text x="{hx}" y="{hy}" font-family="Arial" font-size="11.5" fill="#e4e6ea">'
                   f'<tspan fill="#7fc1ff">linked name</tspan>: call site or code</text>')
        svg.append(f'<text x="{hx}" y="{hy + 17}" font-family="Arial" font-size="11.5" fill="#e4e6ea">'
                   f'<tspan fill="#ffb86b">↪</tspan>: definition   (hover: code excerpt)</text>')

    if author:      # author note (date of generation), right-aligned at note_xy
        nx, ny = note_xy if note_xy else (W - 20, H - 12)
        name = (f'<a class="mail" href="mailto:{escape(author_email)}"><tspan>{escape(author)}</tspan></a>'
                if author_email else escape(author))
        svg.append(f'<text x="{nx}" y="{ny}" font-family="Arial" font-size="11.5" fill="#8a919b" text-anchor="end">'
                   f'Created by {name} {datetime.date.today().isoformat()}</text>')

    marker_defs = "".join(
        f'<marker id="arr{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="11" markerHeight="11" '
        f'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>'
        for c in sorted(markers))

    page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{escape(title)}</title>
<style>
  html, body {{ margin: 0; background: {S.DARK_BG}; color: #e4e6ea; font-family: Arial, sans-serif; }}
  #wrap {{ max-width: {W}px; margin: 0 auto; padding: 10px; }}
  svg {{ width: 100%; height: auto; display: block; }}
  a.lk tspan {{ fill: #7fc1ff; }}
  a.lk:hover tspan {{ text-decoration: underline; fill: #b5dcff; }}
  a.mail tspan {{ fill: #7fc1ff; }}
  a.mail:hover tspan {{ text-decoration: underline; fill: #b5dcff; }}
  a.call tspan {{ fill: #ffb86b; font-weight: bold; }}
  a.call:hover tspan {{ fill: #ffd7a8; }}
  #tip {{ position: fixed; display: none; z-index: 10; max-width: 760px; background: #1b1e24;
         border: 1px solid #4a505a; border-radius: 6px; box-shadow: 0 6px 24px rgba(0,0,0,.6);
         font-size: 12px; pointer-events: none; }}
  #tip .hd {{ padding: 6px 10px; border-bottom: 1px solid #333842; color: #aab2bd; }}
  #tip .hd b {{ color: #e4e6ea; }}
  #tip .role {{ color: #ffb86b; }}
  #tip pre {{ margin: 0; padding: 6px 0; font-family: Consolas, "Courier New", monospace;
             font-size: 11.5px; color: #d6dae0; white-space: pre; overflow: hidden; }}
  #tip .ln {{ color: #5f6773; display: inline-block; min-width: 3.2em; }}
  #tip .row {{ display: block; padding: 0 10px; color: #8f969f; }}
  #tip .row.hl {{ background: #3a3420; color: #f1f3f5; box-shadow: inset 3px 0 0 #ffb86b; }}
  #tip .row.hl .ln {{ color: #ffb86b; }}
  #tip .more {{ padding: 0 10px 6px; color: #8a919b; font-style: italic; }}
</style></head>
<body><div id="wrap">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">
<defs>{marker_defs}</defs>
<rect x="0" y="0" width="{W}" height="{H}" fill="{S.DARK_BG}"/>
{chr(10).join(svg)}
</svg></div>
<div id="tip"></div>
<script>
const REFS = {json.dumps(refs, ensure_ascii=False).replace("</", "<\\/")};
const tip = document.getElementById("tip");
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
// fit the figure to the window in fixed px, so that browser zoom enlarges it; refit only on real
// window resizes (zoom changes devicePixelRatio, a resize does not)
const wrap = document.getElementById("wrap");
let dpr = devicePixelRatio;
const fit = () => wrap.style.width = Math.min({W}, document.documentElement.clientWidth - 20) + "px";
fit();
addEventListener("resize", () => {{ if (devicePixelRatio === dpr) fit(); dpr = devicePixelRatio; }});
function show(ev) {{
  const r = REFS[+ev.currentTarget.dataset.ref];
  let h = `<div class="hd"><span class="role">${{r.role}}</span> &middot; <b>${{esc(r.repo + "/" + r.path)}}</b> ${{r.span}} &middot; @ ${{r.commit}}</div>`;
  if (r.excerpt.length) {{
    h += "<pre>" + r.excerpt.map(([n, t, hl]) =>
      `<span class="${{hl ? "row hl" : "row"}}"><span class="ln">${{n}}</span>${{esc(t)}}</span>`).join("") + "</pre>";
    if (r.more > 0) h += `<div class="more">&hellip; ${{r.more}} more lines (click to open)</div>`;
  }} else h += `<div class="more">click to open the file</div>`;
  tip.innerHTML = h; tip.style.display = "block"; move(ev);
}}
function move(ev) {{
  const pad = 14, w = tip.offsetWidth, hgt = tip.offsetHeight;
  let x = ev.clientX + pad, y = ev.clientY + pad;
  if (x + w > innerWidth) x = Math.max(4, ev.clientX - w - pad);
  if (y + hgt > innerHeight) y = Math.max(4, ev.clientY - hgt - pad);
  tip.style.left = x + "px"; tip.style.top = y + "px";
}}
document.querySelectorAll("a.lk, a.call").forEach(a => {{
  a.addEventListener("mouseenter", show);
  a.addEventListener("mousemove", move);
  a.addEventListener("mouseleave", () => tip.style.display = "none");
}});
</script>
</body></html>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"{len(refs)} links written")
