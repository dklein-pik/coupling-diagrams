"""Links of the REMIND-MAgPIE example: diagram text -> source lines at pinned commits.

Entry format and matching rules: see coupling_diagram/links.py. Local clones: local_paths.json next to this file
(copy local_paths.example.json) or environment variables COUPLING_DIAGRAM_REMIND / _MAGPIE / _REMIND2.
"""
import os

from coupling_diagram import LinkTable, Repo

HERE = os.path.dirname(os.path.abspath(__file__))
REPOS = [
    Repo("remind", "https://github.com/remindmodel/remind", "be7130269a4a6acb6dc56698a0e50c96c35e2f32"),
    Repo("magpie", "https://github.com/magpiemodel/magpie", "fcbd591df88eb2a27fb255421943b3d819d23696"),   # MAgPIE 4.14.2
    Repo("remind2", "https://github.com/pik-piam/remind2", "e414aecde1eb0ce334c2424367617d711374ea09"),    # remind2 2.9.0
]
RELABEL = {}   # text replacements applied to the HTML only


def R(path, a=None, b=None):
    return ("remind", path, a, b if b else a)


def M(path, a=None, b=None):
    return ("magpie", path, a, b if b else a)


MAG = "scripts/input/magpie.R"
PRE = "core/presolve.gms"
LOOP = "core/loop.gms"
P26 = "modules/26_agCosts/costs/presolve.gms"
P30 = "modules/30_biomass/magpie/presolve.gms"

