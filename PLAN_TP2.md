# Plan de implementación — TP2 SdS: Vicsek / Votante (motor de simulación)

## Estado (actualizar al terminar cada paso)

- [x] Paso 1 — Modelo de datos y parametrización (compilado y verificado con smoke tests de CIM)
- [x] Paso 2 — Motor de actualización (Vicsek + Votante, ruido, wrap-around) (compilado y verificado con smoke tests de orden/desorden/consenso/wrap-around)
- [x] Paso 3 — Observables por paso: polarización `va(t)` y clusters `S(t)` (compilado y verificado con smoke tests de la serie temporal y del Union-Find sobre un grafo conocido)
- [x] Paso 4 — Persistencia: archivos de salida (estático / dinámico / observables)
- [x] Paso 5 — CLI / configuración de corridas y barrido de η
- [x] Paso 6 — Benchmark del CIM (punto g): `Main --cim-benchmark` escribe tiempos de `nearestNeighbor()` aislados de I/O
- [ ] Paso 7 - Animar, graficar y analizar para el informe y la presentación.
- [ ] Zip de entrega (`experiment/` sin `target/`, `.git`, `Contexto_Teorico/`, outputs)

Cuando termines un paso: tildalo, hacé commit (mensaje `TP2 paso N: ...`), pusheá, y avisá al grupo. El siguiente en sentarse arranca leyendo el "Qué encontrás al llegar" del paso que sigue.

## Context

El TP2 pide implementar el algoritmo de bandadas de Vicsek (off-lattice) en una caja `L=10` con contorno periódico, para tres densidades `ρ = 2, 4, 8` (`N = 200, 400, 800`), comparando el modelo estándar (promedio de ángulos de vecinos) contra el modelo de votante (copia el ángulo de un vecino al azar), ambos con ruido `η`. Además hay que calcular y exportar dos observables por paso temporal — la polarización `va` y el tamaño relativo del cluster más grande `S` — y comparar los tiempos de ejecución del Cell Index Method (CIM) contra los medidos en el TP1.

Ya existe en `experiment/` (Java/Maven) el motor de simulación: `Particle`, `Grid` (CIM con `M = floor(L/rc)` y wrap `% M`), `SimulationEngine` (Vicsek + votante), persistencia en `SimulationWriter`, CLI en `Main`/`RunConfig`, y `benchmark/CimBenchmark` (punto g). `Main` invoca el engine (Paso 5) y acepta `--cim-benchmark` (Paso 6). La carpeta `Contexto_Teorico/docs/` del repo ya tiene, en Markdown, el enunciado completo y las ecuaciones exactas (`Contexto_Teorico/docs/tp/TP2_Enunciado.md`, `Contexto_Teorico/docs/teoria/Teorica_2.md`, `Contexto_Teorico/docs/teoria/Teorica_1.md` para el CIM) — son la referencia normativa por sobre cualquier otra nota.

**Aclaración del profesor por mail (no está en el enunciado escrito, prevalece sobre él):** las densidades `ρ = 2, 4, 8` (`N = 200, 400, 800`) son para todo el estudio general (animaciones, `va` vs `η`, etc.). **Solo para el estudio de clusters** (punto d del enunciado: `S` vs tiempo y `S` vs `η`) hay que extender el barrido a tres densidades adicionales, más bajas: `ρ = 1/π, 1/(2π), 1/(3π)` → `N = 32, 16, 11` (con `L=10`, `N=ρ·L²`, redondeado). Estos son exactamente los valores que ya estaban anotados en el `README.md` del repo (N=11,16,32,200,400,800) — no era un borrador descartado, era esta extensión específica para clusters. El motor debe poder correr con cualquiera de las 6 densidades sin distinguir "modo cluster" a nivel de código — la distinción de qué densidades usar para qué estudio es una decisión de qué corridas lanzar, no del motor en sí.

Alcance de este plan: **únicamente el motor de simulación en Java** (`experiment/`) — nada de scripts de análisis/gráficos, presentación ni informe. El objetivo de cada paso es que el código funcione correctamente y sea reusable por el siguiente paso; no se prioriza estilo ni elegancia.

Decisiones ya tomadas (no reabrir sin razón):
- Lenguaje/stack: Java, extendiendo `experiment/` (Maven, Java 25).
- Densidades: `ρ = 2, 4, 8` (`N = 200, 400, 800`) para el estudio general; `ρ = 1/π, 1/(2π), 1/(3π)` (`N = 32, 16, 11`) agregadas **solo** para clusters (ver aclaración del profesor arriba). Todas con `L=10`.
- `v = 0.03` (constante), `rc = 1`, `dt = 1`, `η ∈ [0, 2π)` barrido por el usuario del motor.
- Reusar y extender el CIM existente en `Grid.java`, no reescribirlo desde cero.

