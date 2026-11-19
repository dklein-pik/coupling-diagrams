---
name: coupling-diagram
description: Create or revise a code-linked structure diagram of a REMIND model coupling or data flow (e.g. REMIND-MAgPIE, other soft-links) as an editable PowerPoint slide plus an interactive dark HTML page whose code elements link to pinned source lines on GitHub with hover excerpts. Use when the user asks for a diagram/figure/flowchart of how models are coupled, which scripts call each other, or which files are exchanged, or wants to update such a diagram or port hand edits from the PPTX.
---

# Coupling diagrams (REMIND and partner models)

One Python layout script draws the diagram once; the library writes **both** outputs from the same primitives:
- `*.pptx`: native, editable PowerPoint shapes (light colours), one slide, one group.
- `*.html`: self-contained dark page; code names link to GitHub at pinned commits, hover shows the code excerpt.

Library, tools and a complete worked example live next to this file:
- `${CLAUDE_SKILL_DIR}/lib/coupling_diagram/` (Canvas, LinkTable, Repo, backends, styles)
- `${CLAUDE_SKILL_DIR}/tools/` (`measure.py`, `render.py`, `compare_pptx.py`)
- `${CLAUDE_SKILL_DIR}/examples/remind-magpie/` (`figure.py`, `links.py`): read it before starting a new diagram.

Requirements: Python 3 (standard library only, run with `python -I`), git, local clones of every linked repository,
and Edge or Chrome for previews and text measurement (`COUPLING_DIAGRAM_BROWSER` overrides the path).

## Working method (follow for every change)

1. **Work in the user's project folder.** Copy the example to e.g. `<project>/figure_src/`, adapt `figure.py` and
   `links.py`. Make `sys.path` point to `${CLAUDE_SKILL_DIR}/lib`. Temporary files only inside the project
   (e.g. `figure_src/_preview/`), never in system temp folders; delete them afterwards.
2. **Restore point before every change:** copy the layout script, link table and both outputs to
   `figure_src/backup-YYYYMMDD-vN/`. Users iterate many times and expect to roll back.
3. **Ask when a layout request is ambiguous** (which element, which direction, which of two readings). One short
   question is cheaper than a wrong iteration. Before a larger build, ask whether anything is unclear.
4. **Verify facts in the code, not in prose.** Pin each repository to a commit; read line numbers with
   `git show <commit>:<path>` in the local clone. If the user's wording contradicts the code (e.g. a default
   value), use the code and say so.
5. **Render and look at every result** before reporting (`tools/render.py`, then read the PNG). Check overlaps of
   text with arrows and borders, arrowheads, text running past box edges.
6. **Check the PPTX structurally** (all zip parts parse as XML; count shapes/arrows). Opening it in PowerPoint via
   COM/PowerShell may be blocked; then ask the user to open it.
7. **Never overwrite a PPTX the user may have edited** without a backup. If the file was saved by PowerPoint
   (larger, `docProps/` parts) or the user says they edited it: generate a fresh reference
   (`figure.py ref.pptx -`) and run `tools/compare_pptx.py ref.pptx edited.pptx`. The hand edit is the most precise
   specification: port every change into the layout script (coordinates in px; script coordinates are before
   cropping, i.e. PPTX y + CROP_Y), regenerate, and compare again until only intended deviations remain. Report
   deviations you made on purpose and obvious slips in the user's file (e.g. a text line left behind when moving a
   block, an arrow not following its box).

## Content: what to find out for a coupling

- **Where and when the coupling fires** inside REMIND (e.g. which GAMS phase of the Nash loop, condition, default
  iterations, switches) and whether the loop can stop early.
- **The call chain** from the start script to the partner model and back (scripts, functions, sequential or
  submitted runs), and the run folders of both models.
- **Every exchanged file:** who writes it, who reads it, which quantities it carries, in which iteration it is read.
- **Defaults and per-scenario settings** (verified in code), and code that exists only for the coupling.

## Visual conventions

- **Panels** = actors/processes (start-up, call chain, model structure, coupling script, partner model). Panels are
  containers: tinted background, no outline, numbered title in one common size (`Canvas(panel_title=...)`): the
  largest size at which the longest title still fits and leaves room for arrows (`tools/measure.py fit`).
- **Outlines only for actual steps** (scripts, functions, code blocks, files). Nested containers get a slightly
  stronger tint (`loopbg`), not an outline.
- **Iteration loop** (e.g. the Nash loop): tinted rectangle with a dashed outline that encloses everything running
  inside it, including partner panels; a thick control-flow arrow back to its first phase labelled "repeat ...".
