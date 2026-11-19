"""Drawing primitives shared by both outputs.

A layout script creates one Canvas, draws boxes/texts/arrows in pixel coordinates (top-left origin, text y =
baseline) and then writes the PPTX slide and the HTML page from the same primitives.
"""
from xml.sax.saxutils import escape

from . import styles as S


class Canvas:
    """Collects drawing primitives ("rect", "text", "para", "arrow") for the PPTX and HTML backends.

    Attributes a layout script may set while drawing:
      off_y   vertical offset added to everything drawn next (move a whole section as a block)
      target  "both", "html" or "pptx": output(s) the next primitives appear in
    """

    def __init__(self, width, height, panel_title=19, styles=None):
        self.W, self.H = width, height
        self.panel_title = panel_title          # one size for all panel titles (largest that fits, see SKILL.md)
        self.styles = dict(S.STYLES, **(styles or {}))
        self.prims, self.targets = [], []
        self.off_y = 0
        self.target = "both"
        self._svg = []                          # light SVG preview of the PPTX layout

    # ---------------- font sizes ----------------
    def norm_size(self, size):
        """Four levels only: body 11.5, box title 12.5, panel title (self.panel_title); sizes >= 20 are kept."""
        if size == self.panel_title:
            return size
        return 11.5 if size < 12 else 12.5 if size < 13 else 15 if size < 20 else size

    # ---------------- primitives ----------------
    def _add(self, prim):
        self.prims.append(prim)
        self.targets.append(self.target)

    def text(self, x, y, s, size=11.5, bold=False, family=S.FONT, anchor="start", color="#202020", italic=False,
             exact=False):
        """exact=True keeps the size as given (e.g. a figure subtitle) instead of mapping it to a size level."""
        size = size if exact else self.norm_size(size)
        y = y + self.off_y
        self._add(("text", x, y, s, size, bold, family, color, italic))
        self._svg.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}"'
            f'{" font-weight=\"bold\"" if bold else ""}{" font-style=\"italic\"" if italic else ""}'
            f' fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')

    def para(self, x, y, w, h, s, size=11.5, bold=False, family=S.FONT, color="#202020", step=None):
        """Paragraph wrapped automatically to width w (HTML: foreignObject, PPTX: wrapping text box).

        y is the top of the box, h its height, step the line distance in px (default 1.3 * size); "
" forces a
        line break; no code links.
        """
        step = step or round(1.3 * size, 2)
        y = y + self.off_y
        self._add(("para", x, y, w, h, s, size, bold, family, color, step))
        self._svg.append(
            f'<foreignObject x="{x}" y="{y}" width="{w}" height="{h}"><div xmlns="http://www.w3.org/1999/xhtml" '
            f'style="font-family:{family};font-size:{size}px;line-height:{step}px;color:{color}'
            f'{";font-weight:bold" if bold else ""}">{escape(s).replace(chr(10), "<br/>")}</div></foreignObject>')

    def ctext(self, cx, y, s, size=10, **kw):
        """Text centred at cx (width estimated, since the PPTX backend has no text anchor)."""
        size = self.norm_size(size)
        self.text(round(cx - len(s) * size * 0.27, 1), y, s, size=size, **kw)

    def rect(self, x, y, w, h, style, dash=False, rx=4, sw=1.3):
        fill, stroke = self.styles[style] if style in self.styles else ("none", "#404040")
        y = y + self.off_y
        self._add(("rect", x, y, w, h, fill, stroke, dash, rx, sw))
        self._svg.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"'
            f' stroke-width="{sw}"{" stroke-dasharray=\"6,4\"" if dash else ""}/>')

    def box(self, x, y, w, h, style, title, lines=(), size=11.5, tsize=12.5, mono_title=False, step=16):
        """Outlined step box with an optional title line and body lines."""
        self.rect(x, y, w, h, style)
        yy = y + 18
        if title:
            self.text(x + 10, yy, title, size=tsize, bold=not mono_title, family=S.MONO if mono_title else S.FONT)
            yy += 16
        for ln in lines:
            self.text(x + 10, yy, ln, size=size)
            yy += step

    def tag(self, x, y, s, style):
        """Small rounded label (pill) with its top-left corner at x, y."""
        w = len(s) * 11.5 * 0.53 + 14
        self.rect(x, y, w, 17, style, rx=8, sw=1)
        self.text(x + 7, y + 13, s, size=11.5, bold=True, color=self.styles[style][1])

    def badge(self, cx, cy, n):
        """Step number of the coupling loop, centred at cx, cy."""
        self.rect(cx - 10, cy - 10, 20, 20, "badge", rx=10, sw=1)
        self.text(cx - 3.3, cy + 4.2, str(n), size=11.5, bold=True, color="#ffffff")

    def panel(self, x, y, w, h, title):
        """Container: tinted background without outline, title in the panel title size."""
        y = y + self.off_y
        fill = self.styles["panelbg"][0]
        self._svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="none"/>')
        self._add(("rect", x, y, w, h, fill, "none", False, 6, 0))
        self.text(x + 12, y + 27 - self.off_y, title, size=self.panel_title, bold=True)

    def arrow(self, pts, label=None, lx=None, ly=None, color=S.FLOW, dash=False, width=2.2):
        """Polyline with an arrowhead at the last point (control flow by default)."""
        pts = [(px, py + self.off_y) for px, py in pts]
        d = "M " + " L ".join(f"{px} {py}" for px, py in pts)
        self._add(("arrow", pts, color, dash, width))
        self._svg.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'
                         f'{" stroke-dasharray=\"7,4\"" if dash else ""} marker-end="url(#arr{color[1:]})"/>')
        if label:
            self.text(lx, ly, label, size=10.5, italic=True, color=color)

    def loop_arrow(self, pts, label=None, lx=None, ly=None, dash=False):
        """Coupling (data exchange) arrow: solid, coupling colour."""
        self.arrow(pts, label, lx, ly, color=S.LOOPC, dash=False, width=2.8)

    # ---------------- finishing ----------------
    def crop_top(self, dy):
        """Move everything up by dy and reduce the canvas height accordingly."""
        for k, pr in enumerate(self.prims):
            if pr[0] in ("text", "rect", "para"):
                self.prims[k] = pr[:2] + (pr[2] - dy,) + pr[3:]
            elif pr[0] == "arrow":
                self.prims[k] = (pr[0], [(px, py - dy) for px, py in pr[1]]) + pr[2:]
        self.H -= dy

    def prims_for(self, output):
        """Primitives of one output ("html" or "pptx")."""
        other = "pptx" if output == "html" else "html"
        return [pr for pr, t in zip(self.prims, self.targets) if t != other]

    def write_svg_preview(self, path):
        """Light SVG of everything drawn (both targets, before cropping) - only for a quick visual check."""
        head = (f'<svg xml:space="preserve" xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" '
                f'viewBox="0 0 {self.W} {self.H}"><defs>' + "".join(
                    f'<marker id="arr{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="11" markerHeight="11" '
                    f'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/>'
                    f'</marker>' for c in (S.FLOW, S.LOOPC)) + '</defs>'
                f'<rect x="0" y="0" width="{self.W}" height="{self.H}" fill="#ffffff"/>')
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join([head] + self._svg + ["</svg>"]))

    def write_pptx(self, path):
        from . import pptx
        pptx.write(path, self.prims_for("pptx"), self.W, self.H)

    def write_html(self, path, links, **kw):
        """kw: title, note_xy, author, author_email, hint_xy (see html.write)."""
        from . import html
        html.write(path, self.prims_for("html"), self.W, self.H, links, **kw)