## Paso 1 — Modelo de datos y parametrización ✅ IMPLEMENTADO

**Objetivo:** dejar los tipos base configurables (nada de constantes hardcodeadas de `L`, `R`, velocidad) para que los pasos siguientes puedan construir el loop de simulación sobre una base estable.

**Qué se hizo:**
- `models/Particle.java`: se agregó `hashCode()` consistente con el `equals()` actual (antes solo comparaba `id` y se usaba como key de `HashMap`/`HashSet` en `Grid` sin `hashCode()` — bug latente corregido). Se agregaron helpers `vx(v)`/`vy(v)` para la velocidad vectorial (dado el módulo constante `v`, que vive en `SimulationParams`, no en cada partícula).
- Nueva clase `models/SimulationParams.java`: agrupa `N`, `L`, `rc`, `v`, `eta`, `T` (pasos de tiempo), `seed`, y un enum `Model { VICSEK, VOTANTE }`, más un factory `nFromDensity(rho, L)` para las 6 densidades del TP. Este objeto viaja por todo el motor en vez de constantes sueltas.
- `models/Grid.java`: los `static final` de `L`/`R` pasaron a ser campos de instancia recibidos vía `SimulationParams` en el constructor. Se eliminó el campo `matrix` (grilla unitaria de TP1, código muerto que no se usaba en `nearestNeighbor()`). El commit de Paso 1 *afirmó* `M = floor(L/rc)`, pero el wrap de celdas siguió usando `% L` e índice `x/R` (correcto solo si `rc=1`). Eso se corrigió después: `M = max(1, floor(L/rc))`, `cellSize = L/M`, bin `floor(x/cellSize)` clamp a `[0,M)`, wrap de vecinos con `% M`. El CIM vale para cualquier `rc` (Paso 6, geometría TP1 `L=20`).
- `Random` centralizado como campo de `Grid`, sembrado con `params.getSeed()` (runs reproducibles).
- `Main.java`: cambio mínimo para compilar contra el nuevo constructor de `Grid` (arma un `SimulationParams` con los valores que antes estaban hardcodeados). **No** se tocó el resto de `Main` ni `simulateTick()`/`viscek()` — eso es Paso 2/5.

**Verificado:** `mvn compile` limpio; `Main 10` genera el mismo `static.csv` de siempre (sin cambio de comportamiento); test manual del CIM con posiciones conocidas confirmando vecinos correctos con contorno periódico, incluyendo el caso `rc≠1` que antes rompía.

**Qué encontrás al llegar (para quien siga con el Paso 2):** `Grid` construible con cualquier `L`/`rc`/semilla, `nearestNeighbor()` sigue devolviendo `Map<Particle,List<Particle>>` con vecinos correctos, `Particle` usable de forma segura en `HashMap`/`HashSet`.

## Paso 2 — Motor de actualización (Vicsek + Votante, ruido, wrap-around) ✅ IMPLEMENTADO

**Objetivo:** implementar correctamente las dos reglas de actualización de ángulo con ruido, actualización de posición con wrap-around periódico, y un loop temporal síncrono (todas las partículas se actualizan a partir del mismo estado "congelado" del paso anterior, no en cascada).

**Qué se hizo:**
- Nueva clase `core/SimulationEngine.java`, con `step()` (un tick) y `run(steps)` (loop de `steps` ticks). Reemplaza por completo el prototipo `viscek()`/`simulateTick()` que tenía `Grid` (eliminado — Grid vuelve a ocuparse solo del modelo de datos y el CIM).
- **Vicsek:** `θ(t+1) = atan2(⟨sin θ⟩r, ⟨cos θ⟩r) + R`, promedio incluyendo a la propia partícula.
- **Votante:** copia el ángulo de un vecino al azar **distinto de sí misma** (el CIM no incluye self). Si no hay vecinos, se queda con el ángulo propio y después se suma el ruido. (El texto viejo de este plan que sorteaba en `{i} ∪ vecinos(i)` no es la regla del enunciado ni de Loscar; el código nunca lo hizo así.)
- `R = U(-η/2, η/2)` sumado en ambos casos (antes no existía ruido en el código).
- Posición: `x_i(t+1) = x_i(t) + v·cos(θ(t+1))`, igual para `y`, usando `v` de `SimulationParams` (ya no el `10` hardcodeado), con wrap-around `x % L` corrigiendo negativos.
- **Sincronía:** `step()` primero calcula todos los ángulos nuevos en un array (`newAngles`, usando el estado congelado del tick anterior) y recién después muta posiciones/ángulos — ya no hay riesgo de que una partícula lea el ángulo ya actualizado de otra en el mismo tick.
- `Grid` expone `getRandom()` para que el engine reutilice el mismo `Random` sembrado (mismo criterio de reproducibilidad del Paso 1) para el ruido y el sorteo del votante, en vez de crear un segundo `Random` desincronizado.

