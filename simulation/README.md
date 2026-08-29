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

1. **Generate data.** Choose the frozen production sweep, the 24 animation runs,
   the CIM benchmark, or a custom simulation. Each result is stored as a
   timestamped batch under `output/simulation/`.
2. **Generate results from existing data.** Select any combination of animations,
   figures b–e, the Vicsek/Voter comparison, the HTML explorer, and the CIM
   comparison. This stage never reruns the physical simulation.
3. **Do the complete assignment (a–g).** Choose whether to reuse three existing
   batches (observables, animations, and CIM) or create everything from scratch.
   Starting from scratch requires confirmation because the frozen sweep is
   780 runs and takes approximately 1.5–2 hours.

`observables.txt` is always written. `dynamic.txt` is generated only for the
24 characteristic animation runs because it is substantially larger.

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
mvn -f experiment/pom.xml exec:java -Dexec.args=...
```

with an absolute `--out` under `output/simulation/<timestamp>/`.

See `PLAN.md` for the frozen production sweep (T=10000, η=0:6:0.5, repeats=5, η_mid=3.5) and the assignment compliance list.
