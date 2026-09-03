# Tiempos del TP1 (punto g)

El punto (g) del TP2 pide comparar los tiempos de ejecución del Cell Index
Method con los medidos en el TP1. Esta carpeta es la única fuente de esos
números: la figura `output/g_tiempos_cim/g_cim_times.png` los lee de acá.

## Qué completar

Editar `cim_times_tp1.csv` (una fila por valor de `N`):

| columna    | significado                                                              |
| ---------- | ------------------------------------------------------------------------ |
| `serie`    | etiqueta de la curva, p. ej. `L=20 fijo` (punto 4.1) o `rho fija` (4.2)  |
| `N`        | cantidad de partículas                                                   |
| `L`        | lado de la caja de esa medición                                          |
| `M`        | celdas por lado (el `M` óptimo encontrado en el TP1)                     |
| `mean_ms`  | tiempo medio de **una** búsqueda de vecinos, en ms                       |
| `stdev_ms` | desvío estándar de ese tiempo, en ms (se dibuja como barra de error)     |

Las líneas que empiezan con `#` se ignoran. Mientras el archivo no tenga
filas de datos, la figura (g) muestra solo las curvas del TP2 y avisa por
consola.

## De dónde salieron los números cargados

`cim_times_tp1.csv` ya está completo con las corridas del TP1 del 2026-08-10
(carpeta `TP-1-SdS/simulation/outputs`, copia en `tmp/` de este repo):

| serie           | archivo del TP1                                                                      | punto TP1 |
| --------------- | ------------------------------------------------------------------------------------ | --------- |
| `L=20 fijo`     | `sweep_vary_n/L20_M13_rc1_wrap_N10-1000_20260810_182324/timing_summary.csv`          | 4.1       |
| `rho=0.25 fija` | `sweep_fixed_density/rho0.25_M13_rc1_wrap_N100-1000_20260810_182502/timing_summary.csv` | 4.2    |

Condiciones del TP1: `rc=1`, `M=13` (óptimo del punto 3), contorno periódico,
partículas con radio `r_i ~ U[0.23, 0.26]` y distancia borde a borde, 100
repeticiones tras 20 de calentamiento. `mean_ms`/`stdev_ms` son
`mean_elapsed_ns`/`std_elapsed_ns` pasados a ms.

Diferencias con el TP2 que hay que decir al comparar: el TP2 usa partículas
puntuales y `M = floor(L/rc) = 20` (el TP1 necesitaba `L/M > rc + 2·r_max`, de
ahí `M=13`); el TP2 mide 1000 repeticiones. Para que la serie de densidad fija
sea comparable, el benchmark del TP2 se corre con los mismos `N` y `rho=0.25`:

```
java -cp experiment/target/classes Main --cim-benchmark \
     --N 10,20,40,60,80,100,150,200,300,500,1000 --rho 0.25 --repeats 1000 --out <lote>
```

## Cómo se usa

```
python simulation/main.py cim-comparison --batch <lote con cim_times_*.txt>
```

Si el CSV tiene datos se carga solo; `--tp1 <otro.csv>` lo pisa. El TP2 mide
lo mismo (`Grid.nearestNeighbor()` aislado, `L=20`, `rc=1`, 200 repeticiones
tras 20 de calentamiento), así que las curvas son comparables punto a punto
mientras los `N` coincidan.