**Verificado (`mvn compile` limpio + smoke tests manuales, no versionados):**
- Vicsek con `η=0`: `va` pasa de ~0.03 (inicio aleatorio) a ~0.998 tras 200 pasos (orden emergente correcto).
- Vicsek con `η=2π` (ruido máximo): `va` se mantiene bajo (~0.05) tras 200 pasos (desorden correcto).
- Votante con `η=0` y ángulo inicial idéntico en todas las partículas: `va=1.000000` exacto (consenso trivial correcto).
- Wrap-around: partícula en `x=9.99` moviéndose en `+x` con `v=0.03` reaparece en `x≈0.02` (contorno periódico correcto).

**Qué encontrás al llegar (para quien siga con el Paso 3):** `SimulationEngine(grid, params).run(T)` hace evolucionar correctamente `N` partículas por `T` pasos con el modelo elegido, ruido y contorno periódico. `step()` registra observables y, si hay writer, persiste el frame. `Main` ya invoca el engine (Paso 5).

## Paso 3 — Observables por paso: polarización `va(t)` y clusters `S(t)` ✅ IMPLEMENTADO

**Objetivo:** en cada tick del loop, calcular los dos observables primarios pedidos por el enunciado (a) `va` y (d) `S`), usando la lista de vecinos que ya devuelve el CIM.

**Qué se hizo:**
- Nueva clase `analysis/OrderParameter.java`: `polarization(particles)` calcula `va = |Σ_i (cos θ_i, sin θ_i)| / N` (el `v` de la fórmula del enunciado se cancela al ser constante — queda comentado en el código).
- Nueva clase `analysis/ClusterFinder.java`: `largestClusterFraction(neighbors, particles)` con Union-Find (Disjoint Set, path compression + union by rank) sobre el mapa de vecinos que devuelve `Grid.nearestNeighbor()` — `union(i,j)` por cada par vecino, y al final `S = tamaño del componente más grande / N`. (Firma final recibe `List<Particle>` en vez de solo `int N` porque hace falta la lista para indexar el mapa de vecinos.)
- Nuevo `core/ObservableSample.java` (record `t, va, s`) — una muestra de la serie temporal.
- `core/SimulationEngine.java`: `step()` ahora registra `(t, va, S)` del estado **antes de mover a nadie**, reusando el mismo mapa de vecinos que ya calculaba para la regla de actualización (no se duplica la búsqueda del CIM en cada tick). `run(steps)` corre `steps` pasos y además registra el estado final (`t == steps`) con una búsqueda de vecinos extra al final — así la serie queda completa con `T+1` muestras (`t=0` inicial incluido) sin pagar el costo de una búsqueda doble en cada tick intermedio. Nuevo método público `sampleObservables()` para registrar el estado actual sin avanzar el tiempo (usado internamente por `run()`, disponible también si alguien quiere una muestra puntual). Nuevo getter `getObservables()` devuelve la lista acumulada.

**Verificado (`mvn compile` limpio + smoke tests manuales, no versionados):**
- `run(30)` genera exactamente 31 muestras (`T+1`).
- Densidad alta (`ρ=8`, `N=800`): `S≈1.000` casi desde el arranque (esperable, muy por encima del umbral de percolación con `rc=1`); `va` sube de 0.05 a 0.63 en 30 pasos (todavía convergiendo, consistente).
- Densidad baja del estudio de clusters (`ρ=1/(3π)`, `N=11`): `S` inicial bajo (0.18 ≈ 2/11), consistente con partículas dispersas.
- `ClusterFinder` contra un grafo de vecinos armado a mano (cadena de 3 + 1 aislada): `S=0.75` exacto, como corresponde.

**Archivos:** `experiment/src/main/java/analysis/OrderParameter.java`, `experiment/src/main/java/analysis/ClusterFinder.java`, `experiment/src/main/java/core/ObservableSample.java`, `experiment/src/main/java/core/SimulationEngine.java` (modificado).

**Qué encontrás al llegar (para quien siga con el Paso 4):** `engine.run(T)` (o `step()` en loop propio) ya deja en `engine.getObservables()` la serie completa `(t, va, S)` además del estado de las partículas — solo falta persistir todo esto (posiciones/velocidades y la serie de observables) en disco con el formato correcto.

## Paso 4 — Persistencia: archivos de salida (estático / dinámico / observables) ✅ IMPLEMENTADO

