"""REMIND-MAgPIE coupling diagram (example for the coupling-diagram skill).

Usage: python -I figure.py OUT.pptx OUT.html [--svg PREVIEW.svg]   ("-" skips an output)
Coordinates are pixels before cropping (CROP_Y is subtracted at the end); text y = baseline.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
sys.path.insert(0, HERE)
from coupling_diagram import Canvas                      # noqa: E402
from coupling_diagram.styles import FLOW, LOOPC, MAGC, MONO   # noqa: E402
from links import TABLE                                  # noqa: E402

W, H = 2760, 1450
c = Canvas(W, H, panel_title=19)   # 19 px: largest size at which the panel 2 title leaves room for the arrow from panel 1
text, ctext, rect, box, tag, badge, panel, arrow, loop_arrow = (
    c.text, c.ctext, c.rect, c.box, c.tag, c.badge, c.panel, c.arrow, c.loop_arrow)
MAGPIE_ITER = [20, 24, 28, 32]   # default c_magpieIter (main.gms)
PT, PB = 250, 1415          # common top and bottom of panels 2, 3 and 4

Y_TITLE = 496.4             # first title line (moved up 25 px to make room for the subtitle)
T_SIZE = 53.33              # 40 pt
text(1201.5, Y_TITLE, "Structure of the", size=T_SIZE, bold=True)          # two lines (user's PPTX edit)
text(1201.5, Y_TITLE + 1.15 * T_SIZE, "REMIND-MAgPIE coupling", size=T_SIZE, bold=True)


SUB_1 = ("This diagram illustrates the call chain (blue lines) and data flow (pink lines) of the iterative soft-link "
         "between REMIND and MAgPIE within REMIND's Nash loop.")
SUB_HTML = (" Hover over a code element to preview its excerpt, click the code to view its usage on GitHub, "
            "or click the arrow to jump to its definition.")
SUB_3 = " By default, MAgPIE runs during Nash iterations 20, 24, 28, and 32 (configurable per scenario)."
# line breaks measured in the browser (Arial 12.5 px): the paragraph has the width of the timeline box above the title
SUB_LINES = {"html": ["This diagram illustrates the call chain (blue lines) and data flow (pink lines) of the iterative soft-link between REMIND and MAgPIE within", "REMIND's Nash loop. Hover over a code element to preview its excerpt, click the code to view its usage on GitHub, or click the arrow to", "jump to its definition. By default, MAgPIE runs during Nash iterations 20, 24, 28, and 32 (configurable per scenario)."],
             "pptx": ["This diagram illustrates the call chain (blue lines) and data flow (pink lines) of the iterative soft-link between REMIND and MAgPIE within", "REMIND's Nash loop. By default, MAgPIE runs during Nash iterations 20, 24, 28, and 32 (configurable per scenario)."]}
assert " ".join(SUB_LINES["html"]) == (SUB_1 + SUB_HTML + SUB_3).strip()
assert " ".join(SUB_LINES["pptx"]) == (SUB_1 + SUB_3).strip()
for c.target in ("html", "pptx"):
    for k, ln in enumerate(SUB_LINES[c.target]):
        text(1201.5, Y_TITLE + 1.15 * T_SIZE + 30 + 16.5 * k, ln, size=12.5)
c.target = "both"

# ---------------- Panel 1: starting a run ----------------
DY12 = 200.7               # panels 1 and 2 moved down as a block (user's PPTX edit)
c.off_y = DY12
panel(20, 50, 520, 184, "1  Starting a coupled run")
box(40, 88, 480, 34, "startcmd", "Rscript start.R config/scenario_config_magpie_XYZ.csv", mono_title=True, tsize=12.5)
box(40, 132, 232, 90, "start", "scenario_config_magpie*.csv",
    ["coupling settings per scenario:", "magpieIter, magpie_scen,", "cfg_mag$..., continueFromHere,", "no_ghgprices_land_until, ..."])
box(288, 132, 232, 90, "start", "scenario_config*.csv",
    ["REMIND settings of the", "same scenarios (same file", "name without _magpie);", "MAgPIE code: ./magpie or ../magpie"])

# ---------------- Panel 2: call chain ----------------
P2 = 24                     # panel 2 content moved down: larger gap to panel 1 and room for the run folder note
c.off_y = DY12 + P2
panel(20, PT - P2 / 2, 520, 653.4 + P2 / 2, "2  Chain of calls in start.R (coupling-relevant parts)")
text(40, 305 - P2, "run folder: output/C_<title>_<date>/", size=11)
arrow([(508, 234 - P2), (508, 286)])   # panel 1 -> start.R, right of the end of the panel 2 title (x 487)
box(40, 290, 480, 58, "r", "start.R",
    ["readCheckScenarioConfig(), selectScenarios(): coupled mode if the file name",
     "contains _magpie; only scenarios defined in both files are started"])
arrow([(280, 348), (280, 360)])
box(40, 362, 480, 58, "r", "configureCfg()   (for each scenario)",
    ["REMIND switches from scenario_config*.csv; cm_MAgPIE_Nash = 1",
     "c_magpieIter from column magpieIter; restart point from continueFromHere"])
arrow([(280, 420), (280, 432)])
box(40, 434, 480, 112, "cpl", "MAgPIE configuration (cfg$cfg_mag)",
    ["read magpie/config/default.cfg",
     "setScenario(): scenarios from column magpie_scen, then always \"coupling\"",
     "individual MAgPIE switches from columns cfg_mag$...",
     "c56_mute_ghgprices_until; optional external GHG prices (path_mif_ghgprice_land)",
     "checkSettingsRemMag(): consistency of REMIND and MAgPIE settings"])
arrow([(280, 546), (280, 558)])
box(40, 560, 480, 58, "r", "submit(cfg)",
    ["save <title>.RData; create run folder; write config.Rdata",
     "start prepareAndRun.R via SLURM (sbatch) or directly via Rscript"])
arrow([(280, 618), (280, 630)])
box(40, 632, 480, 58, "r", "prepareAndRun.R  ->  prepare()",
    ["copy cfg$files2export$start into run folder (incl. scripts/input/magpie.R)",
     "merge GAMS code of main.gms and the selected modules into full.gms"])
arrow([(280, 690), (280, 702)])
box(40, 704, 480, 42, "r", "run()",
    ["call GAMS: gams full.gms   (see panel 3)"])
arrow([(280, 746), (280, 772)], "after GAMS has finished", 290, 763)
box(40, 774, 480, 58, "r", "run() continued  ->  output.R (cfg$output)",
    ["reporting.R: appends MAgPIE report.mif (cfg$pathToMagpieReport)",
     "plotRemMagNash: convergence of the coupling across Nash iterations"])
arrow([(280, 832), (280, 844)])
box(40, 846, 480, 42, "r", "subsequent runs",
    ["submit() of runs whose reference gdx files are now available"])
box(40, 919.8, 480, 74, "file", "Final output: run folders",
    ["REMIND: output/C_<title>_<date>/  (full.gms, magpie.R, config.Rdata,",
     "   fulldata.gdx, magpieData.gdx, REMIND_rem2mag-<i>.mif)",
     "MAgPIE: magpie/output/C_<title>-mag-<i>/  (report.mif, fulldata.gdx)"], tsize=12)

c.off_y = 0

# ---------------- Timeline: Nash iterations with MAgPIE runs ----------------
TX, TY = 1190.7, 254.2      # timeline: top, right of panel 3 (position from the user's PPTX edit)
panel(TX, TY, 799.3, 178.4, "Nash iterations and MAgPIE runs")
text(TX + 96.9, TY + 162.1, "MAgPIE runs in the Nash iterations c_magpieIter = 20, 24, 28, 32 (default in main.gms; "
              "per scenario: column magpieIter)", size=11.5)
CELLS = [1, "...", 19] + list(range(20, 36)) + ["..."]   # compressed: iterations 2-18 and > 35 as "..."
NCELL, CX0, CSTEP = len(CELLS), TX + 15, 28
for k, i in enumerate(CELLS):
    x = CX0 + k * CSTEP
    st = "mag" if i in MAGPIE_ITER else "gms"
    rect(x, TY + 40, 26, 24, st, rx=3, sw=1.6 if st == "mag" else 1)
    ctext(x + 13, TY + 57, str(i), bold=st == "mag")
    if i in MAGPIE_ITER:
        ctext(x + 13, TY + 82, f"MAgPIE run {MAGPIE_ITER.index(i) + 1}", bold=True, color=MAGC)
xe = CX0 + NCELL * CSTEP + 4
text(xe, TY + 47, "until converged,")
text(xe, TY + 62, "but not before the last")
text(xe, TY + 77, "MAgPIE run (max. 100)")
rect(TX + 46.7, TY + 108.5, 26, 17, "gms", rx=3, sw=1)
text(TX + 79.7, TY + 121.5, "REMIND only (Nash iteration without MAgPIE)")
rect(TX + 46.7, TY + 134.8, 26, 17, "mag", rx=3, sw=1.6)
text(TX + 79.7, TY + 147.8, "REMIND and MAgPIE: MAgPIE runs in PRESOLVE, then REMIND solves with the updated land-use data")

# ---------------- Panel 3: REMIND GAMS structure ----------------
o = PT - 175                # vertical offset of panel 3 content
panel(600, PT, 530, PB - PT, "3  REMIND GAMS structure (main.gms, l. 2264 ff.)")
arrow([(520, 725 + DY12 + P2), (570, 725 + DY12 + P2), (570, 342), (616, 342)])   # run() (panel 2) -> SETS, drawn after the panel 3 background
text(620, 219 + o, "Each phase: core/<phase>.gms, then $batinclude modules/include.gms <phase>", size=11)
text(620, 235 + o, "(adds <phase>.gms of every active module realization)", size=11)
y = 250 + o
for name, note in [("SETS", ""), ("DECLARATIONS", ""),
                   ("DATAINPUT", "standalone values of MAgPIE quantities (lookup tables, supply curves)"),
                   ("EQUATIONS", ""), ("PRELOOP", "")]:
    h = 44 if note else 34
    box(620, y, 490, h, "gms", name, [note] if note else [], size=11)
    y += h + 12
rect(620, 490 + o, 490, 789, "loopbg", sw=0)
text(630, 510 + o, "LOOP   core/loop.gms", size=12.5, bold=True)
box(635, 521 + o, 460, 30, "cmd", "", [])
text(645, 541 + o, "execute_loadpoint \"input\"  (start gdx)", size=11)
rect(635, 563 + o, W - 10 - 635, 704, "nash", dash=True, sw=2.2)   # Nash loop (tinted), surrounds panels 4 and 5
text(645, 582 + o, "Nash iteration loop  (i = 1, 2, 3, ... until converged)", size=12, bold=True)
box(670, 593 + o, 410, 30, "gms", "BOUNDS", [])
# PRESOLVE
rect(670, 635 + o, 410, 448, "cpl", sw=2)
text(680, 655 + o, "PRESOLVE", size=12.5, bold=True)
rect(682, 665 + o, 386, 210, "cmd")
text(692, 683 + o, "core/presolve.gms", size=11.5, bold=True)
text(692, 703 + o, "if iteration in c_magpieIter (and cm_MAgPIE_Nash = 1):", size=11)
text(704, 719 + o, "sm_updateMagpieData = 1", size=11)
rect(704, 727 + o, 340, 46, "cpl", sw=2.2)
text(714, 745 + o, "Rscript magpie.R  <i>  <iteration>", size=12, family=MONO)
text(714, 763 + o, "runs only in Nash iterations 20, 24, 28, 32 (default)", size=10.5, bold=True, color=LOOPC)
text(704, 789 + o, "Execute_Loadpoint magpieData.gdx: pm_pebiolc_demandmag", size=11)
tag(704, 795 + o, "MAgPIE iterations only", "tagM")
text(692, 829 + o, "if MAgPIE has run before (sm_magpieIter > 0), every iteration:", size=11)
text(704, 847 + o, "Execute_Loadpoint magpieData.gdx: f_macBaseMagpie_coupling", size=11)
tag(704, 853 + o, "every iteration after the 1st MAgPIE run", "tagE")
rect(682, 885 + o, 386, 80, "cmd")
text(692, 903 + o, "modules/26_agCosts/costs/presolve.gms", size=11.5, bold=True)
text(692, 921 + o, "if sm_updateMagpieData = 1:", size=11)
text(704, 937 + o, "Execute_Loadpoint magpieData.gdx: p26_totLUcost_coupling", size=11)
tag(704, 943 + o, "MAgPIE iterations only", "tagM")
rect(682, 975 + o, 386, 98, "cmd")
text(692, 993 + o, "modules/30_biomass/magpie/presolve.gms", size=11.5, bold=True)
text(692, 1011 + o, "if sm_updateMagpieData = 1:", size=11)
text(704, 1027 + o, "Execute_Loadpoint magpieData.gdx: p30_pebiolc_pricemag", size=11)
tag(704, 1033 + o, "MAgPIE iterations only", "tagM")
text(704, 1063 + o, "shift of the bioenergy supply curve to the MAgPIE price", size=11)
box(670, 1095 + o, 410, 44, "gms", "SOLVE", ["regions solved independently (Nash algorithm)"], size=11)
box(670, 1151 + o, 410, 44, "gms", "POSTSOLVE", ["e.g. price update from market surpluses, convergence check"], size=11)
box(670, 1205 + o, 410, 30, "file", "", [])
text(680, 1225 + o, "execute_unload fulldata.gdx (if optimal); read by magpie.R", size=11)
arrow([(670, 1220 + o), (652, 1220 + o), (652, 608 + o), (666, 608 + o)], width=3)   # next Nash iteration
text(662, 1257 + o, "repeat with the next Nash iteration (i + 1) until converged", size=11, italic=True, color=FLOW)
box(620, 1291 + o, 490, 34, "gms", "OUTPUT", [])

# ---------------- Panel 4: magpie.R ----------------
# The contents of panels 4 and 5 start at the height of the Nash iteration loop in panel 3 (dashed line).
Y_NASH = 563 + o            # top of the dashed Nash loop in panel 3
SHIFT45 = 80                # panels 4 and 5 lie inside the Nash loop, below its top line
o4 = Y_NASH - 230 + SHIFT45 # vertical offset of panel 4 content
d5 = o4 - o                 # vertical shift of panel 5 content and of the file column between panels 4 and 5
X4 = 1480                   # left edge of the boxes in panel 4
XC = (X4 + 240)             # centre line for the step arrows
P45_T = Y_NASH + SHIFT45 - 63                        # frames of panels 4 and 5 fitted to the content of panel 4
P45_H = 666.4                              # height from the user's PPTX edit
panel(X4 - 20, P45_T, 530, P45_H, "4  magpie.R (in the run folder)")
text(X4, 219 + o4, "arguments: MAgPIE iteration i, Nash iteration", size=11)
box(X4, 230 + o4, 480, 42, "cpl", "", [])
text(X4 + 10, 248 + o4, "rename magpieData.gdx  ->  magpieData-<i-1>.gdx", size=12.5, bold=True)
text(X4 + 10, 264 + o4, "So REMIND cannot continue with outdated data if the script fails", size=11.5)
arrow([(XC, 272 + o4), (XC, 284 + o4)])
box(X4, 286 + o4, 480, 58, "cpl", "Choose entry point",
    ["regular coupling iteration: all three steps below",
     "continueFromHere (1st Nash iteration only): full | runMAgPIE | getMagpieData"])
arrow([(XC, 344 + o4), (XC, 356 + o4)])
box(X4, 358 + o4, 480, 74, "cpl", "createREMINDReporting()",
    ["reads fulldata.gdx (solution of the preceding Nash iteration)",
     "remind2::convGDX2MIF_REMIND2MAgPIE()  ->  REMIND_rem2mag-<i>.mif"])
arrow([(XC, 432 + o4), (XC, 444 + o4)])
rect(X4, 446 + o4, 480, 170, "cpl")
text(X4 + 10, 464 + o4, "runMAgPIE()   (working directory: MAgPIE folder)", size=12.5, bold=True)
text(X4 + 10, 480 + o4, "bioenergy demand and GHG prices from REMIND_rem2mag-<i>.mif", size=11.5)
text(X4 + 10, 496 + o4, "start values: MAgPIE gdx files of run i-1 for t >= cm_startyear", size=11.5)
box(X4 + 20, 505 + o4, 440, 42, "cmd", "start_run(cfg_mag)",
    ["starts MAgPIE run i (panel 5) and waits for it"], size=11.5, mono_title=True)
text(X4 + 10, 570 + o4, "stop if the MAgPIE model status is not 2 or 7 in every time step", size=11.5)
text(X4 + 10, 586 + o4, "returns the path to report.mif", size=11.5)
arrow([(XC, 616 + o4), (XC, 628 + o4)])
box(X4, 630 + o4, 480, 90, "cpl", "getMagpieData()",
    ["read report.mif; select variables via mapping table mag2rem",
     "unit conversion; sum categories that map to the same REMIND type",
     "write magpieData.gdx and reporting/AirPollutantsMAgPIE.cs4r"])
arrow([(XC, 720 + o4), (XC, 732 + o4)])
box(X4, 734 + o4, 480, 42, "cpl", "", [])
text(X4 + 10, 752 + o4, "save cfg (incl. pathToMagpieReport) to config.Rdata", size=11.5)
text(X4 + 10, 768 + o4, "return to GAMS PRESOLVE", size=11.5)

# ---------------- Panel 5: MAgPIE ----------------
X5 = 2280                   # left edge of the boxes in panel 5
panel(X5 - 20, P45_T, 480, P45_H, "5  MAgPIE")                 # width fitted to its content
text(X5, 294 + d5, "run folder: magpie/output/C_<title>-mag-<i>/", size=11)
rect(X5, 330 + d5, 440, 285, "mag")
text(X5 + 10, 348 + d5, "start_run(cfg_mag)", size=12.5, family=MONO)
text(X5 + 10, 366 + d5, "called by runMAgPIE() (magpie.R); sequential run", size=11)
text(X5 + 10, 382 + d5, "copies the model to the run folder and applies cfg_mag;", size=11)
text(X5 + 10, 398 + d5, "scenario \"coupling\": c60_2ndgen_biodem and", size=11)
text(X5 + 10, 414 + d5, "c56_pollutant_prices use the data from REMIND", size=11)
rect(X5 + 15, 426 + d5, 410, 136, "cpl")   # getReportData(): coupling-specific
text(X5 + 25, 444 + d5, "getReportData()", size=12, family=MONO)
text(X5 + 25, 462 + d5, "reads REMIND_rem2mag-<i>.mif, writes MAgPIE inputs:", size=11)
text(X5 + 25, 480 + d5, "bioenergy demand ->", size=11)
text(X5 + 37, 496 + d5, "60_bioenergy/input/reg.2ndgen_bioenergy_demand.csv", size=11)
text(X5 + 25, 514 + d5, "GHG prices ->", size=11)
text(X5 + 37, 530 + d5, "56_ghg_policy/input/f56_pollutant_prices_coupling.cs3", size=11)
text(X5 + 10, 586 + d5, "Rscript submit.R", size=11.5, family=MONO)
text(X5 + 10, 603 + d5, "start_run() waits until the run has finished", size=11)
arrow([(X5 + 220, 615 + d5), (X5 + 220, 638 + d5)])
rect(X5, 640 + d5, 440, 110, "mag")
text(X5 + 10, 658 + d5, "submit.R", size=12.5, family=MONO)
text(X5 + 10, 676 + d5, "gams full.gms: MAgPIE optimization", size=11.5)
text(X5 + 10, 692 + d5, "(recursive-dynamic land-use optimization)", size=11.5)
text(X5 + 10, 708 + d5, "MAgPIE output scripts (cfg$output):", size=11.5)
text(X5 + 22, 724 + d5, "rds_report writes report.mif", size=11.5)
arrow([(X4 + 460, 601 + d5), (X5 - 4, 601 + d5)], "starts MAgPIE", X4 + 613, 594 + d5)   # runMAgPIE() -> start_run()

# ---------------- Exchanged files ----------------
FX, FW = 1190, 210          # file column between panels 3 and 4 (60 px gaps for the arrows)
FX2 = 2020                  # file column between panels 4 and 5
y_call, y_d1 = 750 + o, 251 + o4                # Rscript magpie.R box (panel 3), rename box (panel 4)
arrow([(1044, y_call), (1150, y_call), (1150, y_d1), (X4 - 4, y_d1)], "calls magpie.R", FX + 20, y_d1 - 7)
Y_FH = 671                  # common baseline of both file column headings
text(FX, Y_FH, "Files exchanged between", size=11.5, bold=True)
text(FX, Y_FH + 16, "REMIND and magpie.R", size=11.5, bold=True)
text(FX2, Y_FH, "Files exchanged between", size=11.5, bold=True)
text(FX2, Y_FH + 16, "magpie.R and MAgPIE", size=11.5, bold=True)
# REMIND_rem2mag-<i>.mif: written by createREMINDReporting(), read by getReportData() in MAgPIE
y_rm = 470 + d5
box(FX2, y_rm, FW, 60, "file", "REMIND_rem2mag-<i>.mif",
    ["reduced REMIND report:", "bioenergy demand, GHG prices"], size=11, step=14, tsize=12)
y_rma = y_rm + 27.5         # both REMIND_rem2mag arrows on one line
loop_arrow([(X4 + 480, y_rma), (FX2 - 4, y_rma)], dash=True)
loop_arrow([(FX2 + FW, y_rma), (X5 - 4, y_rma)], dash=True)
# report.mif: written by MAgPIE, read by getMagpieData()
y_rp = 1117.9
Y_OUT = 1136.9              # one line: MAgPIE -> report.mif -> getMagpieData() -> magpieData.gdx
box(FX2, y_rp, FW, 41.5, "file", "report.mif", ["Full MAgPIE report of run i"], size=11, step=14, tsize=12)
loop_arrow([(X5, Y_OUT), (FX2 + FW + 4, Y_OUT)], dash=True)
loop_arrow([(FX2, Y_OUT), (X4 + 484, Y_OUT)], dash=True)
# fulldata.gdx (top): written at the end of each Nash iteration, read by createREMINDReporting() at the next MAgPIE run
y_fd_save = 1220 + o        # fulldata step at the end of the Nash loop (panel 3)
y_fd = 395 + o4             # createREMINDReporting() (panel 4)
box(FX, y_fd - 32, FW, 57, "file", "fulldata.gdx",
    ["REMIND solution of the latest", "optimal Nash iteration"], size=11, step=14)
loop_arrow([(1080, y_fd_save), (1170, y_fd_save), (1170, y_fd), (FX - 4, y_fd)], dash=True)
loop_arrow([(FX + FW, y_fd), (X4 - 4, y_fd)], dash=True)
text(FX, y_fd - 40, "REMIND -> MAgPIE", size=11, bold=True, color=LOOPC)
# magpieData.gdx (below): written by getMagpieData(), read in PRESOLVE of the same Nash iteration
y_read = 1045               # gap between the 26_agCosts and the 30_biomass box in PRESOLVE
y_md = y_read - 52
text(FX, y_md - 42, "MAgPIE -> REMIND", size=11, bold=True, color=LOOPC)
text(FX, y_md - 26, "read in PRESOLVE of the", size=11, color=LOOPC)
text(FX, y_md - 10, "same Nash iteration", size=11, color=LOOPC)
box(FX, y_md, FW, 167.3, "file", "magpieData.gdx", [])
for k, (par, desc) in enumerate([("pm_pebiolc_demandmag", "bioenergy production"),
                                 ("p30_pebiolc_pricemag", "bioenergy price"),
                                 ("p26_totLUcost_coupling", "land-use costs"),
                                 ("f_macBaseMagpie_coupling", "land-use emissions (CO2, CH4, N2O)")]):
    text(FX + 10, y_md + 38 + 34 * k, par, size=11)
    text(FX + 16, y_md + 52 + 34 * k, desc, size=10)
loop_arrow([(X4, Y_OUT), (FX + FW + 4, Y_OUT)], dash=True)
loop_arrow([(FX, y_read), (1072, y_read)], "read", 1084, y_read - 7, dash=True)

# ---------------- Steps of one coupling iteration ----------------
badge(1335, y_d1, 1)                   # PRESOLVE calls magpie.R
badge((FX + FW + X4) / 2, y_fd, 2)     # createREMINDReporting() reads fulldata.gdx
badge(2246.3, y_rma, 3)   # MAgPIE reads REMIND_rem2mag-<i>.mif
badge(X5 + 95, 654 + d5, 4)            # MAgPIE run
badge(1995.4, Y_OUT, 5)   # getMagpieData() reads report.mif
badge(1148, y_read, 6)                 # PRESOLVE reads magpieData.gdx

# ---------------- Legend (one column at the top right, positions from the user's PPTX edit) ----------------
c.off_y = -10                 # legend moved up a bit (more distance to the Nash loop)
LXA, LXB = 2287.8, 2292.1   # colour boxes; arrows / steps / tags
text(2279.8, 265.0, "Legend", size=c.panel_title, bold=True)
items = [("start", "start-up inputs (command, scenario files)"), ("r", "REMIND R scripts (start, submission, output)"),
         ("gms", "REMIND GAMS phases"), ("cpl", "coupling-specific code"), ("mag", "MAgPIE"), ("file", "files")]
for k, (st, lab) in enumerate(items):
    yy = 288.0 + 24.88 * k
    rect(LXA, yy, 34, 18, st, rx=3)
    text(LXA + 44, yy + 14, lab)
arrows_legend = [(FLOW, False, "control flow (call, next step)"),
                 (LOOPC, False, "coupling loop: data exchange (file)")]
for k, (col, d, lab) in enumerate(arrows_legend):
    yy = 449.7 + 20.4 * k
    arrow([(LXB, yy), (LXB + 42, yy)], color=col, dash=d, width=2.8 if col == LOOPC else 2.2)
    text(LXB + 52, yy + 4.1, lab)
for k in range(6):
    badge(LXB + 10 + 24 * k, 504.1, k + 1)
text(LXB + 160, 508.2, "steps of one coupling iteration")
text(LXB - 6.7, 540.9, "tags: when a GAMS read is executed")
tag(LXB - 6.7, 553.1, "MAgPIE iterations only", "tagM")
tag(LXB - 6.7, 576.5, "every iteration after the 1st MAgPIE run", "tagE")

c.off_y = 0


# ---------------- Crop the empty band at the top ----------------
CROP_Y = 230                # everything moves up; top margin 20 px like the other edges
NASH_BOTTOM = 563 + o + 704 - CROP_Y      # bottom edge of the dashed Nash loop (after cropping)
c.crop_top(CROP_Y)

args = sys.argv[1:]
if "--svg" in args:
    k = args.index("--svg")
    c.write_svg_preview(args[k + 1])
    del args[k:k + 2]
if len(args) > 0 and args[0] != "-":
    c.write_pptx(args[0])
if len(args) > 1 and args[1] != "-":
    c.write_html(args[1], TABLE, title="Structure of the REMIND-MAgPIE coupling",
                 note_xy=(c.W - 10, NASH_BOTTOM + 20), author="David Klein",
                 author_email="david.klein@pik-potsdam.de", hint_xy=(2285.4, 372))
