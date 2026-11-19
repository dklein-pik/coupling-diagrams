"""Default palette (light, used for the PPTX) and its dark counterpart (used for the HTML page).

Box styles map a name to (fill, stroke). Diagrams may add their own styles; every new light colour that
should look different in the dark theme needs an entry in DARK.
"""

FONT = "Arial"
MONO = "Courier New"

STYLES = {
    "r":        ("#e8eef7", "#4a6fa5"),   # REMIND R scripts
    "gms":      ("#f2f2f2", "#7f7f7f"),   # REMIND GAMS phases
    "cpl":      ("#fff0dc", "#d9822b"),   # coupling-specific code
    "mag":      ("#e6f2e1", "#4f8a3c"),   # partner model (e.g. MAgPIE)
    "file":     ("#fffbe0", "#b59b00"),   # exchanged files
    "cmd":      ("#ffffff", "#404040"),   # code block inside a step
    "start":    ("#efe8f7", "#6a4c93"),   # start-up inputs
    "startcmd": ("#faf7fd", "#6a4c93"),
    "tagM":     ("#fde4ee", "#c2185b"),   # tag: only in coupling iterations
    "tagE":     ("#f2f2f2", "#7f7f7f"),   # tag: every iteration
    "panelbg":  ("#e2e5eb", "none"),      # container: panel (tinted background, no outline)
    "loopbg":   ("#d5d9e0", "none"),      # container: loop phase inside a panel
    "nash":     ("#f0f5fb", "#404040"),   # iteration loop (light tint, dashed outline)
    "badge":    ("#c2185b", "#c2185b"),   # step number of the coupling loop
}

FLOW = "#00838f"   # control flow arrows (calls, next step); no box border uses this colour
LOOPC = "#c2185b"  # coupling arrows (data exchange) and step badges
MAGC = "#4f8a3c"   # partner model accent (timeline labels)

DARK_BG = "#121417"
DARK = {  # light colour -> dark theme colour
    "#e8eef7": "#1b2a40", "#4a6fa5": "#6d9ee0",
    "#f2f2f2": "#262a30", "#7f7f7f": "#8a919b",
    "#fff0dc": "#3b2a12", "#d9822b": "#f0a050",
    "#e6f2e1": "#1c3320", "#4f8a3c": "#7cc46a",
    "#fffbe0": "#353014", "#b59b00": "#d8bd3a",
    "#ffffff": "#1a1d22", "#404040": "#9aa0a6",
    "#efe8f7": "#2b2240", "#6a4c93": "#a58bd8",
    "#faf7fd": "#211b2e", "#303030": "#c8ccd2",
    "#202020": "#e4e6ea",
    "#00838f": "#4dd0e1", "#c2185b": "#ff6b9a",   # control flow, coupling loop
    "#fde4ee": "#4a1830",
    "#e2e5eb": "#262b36", "#d5d9e0": "#313846", "#f0f5fb": "#111d2b",   # panels, loop container, iteration loop
}
