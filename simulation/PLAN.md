# Python CLI — TP2 figures and animations

Launch from the repo root:

```
python simulation/main.py --help
```

or from this folder: `python main.py --help`.

On this Windows machine `python` is not on PATH; use `py -3`. Team target is Python ≥ 3.12.

Java writes text; this package only reads it (and can start Maven). Physics stay in `experiment/`.

Create a venv yourself, then `pip install -r requirements.txt`. Animations default
to GIF + MP4 (`--format gif|mp4|both`). Pillow writes GIF; `imageio-ffmpeg`
supplies the MP4 encoder, so no system FFmpeg is required.

## Layout

```
simulation/main.py     entry
simulation/src/        cli, paths, java, io, aggregate, plot, animate
output/                gitignored product tree
  simulation/<YYYY-MM-DD_HHMMSS>/   Java runs + cim_times_*.txt
  a_animaciones/<run_dir>/flock.{gif,mp4}
  b_evolucion_temporal/            one folder per assignment point (paths.POINT_FOLDERS)
  c_input_vs_observable/
  d_clusters/
  e_va_vs_S/
  f_comparacion_modelos/           the --compare overlays
  g_tiempos_cim/
  explore/<stamp>/                 make_batch kind, still timestamped
  data/s_axis_limits.txt
  data/cache/index.csv.gz
  data/cache/series/<batch>/<run_dir>.csv.gz   # t, va, S only
```

`src/paths.py` is the only module that knows that tree.

Java `--eta` / `--rho` / `--N` lists are `from:to:step` (`0:6:0.5`), not MATLAB `start:step:stop`. `src/java.py` expands those ranges to a comma list before Maven because `exec.args` on Windows splits on `:`.

## Production sweep (frozen 2026-08-27)

> **Registro historico.** Esta seccion documenta la calibracion del perfil con
> `T=10000`. El perfil que corre hoy vive en `src/cli.py` (`_production_args`) y
> usa `T=500` en dos tandas de densidades; ver `README.md`. La razon de fondo de
> la calibracion sigue valiendo y por eso se conserva.

Calibration (measured, not invented):

| run | wall-clock | result |
| --- | --- | --- |
| `vicsek --rho 4 --eta 2 --T 20000 --seed 1` (no `--dynamic`) | **22.9 s** (N=400) | `output/simulation/2026-08-27_233757/`. `va(0)=0.004`, first `va≥0.75` at **t=63**, `va(20000)=0.803`. Mean `va` on `t=200..700` vs last 500: 0.782 vs 0.787 (Δ=0.005). Detector `--window 200 --t-min 200` reports onset **t=200** (already flat; `t-min` clips). |
| η scout `vicsek --rho 4 --eta 0:6:0.5 --T 2000 --seed 1` | **27.5 s** for 13 runs | `output/simulation/2026-08-27_234116/`. `va_final`: 0→1.00, 0.5→0.99, 1→0.94, 1.5→0.87, 2→0.78, 2.5→0.66, **3→0.46**, **3.5→0.39**, **4→0.05**, 4.5→0.15, 5→0.05, 5.5→0.06, 6→0.01. Drop sits at **η≈3–4**. |

Frozen knobs:

- **T = 10000.** Ordered side flattens by t≈63. Do not lower T: the scout is one seed at T=2000; near η≈3.5 the series is still moving.
- **η = `0:6:0.5`** (13 points). Java `from:to:step`.
- **`--repeats 5`**, **`--seed 1`**. No `--dynamic` on the sweep.
- Densities `{1/π, 1/(2π), 1/(3π), 2, 4, 8}` ≈ `0.3183,0.1592,0.1061,2,4,8`.
- Detector (de aquella calibracion): `--window 200 --t-min 200 --sustain 3 --atol 0.02 --rtol 0.05`. Los defaults actuales son `--window 100 --t-min 100`, y `sustain` cambio de significado: ahora es la cantidad de tramos de confirmacion, no de ventanas corridas.
- **η_mid = 3.5** (talk catalog + `--eta-mid` default). 2.5 is still ordered at ρ=4 (`va≈0.66`).
- Talk videos: `T_anim = 2000`, `--stride 5`, `--dynamic`, seed 1.

Wall-clock: N=800 at T=10000 is ~23 s (same order as the T=20000 N=400 calibration). 780 flock runs ≈ **1.5–2 h**. Keep repeats=5; do not thin η.

Production command (quote the η range in PowerShell even though Python expands it):

```
python simulation/main.py run -- --model both --rho 0.3183,0.1592,0.1061,2,4,8 --eta 0:6:0.5 --T 10000 --repeats 5 --seed 1
```

780 flock runs (6 ρ × 13 η × 5 × 2 models). Talk animations are a separate 24-run `--dynamic` batch (`animate --talk`). CIM: `run -- --cim-benchmark`.

Do **not** launch this until the group is ready to leave the machine overnight. Calibration is done; the command is frozen, not started.

## Compliance

Status: CLI implemented. Sweep numbers frozen 2026-08-27. Production matrix not launched.

- **(a)** GIF and MP4 animations, arrows at positions, colored by velocity angle, both models. `python simulation/main.py animate --talk` → `output/a_animaciones/`. Catalog (24 runs, `animate.talk_catalog`): general ρ={2,4,8} × η∈{0.5, η_mid, 6} × both models, plus cluster ρ={1/π, 1/(2π), 1/(3π)} × η_mid × both models. Quiver length is display-only (`L*0.04`, direction kept); Java `v` is unchanged.
- **(b)** characteristic `va(t)` with onset lines. `fig-b --compare` → `output/b_evolucion_temporal/` (los overlays de `--compare` van a `output/f_comparacion_modelos/`). Calibration overlay: `fig-b --batch 2026-08-27_233757 --series va`.
- **(c)** `va` vs η with error bars, densities 2,4,8. `fig-c --compare`.
- **(d) S(t)** one curve per density (six ρ). `fig-d` time panel → `fig-d-S-t`. Vertical `t_onset_S` lines when status is in `aggregate.USABLE` (same rule as fig-b for `va`).
- **(d) S vs η** stationary mean ± SD. `fig-d` eta panel → `fig-d-S-eta`.
- **(d)/(e) cluster ρ** `plot.CLUSTER_RHOS` = the three low densities plus the three from the statement (six curves). Java folders are `rho0.32` / `0.16` / `0.11` (`N/L²`); `rho_close` aliases those to `1/π`, `1/(2π)`, `1/(3π)` and still matches fixture `rho0.3183`. With `rc=1` the ρ={2,4,8} curves sit at `S≈1` for every η — that flatness is a result, not a bug, but the low densities are what make (d) and (e) informative.
- **(e)** `va` vs `S`, densities distinguished, six ρ default. `fig-e --compare`.
- **(f)** voter repeats (a)–(e); overlay both models on (b)–(e) via `--compare`; talk catalog includes votante.
- **(g)** CIM times vs TP1. `run -- --cim-benchmark` then `fig-g --tp1 PATH`. Gap: no TP1 file in this repo.
- **General** animation + primary-observable time series per study: `animate --talk`, `fig-b`, `fig-d` time, `--compare`.
- **General** Java writes text; `animate` reads `dynamic.txt` independently.

## Cache

Only raw `(t, va, S)` plus an index. Onset and aggregation always recompute from the current flags.

## Tests

From `simulation/`: `python -m pytest`.