**Objetivo:** que el motor escriba en disco, en el formato de cátedra (`Contexto_Teorico/docs/teoria/Teorica_1.md`), los archivos que después va a consumir el módulo de animación (independiente, fuera de este alcance) y los que se van a graficar para los observables.

**Qué se hizo:** `utils/SimulationWriter.java` (reemplaza `CsvWriter`) escribe en `outputDir`:
- `static.txt`: solo `N` luego `L` (sin radio/color ni extra params que un parser de cátedra leería como propiedades de partícula).
- `dynamic.txt` (si `writeDynamic`): bloques `t` + `x y vx vy` por partícula, `vx=v·cosθ`, `vy=v·sinθ`, `Locale.ROOT`.
- `observables.txt`: `# t va S` y una línea `t va S` por muestra.
`SimulationEngine` vuelca frame + observables en cada `recordObservables` (incluye `t=0` y el estado final de `run()`). `Main` pasa `--dynamic` para generar `dynamic.txt`; por defecto solo static+observables.

## Paso 5 — CLI / configuración de corridas y barrido de η ✅ IMPLEMENTADO

**Objetivo:** que `Main.java` permita elegir densidad (`ρ`→`N`), `η`, modelo (Vicsek/Votante), `T`, semilla y carpeta de salida sin tocar código, y facilitar correr varias corridas (barrido de `η`) en una sola invocación.

**Qué se hizo:** `cli/RunConfig.java` parsea `--model/--rho/--N/--eta/--T/--repeats/--seed/--out/--dynamic/--L/--v/--rc`. Listas por coma o rango `desde:hasta:paso`. Producto cartesiano modelo×densidad×eta×repetición; carpeta `out/{model}_rho{ρ}_eta{η}_T{T}_seed{seed}[_r{k}]`. `--help` imprime `USAGE`. `mvn -f experiment/pom.xml exec:java -Dexec.args="..."`.

## Paso 6 — Benchmark del CIM (punto g) ✅ IMPLEMENTADO (zip pendiente)

**Objetivo:** cubrir el punto (g) del enunciado (medir tiempos de ejecución del CIM y dejarlos listos para comparar con el TP1) y dejar el código en condiciones de entregar (sin restos de debug, buildable, empaquetable en el zip pedido).

**Qué se hizo:** `benchmark/CimBenchmark.java` + `Main --cim-benchmark`. Solo `nearestNeighbor()` (`System.nanoTime()`), sin writer. Defaults `L=20`, `rc=1`, ≥10 valores de N, 200 reps tras warmup. Dos series: `cim_times_L20.txt` (L fijo) y `cim_times_rho_fixed.txt` (ρ fijo, L crece con N). `pom.xml` tiene `exec-maven-plugin` (`mainClass` Main).

**Pendiente (fuera de este pass):** zip de entrega — solo `experiment/` fuente, sin `target/`, outputs, `.git`, `Contexto_Teorico/`.

## Pas0 7 - Animar, analizar y graficar

Básicamente, los ítems de la consigna.

a) Videos representativos de muestra donde las partículas son vectores y se colorean según el ángulo.

b) Gráficos representativos de polarización en tiempo para demostrar dónde trazamos la vertical del instante en que llega a un equilibrio.

c) Después de tener varias pasadas por cada combinación ruido-densidad, graficar polarización según ruido incluyendo barra de error por cada densidad.

d) Mismo que b y c con S.

e) Comparar tiempos con el TP1 (campo 10x10, ajustar N de manera que mantenga la densidad original usada en el TP1)

## Verificación end-to-end (para cualquiera que retome el trabajo)

1. `mvn -f experiment/pom.xml compile` compila sin errores.
2. Correr una simulación corta (`T` chico, ej. 50) para cada combinación de `model ∈ {vicsek, votante}` y al menos una densidad alta (`ρ=2,4,8`, N=200/400/800) y una densidad baja del estudio de clusters (`ρ=1/(3π)`, N=11 — el caso más chico, buen smoke test rápido), y confirmar que:
   - Los 3 archivos de salida (estático, dinámico, observables) se generan y tienen el formato esperado.
   - `va` queda en `[0,1]` en todo momento; con `η=0` y suficientes pasos, `va` tiende a 1 (orden total) y con `η` alto tiende a valores bajos.
   - `S` queda en `(0,1]`; con `η=0` el cluster más grande debería terminar ocupando prácticamente todas las partículas (`S≈1`).
   - Las posiciones nunca quedan fuera de `[0, L)` (wrap-around correcto).
3. Correr el benchmark del CIM para un par de valores de `N` y confirmar que el tiempo crece de forma razonable (no cuadrática) al aumentar `N` a densidad constante.
4. Confirmar que `Main` puede invocarse con distintos parámetros sin tocar código fuente (barrido de `η` genera una carpeta por corrida, sin pisar archivos).
