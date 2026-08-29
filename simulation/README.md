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

1. **Generate data.** Choose the assignment sweep, the 18 animation runs,
   the CIM benchmark, or a custom simulation. Each result is stored as a
   timestamped batch under `output/simulation/`.
2. **Generate results from existing data.** Select any combination of animations,
   figures b–e, the Vicsek/Voter comparison, the HTML explorer, and the CIM
   comparison. This stage never reruns the physical simulation.
3. **Do the complete assignment (a–g).** Choose whether to reuse three existing
   batches (observables, animations, and CIM) or create everything from scratch.
   Starting from scratch requires confirmation because the sweep contains
   390 runs. The current production profile uses `T=500`.

`observables.txt` is always written. `dynamic.txt` is generated only for the
18 characteristic animation runs because it is substantially larger.

The same actions are available as explicit commands:

```
py -3 simulation/main.py --help
py -3 simulation/main.py simulate -- --model both --rho 2,4,8 --eta 0:6:0.5 --T 500
py -3 simulation/main.py time-series --batch <batch> --compare
py -3 simulation/main.py polarization-vs-noise --batch <batch> --compare
py -3 simulation/main.py clusters --batch <batch> --compare
py -3 simulation/main.py polarization-vs-cluster --batch <batch> --compare
py -3 simulation/main.py animation --batch <batch> --run-dir <run> --format both
```

The old short names (`run`, `fig-b`, `fig-c`, `fig-d`, `fig-e`, `fig-g`,
`animate`) remain as aliases. On Linux/WSL, replace `py -3` with `python3`.

Maven is invoked as:

```
mvn -f experiment/pom.xml clean compile exec:java -Dexec.args=...
```

with an absolute `--out` under `output/simulation/<timestamp>/`.

The current CLI production sweep follows the three assignment densities
ρ=`2,4,8`, with `T=500`, η=`0:6:0.5`, five repeats and η_mid=`3.5`.
The stationary-state detector starts at `t=100` and compares windows of 100 samples.
`PLAN.md` retains the original calibration rationale for the longer run.