LINKS = [
    # ---------- full-line entries (code chunks) ----------
    ("gams full.gms: MAgPIE optimization", M("scripts/run_submit/submit.R", 34, 38), None, None),
    ("rds_report writes report.mif", M("scripts/output/rds_report.R", 30, 43), None, None),
    ("Rscript submit.R", M("scripts/start_functions.R", 560, 584), None, None),
    ("60_bioenergy/input/reg.2ndgen_bioenergy_demand.csv", M("scripts/start_functions.R", 596, 604), None, None),
    ("56_ghg_policy/input/f56_pollutant_prices_coupling.cs3", M("scripts/start_functions.R", 606, 627), None, None),
    ("getReportData()", M("scripts/start_functions.R", 589, 668), M("scripts/start_functions.R", 322, 326), None),
    ("c60_2ndgen_biodem", M("config/scenario_config.csv", 77), None, None),
    ("c56_pollutant_prices", M("config/scenario_config.csv", 71), None, None),
    ("sequential run", R("start.R", 482), None, None),
    ("C_<title>-mag-<i>", R(MAG, 115, 117), None, None),
    ("c_magpieIter = 20, 24, 28, 32", R("main.gms", 1413, 1418), None, None),
    ("runs only in Nash iterations 20, 24, 28, 32 (default)", R("main.gms", 1413, 1418), None, None),
    ("but not before the last", R("modules/80_optimization/nash/postsolve.gms", 753, 758), None, None),
    ("(max. 100)", R("modules/80_optimization/nash/datainput.gms", 22), None, None),
    ("until converged", R("modules/80_optimization/nash/postsolve.gms", 753, 762), None, None),
    ("if iteration in c_magpieIter (and cm_MAgPIE_Nash = 1):", R(PRE, 107, 112), None, None),
    ("Execute_Loadpoint magpieData.gdx: pm_pebiolc_demandmag", R(PRE, 129, 131), None, None),
    ("if MAgPIE has run before (sm_magpieIter > 0), every iteration:", R(PRE, 134, 136), None, None),
    ("Execute_Loadpoint magpieData.gdx: f_macBaseMagpie_coupling", R(PRE, 137, 140), None, None),
    ("Execute_Loadpoint magpieData.gdx: p26_totLUcost_coupling", R(P26, 22, 23), None, None),
    ("Execute_Loadpoint magpieData.gdx: p30_pebiolc_pricemag", R(P30, 21, 22), None, None),
    ("if sm_updateMagpieData = 1:", R(P26, 20, 21), None, {"y": 766}),   # text y after cropping (CROP_Y = 230)
    ("if sm_updateMagpieData = 1:", R(P30, 10, 12), None, {"y": 856}),
    ("sm_updateMagpieData = 1", R(PRE, 107, 112), None, None),
    ("shift of the bioenergy supply curve to the MAgPIE price", R(P30, 29, 127), None, None),
    ("Rscript magpie.R  <i>  <iteration>", R(MAG, 327, 334), R(PRE, 114, 126), None),
    ("execute_unload fulldata.gdx (if optimal)", R(LOOP, 164, 182), None, None),
    ("read by magpie.R", R(MAG, 342, 345), None, None),
    ("rename magpieData.gdx  ->  magpieData-<i-1>.gdx", R(MAG, 336, 337), None, None),
    ("arguments: MAgPIE iteration i, Nash iteration", R(MAG, 327, 334), None, None),
    ("continueFromHere (1st Nash iteration only): full | runMAgPIE | getMagpieData", R(MAG, 342, 366), R("start.R", 442, 470), None),
    ("regular coupling iteration: all three steps below", R(MAG, 342, 345), None, None),
    ("reads fulldata.gdx (solution of the preceding Nash iteration)", R(MAG, 344), None, None),
    ("start values: MAgPIE gdx files of run i-1 for t >= cm_startyear", R(MAG, 148, 155), None, None),
    ("stop if the MAgPIE model status is not 2 or 7 in every time step", R(MAG, 166, 176), None, None),
    ("unit conversion; sum categories that map to the same REMIND type", R(MAG, 305, 313), None, None),
    ("save cfg (incl. pathToMagpieReport) to config.Rdata", R(MAG, 368, 375), None, None),
    ("bioenergy demand and GHG prices", R(MAG, 115, 123), None, None),
    ("standalone values of MAgPIE quantities", R("modules/30_biomass/magpie/datainput.gms", 42, 51), None, None),
    ("lookup tables", R("modules/26_agCosts/costs/datainput.gms", 14, 29), None, None),
    ("supply curves", R("modules/30_biomass/magpie/datainput.gms", 55, 70), None, None),
    ("coupled mode", R("start.R", 239, 247), None, None),
    ("only scenarios defined in both files are started", R("start.R", 254, 273), None, None),
    ("./magpie or ../magpie", R("start.R", 276, 281), None, None),
    ("SLURM (sbatch) or directly via Rscript", R("scripts/start/submit.R", 125, 142), None, None),
    ("save <title>.RData", R("start.R", 567, 572), None, None),
    ("create run folder; write config.Rdata", R("scripts/start/submit.R", 104, 111), None, None),
    ("merge GAMS code of main.gms and the selected modules into full.gms", R("scripts/start/prepare.R", 203, 219), None, None),
    ("gams full.gms", R("scripts/start/run.R", 31, 36), None, None),
    ("of runs whose reference gdx files are now available", R("scripts/start/run.R", 160, 244), None, None),
    ("subsequent runs", R("scripts/start/run.R", 160, 244), None, None),
    ("main.gms, l. 2264 ff.", R("main.gms", 2263, 2308), None, None),
    ("Nash iteration loop", R(LOOP, 35, 43), None, None),
    ("regions solved independently (Nash algorithm)", R(LOOP, 69, 89), None, None),
    # ---------- functions: definition + call site ----------
    ("readCheckScenarioConfig()", R("scripts/start/readCheckScenarioConfig.R", 18), R("start.R", 243), None),
    ("selectScenarios()", R("scripts/start/selectScenarios.R", 15), R("start.R", 244), None),
    ("configureCfg()", R("scripts/start/configureCfg.R", 8), R("start.R", 351, 353), None),
    ("checkSettingsRemMag()", R("scripts/start/checkSettingsRemMag.R", 5), R("start.R", 555), None),
    ("submit(cfg)", R("scripts/start/submit.R", 20), R("start.R", 592), None),
    ("submit()", R("scripts/start/submit.R", 20), R("scripts/start/run.R", 205, 207), None),
    ("prepareAndRun.R", R("scripts/start/prepareAndRun.R", 17, 30), R("scripts/start/submit.R", 127, 138), None),
    ("prepare()", R("scripts/start/prepare.R", 8), R("scripts/start/prepareAndRun.R", 21), None),
    ("run()", R("scripts/start/run.R", 8), R("scripts/start/prepareAndRun.R", 29), None),
    ("output.R", R("output.R"), R("scripts/start/run.R", 265, 273), None),
    ("reporting.R", R("scripts/output/single/reporting.R", 138, 163), None, None),
    ("plotRemMagNash", R("scripts/output/single/plotRemMagNash.R"), R("start.R", 473), None),
    ("setScenario()", R("start.R", 490, 516), None, None),
    ("magpie/config/default.cfg", M("config/default.cfg"), R("start.R", 478, 483), None),
    ("\"coupling\"", M("config/scenario_config.csv", 71, 77), R("start.R", 505, 506), None),
    ("createREMINDReporting()", R(MAG, 92, 102), R(MAG, 344), None),
    ("remind2::convGDX2MIF_REMIND2MAgPIE()", ("remind2", "R/convGDX2MIF_REMIND2MAgPIE.R", 23, 25), R(MAG, 99), None),
    ("runMAgPIE()", R(MAG, 104, 183), R(MAG, 345), None),
    ("start_run(cfg_mag)", M("scripts/start_functions.R", 217), R(MAG, 160, 164), None),
    ("getMagpieData()", R(MAG, 272, 325), R(MAG, 371, 372), None),
    ("reporting/AirPollutantsMAgPIE.cs4r", R(MAG, 259, 270), R(MAG, 321, 323), None),
    # ---------- switches, settings, parameters ----------
    ("cm_MAgPIE_Nash = 1", R("start.R", 351), None, None),
    ("c_magpieIter", R("start.R", 437, 440), None, None),
    ("magpieIter", R("start.R", 437, 440), None, None),
    ("continueFromHere", R("start.R", 442, 470), None, None),
    ("magpie_scen", R("start.R", 485, 503), None, None),
    ("cfg_mag$", R("start.R", 508, 516), None, None),
    ("c56_mute_ghgprices_until", R("start.R", 521, 522), None, None),
    ("no_ghgprices_land_until", R("start.R", 521, 522), None, None),
    ("path_mif_ghgprice_land", R("start.R", 524, 545), None, None),
    ("MAgPIE configuration", R("start.R", 433, 560), None, None),
    ("cfg$files2export$start", R("config/default.cfg", 153, 167), R("scripts/start/prepare.R", 191, 198), None),
    ("scripts/input/magpie.R", R("config/default.cfg", 164), None, None),
    ("cfg$pathToMagpieReport", R(MAG, 368, 369), R("scripts/output/single/reporting.R", 140), None),
    ("mag2rem", R(MAG, 1, 45), None, None),
    ("read report.mif", R(MAG, 285, 287), None, None),
    ("report.mif", R(MAG, 161, 164), None, None),
    ("REMIND_rem2mag-<i>.mif", R(MAG, 92, 102), None, None),
    ("pm_pebiolc_demandmag", R(MAG, 6), None, None),
    ("p30_pebiolc_pricemag", R(MAG, 8), None, None),
    ("p26_totLUcost_coupling", R(MAG, 7), None, None),
    ("f_macBaseMagpie_coupling", R(MAG, 9, 45), None, None),
    ("magpieData.gdx", R(MAG, 185, 257), R(MAG, 316, 319), None),
    ("scenario_config_magpie_XYZ.csv", R("config/scenario_config_magpie.csv", 1), None, None),
    ("scenario_config_magpie*.csv", R("config/scenario_config_magpie.csv", 1), None, None),
    ("scenario_config*.csv", R("config/scenario_config.csv", 1), None, None),
    # ---------- files and GAMS phases ----------
    ("start.R", R("start.R", 239, 247), None, None),
    ("modules/include.gms", R("modules/include.gms"), None, None),
    ("core/loop.gms", R(LOOP, 28, 59), R("main.gms", 2298), None),
    ("core/presolve.gms", R(PRE, 103, 148), R(LOOP, 54), None),
    ("modules/26_agCosts/costs/presolve.gms", R(P26, 15, 24), R(LOOP, 55), None),
    ("modules/30_biomass/magpie/presolve.gms", R(P30, 10, 27), R(LOOP, 55), None),
    ("magpie.R", R(MAG, 327, 377), None, None),
    ("SETS", R("main.gms", 2264, 2268), None, None),
    ("DECLARATIONS", R("main.gms", 2270, 2274), None, None),
    ("DATAINPUT", R("main.gms", 2276, 2280), None, None),
    ("EQUATIONS", R("main.gms", 2282, 2286), None, None),
    ("PRELOOP", R("main.gms", 2288, 2293), None, None),
    ("LOOP", R("main.gms", 2295, 2298), None, None),
    ("OUTPUT", R("main.gms", 2300, 2306), None, None),
    ("execute_loadpoint \"input\"", R(LOOP, 28, 33), None, None),
    ("BOUNDS", R(LOOP, 44, 48), None, None),
    ("PRESOLVE", R(LOOP, 51, 55), None, None),
    ("SOLVE", R(LOOP, 69, 89), None, None),
    ("POSTSOLVE", R(LOOP, 155, 159), None, None),
]

TABLE = LinkTable(REPOS, LINKS, RELABEL, local_paths=os.path.join(HERE, "local_paths.json"))
