# simulation — TP2 plots and animations

Java engine: `experiment/` (Maven). This folder only starts that engine and reads its text files.

## Setup

Python 3.12+. Animations default to GIF + MP4. Pillow writes GIF; the pinned
`imageio-ffmpeg` package supplies the MP4 encoder, so no system FFmpeg is required.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Recommended workflow

From the repo root:

```
py -3 simulation/main.py
```

The interactive assistant presents three options:

1. **Generate data.** Choose the assignment sweep, the 24 animation runs,
   the CIM benchmark, or a custom simulation. Each result is stored as a
   timestamped batch under `output/simulation/`.
2. **Generate results from existing data.** Select any combination of animations,
   figures b–e, the Vicsek/Voter comparison, the HTML explorer, and the CIM
   comparison. This stage never reruns the physical simulation.
3. **Do the complete assignment (a–g).** Choose whether to reuse three existing
   batches (observables, animations, and CIM) or create everything from scratch.
   Starting from scratch requires confirmation because the sweep contains
   1950 runs across the two density passes, all with `T=10000`.

`observables.txt` is always written. `dynamic.txt` is generated only for the
24 characteristic animation runs because it is substantially larger.

The same actions are available as explicit commands:

```
py -3 simulation/main.py --help
py -3 simulation/main.py simulate -- --model both --rho 2,4,8 --eta 0:6:0.5 --T 10000
py -3 simulation/main.py time-series --batch <batch> --compare
py -3 simulation/main.py polarization-vs-noise --batch <batch> --compare
py -3 simulation/main.py clusters --batch <batch> --compare
py -3 simulation/main.py polarization-vs-cluster --batch <batch> --compare
py -3 simulation/main.py animation --batch <batch> --run-dir <run> --format both
```

The old short names (`run`, `fig-b`, `fig-c`, `fig-d`, `fig-e`, `fig-g`,
`animate`) remain as aliases. On Linux/WSL, replace `py -3` with `python3`.

Figures write a combined view plus one file per curve. Point (c) is always one
file per model (never a Vicsek+Votante overlay). `--compare` overlays Vicsek and
Votante only on (b), (d) time, and (e). Error bars are the seed-to-seed standard
deviation of the stationary means (`va_ss_std` / `S_ss_std`); `_yerr_col` falls
back to the mean temporal spread (`va_ss_err` / `S_ss_err`) only when a point has
a single realization. Interactive reuse can type a full Windows or WSL
path; that becomes `--out`. `--out` already accepts a full path from the CLI.

Maven is invoked as:

```
mvn -f experiment/pom.xml clean compile exec:java -Dexec.args=...
```

with an absolute `--out` under `output/simulation/<timestamp>/`.

The production sweep runs in two passes over one batch, because Java's
`--repeats` is global: ρ=`2,4,8` with 5 repeats (390 runs), then the cluster
densities ρ=`0.1061,0.1592,0.3183` (1/(3π), 1/(2π), 1/π) with 20 repeats
(1560 runs). Both use η=`0:6:0.5`, η_mid=`3.5` and `T=10000` (votante at η=0
needs ~10³ steps to reach consensus; the low densities hold only 11 to 32
particles, so S(t) wanders with correlation times of ~10³ steps and needs both
the long run and more realizations). Wall-clock: ~1 h 15 min for ρ=2,4,8
(N=800 dominates), ~3 min for the low densities. With `rc=1`
the three assignment densities leave `S` saturated near 1 for every η, so points
(d) and (e) need the low ones to show anything. Java names those run folders from
ρ = N/L² (`rho0.32` / `rho0.16` / `rho0.11`); `io.rho_close` bridges the two
spellings.
`t0` is detected automatically, per run -- there is no per-model constant;
`--t-onset` and `--t-onset-csv` still override it by hand. Criterion (point
b): the series is smoothed with a moving average (`--window 50`); the last half
of the run (`--tail-frac 0.5`) defines the *stationary band* (2.5–97.5
percentiles of that moving average, widened by `max(atol, rtol*width)`); `t0`
is the first time the moving average enters the band, stays inside for
`--sustain 100` steps and from then on leaves it at most `--max-outside 10%` of
the time. A wide band near the transition (large fluctuations) is accepted; a
narrow band on a plateau makes `t0` wait for the plateau. Every run gets a `t0`
and a value; runs whose tail still trends (the two halves of the tail differ by
more than `max(2*atol, 0.25*width)`) are flagged `drift` in the console and in
`output/data/estacionario_por_corrida.csv` (per-run `t0`, status and band) —
`output/data/estacionario_promedios.csv` holds the per-(model, ρ, η) means,
their seed-to-seed σ and how many runs drifted. Figure (b) marks `t0` with a
vertical line. `--t-min` is only a floor (default 0). `PLAN.md` retains the
original calibration rationale for the longer run.

## TP1 times (point g)

`simulation/tp1/cim_times_tp1.csv` is the only source of the TP1 CIM times.
Fill it in (see `simulation/tp1/README.md`); `cim-comparison` picks it up
automatically and overlays it on the TP2 curves. `--tp1 <csv>` overrides it.
