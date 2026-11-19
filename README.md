# coupling-diagrams

A Claude Code plugin for REMIND developers: it lets Claude create and revise **code-linked structure diagrams of
model couplings and data flows** (e.g. REMIND-MAgPIE). One layout script produces

- an **editable PowerPoint slide** (native shapes, light colours), and
- an **interactive dark HTML page**: code names link to the source lines on GitHub at pinned commits, hovering shows
  the code excerpt, a "↪" marker jumps to the definition.

The plugin contains one skill (`coupling-diagram`) with the working method and design rules, a small Python library
(standard library only), tools for measuring text, rendering previews and comparing hand-edited PPTX files, and the
REMIND-MAgPIE diagram as a worked example.

## Installation

In a terminal (Claude Code installed, git on PATH):

```
claude plugin marketplace add dklein-pik/coupling-diagrams
claude plugin install coupling-diagrams@pik-coupling-diagrams
```

or inside a Claude Code session: `/plugin marketplace add dklein-pik/coupling-diagrams`, then
`/plugin install coupling-diagrams@pik-coupling-diagrams`.
Updates: `claude plugin update coupling-diagrams@pik-coupling-diagrams` (auto-update is off by default for this
marketplace; enable it under `/plugin` -> Marketplaces).

## Requirements

- Python 3 (only the standard library is used)
- git and local clones of all repositories the diagram links to (e.g. remind, magpie, remind2)
- Microsoft Edge or Google Chrome for previews and text measurement (set `COUPLING_DIAGRAM_BROWSER` if it is not found)

## Usage

Ask Claude for a diagram of a coupling, e.g. *"Create a coupling diagram of how REMIND and MAgPIE exchange data"*,
or invoke the skill directly with `/coupling-diagrams:coupling-diagram`. Claude researches the coupling in the code,
builds the layout in your project folder (`figure_src/`), and iterates with you. You can also edit the PPTX by hand;
Claude compares it with the generated version and ports your edits into the layout script.

## Running the example

```
cd plugins/coupling-diagrams/skills/coupling-diagram/examples/remind-magpie
cp local_paths.example.json local_paths.json      # then enter the paths of your local clones
python -I figure.py remind_magpie.pptx remind_magpie.html
```

The example links to REMIND 3.7.1 (`be71302`), MAgPIE 4.14.2 (`fcbd591`) and remind2 2.9.0 (`e414aec`); these commits must
exist in your clones.

## Layout

```
.claude-plugin/marketplace.json            marketplace (this repository)
plugins/coupling-diagrams/
  .claude-plugin/plugin.json               plugin manifest
  skills/coupling-diagram/
    SKILL.md                               working method, conventions, pitfalls, library reference
    lib/coupling_diagram/                  Canvas, links, PPTX and HTML backends, styles
    tools/                                 measure.py, render.py, compare_pptx.py
    examples/remind-magpie/                figure.py, links.py, local_paths.example.json
```