- **File columns** between the panels whose code writes and reads them, with a heading "Files exchanged between X and
  Y" and a short direction label ("MAgPIE -> REMIND"). Place each file next to its writer/reader so arrows are
  straight; put several arrows on one line where the data flows straight through.
- **Arrows:** solid teal (`FLOW`) = control flow (calls, next step); solid magenta (`loop_arrow`, `LOOPC`) = data
  exchange through files. Direct routes with one crossing are better than long detours. Keep 15-30 px between
  parallel lines and between lines and edges; widen gaps between panels instead of squeezing arrows.
- **Step badges 1..n** on the arrows give the order of one coupling iteration; explain them in the legend.
- **Timeline** of the outer iterations: compress uninteresting ranges ("1, ..., 19"), highlight the coupling
  iterations, state the stop condition.
- **Tags** (pills) on conditional reads/actions: when they are executed (e.g. "coupling iterations only").
- **Colour categories** (`styles.py`): start-up inputs, REMIND R scripts, REMIND GAMS phases, coupling-specific code
  (only for code that exists solely for the coupling, also inside the partner model), partner model, files.
  Every new light colour needs a dark counterpart in `styles.DARK`.
- **Fonts:** Arial; four sizes only (body 11.5, box title 12.5, panel title, figure title); monospace only for code
  commands. `Canvas.norm_size` enforces this; the panel title size is exempt.
- **Title and description:** figure title may be large; the description paragraph below it says what the colours
  mean and how to use the HTML (hover, click). Give the PPTX a variant without the interaction sentence
  (`c.target = "pptx" / "html"`). Wrap with measured widths (`tools/measure.py wrap`), not estimates.
- **Legend:** colour boxes, both arrow types, step badges, tags; in the HTML also the two link types (`hint_xy`).
- **Crop** empty margins at the end (`c.crop_top(dy)`), keep about 20 px to the canvas edges.

## Links (HTML)

- `links.py` defines `Repo(name, url, commit)` per repository and the link entries
  `(pattern, ref, call_ref, condition)`; see `lib/coupling_diagram/links.py`. Full-line patterns first.
- The name links to the **call site** (or the code); if a call site exists, the "↪" marker links to the
  **definition**. Hover shows the lines with 5 context lines, linked lines highlighted, header `repo/path Lx-y @commit`.
- The build fails on non-existing files/line ranges and warns about unmatched patterns: when reworded text breaks a
  link, update the pattern. `condition={"y": ...}` uses the y position **after cropping**.
- Local clones: `local_paths.json` next to `links.py` (template `local_paths.example.json`, keep it out of git) or
  environment variables `COUPLING_DIAGRAM_<REPO>`.

## Library reference (`coupling_diagram`)

```python
c = Canvas(W, H, panel_title=19, styles={...})      # extra/override box styles: name -> (fill, stroke)
c.panel(x, y, w, h, title)                           # container
c.box(x, y, w, h, style, title, lines, size=11.5, tsize=12.5, mono_title=False, step=16)
c.rect(x, y, w, h, style, dash=False, rx=4, sw=1.3); c.text(x, y, s, size, bold, family, color=..., italic)
c.ctext(cx, y, s); c.tag(x, y, s, style); c.badge(cx, cy, n)
c.arrow(pts, label, lx, ly, color=FLOW, width=2.2); c.loop_arrow(pts, label, lx, ly)
c.off_y = dy        # move the following elements as a block;  c.target = "html" | "pptx" | "both"
c.crop_top(dy); c.write_svg_preview(p); c.write_pptx(p)
c.write_html(p, TABLE, title=..., note_xy=..., author=..., author_email=..., hint_xy=...)
```

## Pitfalls (learned the hard way)

- Elements drawn later cover earlier ones: draw an arrow **after** the panel backgrounds it enters, or its head
  disappears.
- A size below the panel-title exemption threshold is silently mapped to 15 px by `norm_size`; set sizes through
  `panel_title` or check the rendering.
- Underlining link text hides the underscores of code names; use colour, underline only on hover.
- PowerPoint "Convert to Shape" on an imported SVG drops all text; therefore the PPTX is written natively.
- Do not compare PPTX files by shape name or order; use `tools/compare_pptx.py` (content + nearest position).
- A one-letter variable like `c` for the canvas can be shadowed by loop variables (`for c, d in ...`).
- Character-count width estimates are wrong by up to ~15 %; measure in the browser before fitting text.
