"""PPTX backend: drawing primitives as native, editable shapes on a one-slide PPTX (standard library only)."""
import zipfile
from xml.sax.saxutils import escape

EMU = 9525          # EMU per px (96 dpi)
NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def e(v):
    return int(round(v * EMU))


def col(c):
    return c.lstrip("#").upper()


def fill_xml(c):
    return "<a:noFill/>" if c == "none" else f'<a:solidFill><a:srgbClr val="{col(c)}"/></a:solidFill>'


def shapes_xml(prims):
    parts, sid = [], 3
    for pr in prims:
        sid += 1
        if pr[0] == "rect":
            _, x, y, w, h, fill, stroke, dash, rx, sw = pr
            adj = int(min(50000, rx / min(w, h) * 100000))
            parts.append(
                f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Box {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
                f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst></a:prstGeom>'
                f'{fill_xml(fill)}<a:ln w="{e(sw)}">{fill_xml(stroke)}'
                f'{"<a:prstDash val=\"dash\"/>" if dash else ""}</a:ln></p:spPr></p:sp>')
        elif pr[0] == "text":
            _, x, y, s, size, bold, family, color, italic = pr
            top = y - 0.92 * size                     # SVG y is the baseline
            w = max(10, len(s) * size * 0.6 + 6)
            h = size * 1.3
            parts.append(
                f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Text {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{e(x)}" y="{e(top)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
                f'<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr>'
                f'<a:lstStyle/><a:p><a:pPr algn="l"/><a:r><a:rPr lang="en-US" sz="{int(round(size * 75))}"'
                f' b="{1 if bold else 0}" i="{1 if italic else 0}" dirty="0">{fill_xml(color)}'
                f'<a:latin typeface="{family}"/><a:cs typeface="{family}"/></a:rPr>'
                f'<a:t>{escape(s)}</a:t></a:r></a:p></p:txBody></p:sp>')
        elif pr[0] == "para":     # wrapped by PowerPoint, exact line distance
            _, x, y, w, h, s, size, bold, family, color, step = pr
            rpr = (f'<a:rPr lang="en-US" sz="{int(round(size * 75))}" b="{1 if bold else 0}" dirty="0">{fill_xml(color)}'
                   f'<a:latin typeface="{family}"/><a:cs typeface="{family}"/></a:rPr>')
            runs = f'<a:br>{rpr}</a:br>'.join(f'<a:r>{rpr}<a:t>{escape(ln)}</a:t></a:r>' for ln in s.split("\n"))
            parts.append(
                f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Text {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
                f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
                f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr>'
                f'<a:lstStyle/><a:p><a:pPr algn="l"><a:lnSpc><a:spcPts val="{int(round(step * 75))}"/></a:lnSpc></a:pPr>'
                f'{runs}</a:p></p:txBody></p:sp>')
        elif pr[0] == "arrow":
            _, pts, color, dash, width = pr
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            x0, y0 = min(xs), min(ys)
            w, h = max(xs) - x0, max(ys) - y0
            path = "".join(
                f'<a:{"moveTo" if k == 0 else "lnTo"}><a:pt x="{e(px - x0)}" y="{e(py - y0)}"/></a:{"moveTo" if k == 0 else "lnTo"}>'
                for k, (px, py) in enumerate(pts))
            parts.append(
                f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Arrow {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{e(x0)}" y="{e(y0)}"/><a:ext cx="{max(1, e(w))}" cy="{max(1, e(h))}"/></a:xfrm>'
                f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
                f'<a:pathLst><a:path w="{max(1, e(w))}" h="{max(1, e(h))}" fill="none">{path}</a:path></a:pathLst></a:custGeom>'
                f'<a:noFill/><a:ln w="{e(width)}">{fill_xml(color)}{"<a:prstDash val=\"dash\"/>" if dash else ""}'
                f'<a:tailEnd type="triangle" w="med" len="med"/></a:ln></p:spPr></p:sp>')
    return "".join(parts)


def empty_tree():
    return ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
            '<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree>')


THEME = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Plain"><a:themeElements>
<a:clrScheme name="Plain"><a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
<a:dk2><a:srgbClr val="44546A"/></a:dk2><a:lt2><a:srgbClr val="E7E6E6"/></a:lt2>
<a:accent1><a:srgbClr val="4472C4"/></a:accent1><a:accent2><a:srgbClr val="ED7D31"/></a:accent2>
<a:accent3><a:srgbClr val="A5A5A5"/></a:accent3><a:accent4><a:srgbClr val="FFC000"/></a:accent4>
<a:accent5><a:srgbClr val="5B9BD5"/></a:accent5><a:accent6><a:srgbClr val="70AD47"/></a:accent6>
<a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Plain"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>
<a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
<a:fmtScheme name="Plain"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
<a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
<a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
<a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
<a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle>
<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
<a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'''


def write(path, prims, W, H):
    cx, cy = e(W), e(H)
    hdr = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    files = {
        "[Content_Types].xml": hdr +
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
            '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
            '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
            '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
            '</Types>',
        "_rels/.rels": hdr +
            f'<Relationships xmlns="{PKG}"><Relationship Id="rId1" Type="{REL}/officeDocument" Target="ppt/presentation.xml"/></Relationships>',
        "ppt/presentation.xml": hdr +
            f'<p:presentation {NS}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
            f'<p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst>'
            f'<p:sldSz cx="{cx}" cy="{cy}"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>',
        "ppt/_rels/presentation.xml.rels": hdr +
            f'<Relationships xmlns="{PKG}">'
            f'<Relationship Id="rId1" Type="{REL}/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
            f'<Relationship Id="rId2" Type="{REL}/slide" Target="slides/slide1.xml"/>'
            f'<Relationship Id="rId3" Type="{REL}/theme" Target="theme/theme1.xml"/></Relationships>',
        "ppt/slideMasters/slideMaster1.xml": hdr +
            f'<p:sldMaster {NS}><p:cSld>{empty_tree()}</p:cSld>'
            '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
            'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
            '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>',
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": hdr +
            f'<Relationships xmlns="{PKG}">'
            f'<Relationship Id="rId1" Type="{REL}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            f'<Relationship Id="rId2" Type="{REL}/theme" Target="../theme/theme1.xml"/></Relationships>',
        "ppt/slideLayouts/slideLayout1.xml": hdr +
            f'<p:sldLayout {NS} type="blank"><p:cSld name="Blank">{empty_tree()}</p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>',
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": hdr +
            f'<Relationships xmlns="{PKG}"><Relationship Id="rId1" Type="{REL}/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>',
        "ppt/slides/slide1.xml": hdr +
            f'<p:sld {NS}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            '<p:grpSp><p:nvGrpSpPr><p:cNvPr id="2" name="REMIND-MAgPIE coupling diagram"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            f'<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/><a:chOff x="0" y="0"/><a:chExt cx="{cx}" cy="{cy}"/></a:xfrm></p:grpSpPr>'
            f'{shapes_xml(prims)}</p:grpSp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>',
        "ppt/slides/_rels/slide1.xml.rels": hdr +
            f'<Relationships xmlns="{PKG}"><Relationship Id="rId1" Type="{REL}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>',
        "ppt/theme/theme1.xml": THEME,
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
