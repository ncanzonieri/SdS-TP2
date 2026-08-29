# simulation — TP2 plots and animations

Java engine: `experiment/` (Maven). This folder only starts that engine and reads its text files.

## Setup

Python 3.12+. ffmpeg on PATH for MP4 export.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Launch

From the repo root:

```
python simulation/main.py --help
python simulation/main.py run -- --model vicsek --rho 4 --eta 0.5 --T 500 --dynamic
python simulation/main.py ingest
python simulation/main.py fig-c --compare
python simulation/main.py animate --talk
```

Maven is invoked as:

```
mvn -f experiment/pom.xml exec:java -Dexec.args=...
```

with an absolute `--out` under `output/simulation/<timestamp>/`.

See `PLAN.md` for the frozen production sweep (T=10000, η=0:6:0.5, repeats=5, η_mid=3.5) and the assignment compliance list.
