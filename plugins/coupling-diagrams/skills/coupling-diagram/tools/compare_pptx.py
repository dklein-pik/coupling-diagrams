"""Compare a hand-edited PPTX with a freshly generated reference, shape by shape.

Usage: python -I compare_pptx.py REFERENCE.pptx EDITED.pptx [TOLERANCE_PX]

Shapes are paired by content (type + text + colours + font size + bold + dash), then by the nearest position -
not by name or order, because PowerPoint renames and reorders shapes when the user groups/ungroups or copies them.
Prints: identical shapes, changed shapes (moved / resized / restyled / re-texted), removed and new shapes.
Coordinates in px (1 px = 9525 EMU), relative to the slide.
"""
import re
import sys
import zipfile

EMU = 9525


def shapes(path):
    z = zipfile.ZipFile(path)
    s = z.read("ppt/slides/slide1.xml").decode("utf-8")
    size = re.search(r'sldSz cx="(\d+)" cy="(\d+)"', z.read("ppt/presentation.xml").decode())
    out = []
    for m in re.finditer(r"<p:sp>.*?</p:sp>", s, re.S):
        sp = m.group(0)
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', sp)
        ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', sp)
        paras = ["".join(re.findall(r"<a:t>([^<]*)</a:t>", p)) for p in re.findall(r"<a:p>.*?</a:p>", sp, re.S)]
        out.append(dict(
            kind="text" if "txBox" in sp else ("arrow" if "tailEnd" in sp else "box"),
            txt=" | ".join(p for p in paras if p),
            off=tuple(round(int(v) / EMU, 1) for v in off.groups()),
            ext=tuple(round(int(v) / EMU, 1) for v in ext.groups()),
            cols=sorted(set(c.upper() for c in re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', sp))),
            sz=sorted(set(re.findall(r' sz="(\d+)"', sp))), bold='b="1"' in sp, dash="prstDash" in sp,
            pts=[(round(int(a) / EMU, 1), round(int(b) / EMU, 1)) for a, b in re.findall(r'<a:pt x="(-?\d+)" y="(-?\d+)"', sp)]))
    return out, tuple(round(int(v) / EMU) for v in size.groups())


def compare(ref_path, edit_path, tol=0.6):
    (a, sa), (b, sb) = shapes(ref_path), shapes(edit_path)
    same = lambda x, y: all(x[k] == y[k] for k in ("kind", "txt", "cols", "sz", "bold", "dash"))

    def geo(x, y):
        if any(abs(p - q) > tol for p, q in zip(x["off"], y["off"])):
            return False
        if x["kind"] != "text" and any(abs(p - q) > tol for p, q in zip(x["ext"], y["ext"])):
            return False
        if x["kind"] == "arrow" and (len(x["pts"]) != len(y["pts"]) or any(
                abs(p[0] - q[0]) > tol or abs(p[1] - q[1]) > tol for p, q in zip(x["pts"], y["pts"]))):
            return False
        return True

    rest_b, rest_a = list(b), []
    for x in a:
        m = next((y for y in rest_b if same(x, y) and geo(x, y)), None)
        if m:
            rest_b.remove(m)
        else:
            rest_a.append(x)
    print(f"slide size: reference {sa}, edited {sb}")
    print(f"shapes: reference {len(a)}, edited {len(b)}, identical {len(a) - len(rest_a)}")
    for x in list(rest_a):   # pair the rest by content, nearest position
        cand = [y for y in rest_b if x["kind"] == y["kind"] and x["txt"] == y["txt"] and (x["txt"] or x["cols"] == y["cols"])]
        if not cand:
            continue
        y = min(cand, key=lambda y: abs(y["off"][0] - x["off"][0]) + abs(y["off"][1] - x["off"][1]))
        rest_a.remove(x)
        rest_b.remove(y)
        d = {k: (x[k], y[k]) for k in ("off", "ext", "cols", "sz", "bold", "dash", "pts")
             if x[k] != y[k] and not (k == "ext" and x["kind"] == "text")}
        if x["off"] != y["off"]:
            d["moved by"] = (round(y["off"][0] - x["off"][0], 1), round(y["off"][1] - x["off"][1], 1))
        print(f"CHANGED {x['kind']} {x['txt'][:50]!r} @{x['off']}: {d}")
    for x in rest_a:
        print("REMOVED or unpaired (reference):", x)
    for y in rest_b:
        print("NEW or unpaired (edited):", y)


if __name__ == "__main__":
    compare(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.6)
