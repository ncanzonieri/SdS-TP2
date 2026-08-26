# Plan de implementación — TP2 SdS: Vicsek / Votante (motor de simulación)

## Estado (actualizar al terminar cada paso)

- [x] Paso 1 — Modelo de datos y parametrización (compilado y verificado con smoke tests de CIM)
- [x] Paso 2 — Motor de actualización (Vicsek + Votante, ruido, wrap-around) (compilado y verificado con smoke tests de orden/desorden/consenso/wrap-around)
- [x] Paso 3 — Observables por paso: polarización `va(t)` y clusters `S(t)` (compilado y verificado con smoke tests de la serie temporal y del Union-Find sobre un grafo conocido)
- [ ] Paso 3 — Observables por paso: polarización `va(t)` y clusters `S(t)`
- [ ] Paso 4 — Persistencia: archivos de salida (estático / dinámico / observables)
- [ ] Paso 5 — CLI / configuración de corridas y barrido de η
- [ ] Paso 6 — Benchmark del CIM (punto g) + limpieza final y empaquetado

Cuando termines un paso: tildalo, hacé commit (mensaje `TP2 paso N: ...`), pusheá, y avisá al grupo. El siguiente en sentarse arranca leyendo el "Qué encontrás al llegar" del paso que sigue.

## Context

El TP2 pide implementar el algoritmo de bandadas de Vicsek (off-lattice) en una caja `L=10` con contorno periódico, para tres densidades `ρ = 2, 4, 8` (`N = 200, 400, 800`), comparando el modelo estándar (promedio de ángulos de vecinos) contra el modelo de votante (copia el ángulo de un vecino al azar), ambos con ruido `η`. Además hay que calcular y exportar dos observables por paso temporal — la polarización `va` y el tamaño relativo del cluster más grande `S` — y comparar los tiempos de ejecución del Cell Index Method (CIM) contra los medidos en el TP1.

Ya existe en `experiment/` (Java/Maven) un esqueleto reutilizable del TP1: `Particle` (id, x, y, angle), `Grid` (con un CIM funcional de vecinos con contorno periódico, aunque originalmente con `L` y `R` hardcodeados como `10`/`1.0`), un prototipo incompleto original de `simulateTick()`/`viscek()` (sin ruido, sin wrap-around, velocidad hardcodeada en `10` en vez de `0.03`, sin variante votante — **ya reemplazado por `core/SimulationEngine.java` en el Paso 2**, ver más abajo), y un `CsvWriter` que solo escribe una foto estática. `Main.java` hoy solo genera partículas al azar y las vuelca a un CSV; todavía no invoca el loop de simulación (`SimulationEngine`) — eso es Paso 5. La carpeta `Contexto_Teorico/docs/` del repo ya tiene, en Markdown, el enunciado completo y las ecuaciones exactas (`Contexto_Teorico/docs/tp/TP2_Enunciado.md`, `Contexto_Teorico/docs/teoria/Teorica_2.md`, `Contexto_Teorico/docs/teoria/Teorica_1.md` para el CIM) — son la referencia normativa por sobre cualquier otra nota.

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
- `models/Grid.java`: los `static final` de `L`/`R` pasaron a ser campos de instancia recibidos vía `SimulationParams` en el constructor. Se eliminó el campo `matrix` (grilla unitaria de TP1, código muerto que no se usaba en `nearestNeighbor()`). De paso se corrigió un bug latente: el cálculo de celdas del CIM asumía `M == L` (válido solo si `rc==1`); ahora calcula `M = floor(L/rc)` y `cellSize = L/M` correctamente, así que el CIM sigue siendo válido con cualquier `rc` (relevante para el benchmark del Paso 6, que compara contra TP1 con `L=20`).
- `Random` centralizado como campo de `Grid`, sembrado con `params.getSeed()` (runs reproducibles).
- `Main.java`: cambio mínimo para compilar contra el nuevo constructor de `Grid` (arma un `SimulationParams` con los valores que antes estaban hardcodeados). **No** se tocó el resto de `Main` ni `simulateTick()`/`viscek()` — eso es Paso 2/5.

**Verificado:** `mvn compile` limpio; `Main 10` genera el mismo `static.csv` de siempre (sin cambio de comportamiento); test manual del CIM con posiciones conocidas confirmando vecinos correctos con contorno periódico, incluyendo el caso `rc≠1` que antes rompía.

**Qué encontrás al llegar (para quien siga con el Paso 2):** `Grid` construible con cualquier `L`/`rc`/semilla, `nearestNeighbor()` sigue devolviendo `Map<Particle,List<Particle>>` con vecinos correctos, `Particle` usable de forma segura en `HashMap`/`HashSet`.

## Paso 2 — Motor de actualización (Vicsek + Votante, ruido, wrap-around) ✅ IMPLEMENTADO

**Objetivo:** implementar correctamente las dos reglas de actualización de ángulo con ruido, actualización de posición con wrap-around periódico, y un loop temporal síncrono (todas las partículas se actualizan a partir del mismo estado "congelado" del paso anterior, no en cascada).

**Qué se hizo:**
- Nueva clase `core/SimulationEngine.java`, con `step()` (un tick) y `run(steps)` (loop de `steps` ticks). Reemplaza por completo el prototipo `viscek()`/`simulateTick()` que tenía `Grid` (eliminado — Grid vuelve a ocuparse solo del modelo de datos y el CIM).
- **Vicsek:** `θ(t+1) = atan2(⟨sin θ⟩r, ⟨cos θ⟩r) + R`, promedio incluyendo a la propia partícula.
- **Votante:** se sortea un índice uniforme en `{i} ∪ vecinos(i)` (tamaño `neighbors.size()+1`) y se copia ese ángulo; si sale el último índice, se queda con el propio.
- `R = U(-η/2, η/2)` sumado en ambos casos (antes no existía ruido en el código).
- Posición: `x_i(t+1) = x_i(t) + v·cos(θ(t+1))`, igual para `y`, usando `v` de `SimulationParams` (ya no el `10` hardcodeado), con wrap-around `x % L` corrigiendo negativos.
- **Sincronía:** `step()` primero calcula todos los ángulos nuevos en un array (`newAngles`, usando el estado congelado del tick anterior) y recién después muta posiciones/ángulos — ya no hay riesgo de que una partícula lea el ángulo ya actualizado de otra en el mismo tick.
- `Grid` expone `getRandom()` para que el engine reutilice el mismo `Random` sembrado (mismo criterio de reproducibilidad del Paso 1) para el ruido y el sorteo del votante, en vez de crear un segundo `Random` desincronizado.

**Verificado (`mvn compile` limpio + smoke tests manuales, no versionados):**
- Vicsek con `η=0`: `va` pasa de ~0.03 (inicio aleatorio) a ~0.998 tras 200 pasos (orden emergente correcto).
- Vicsek con `η=2π` (ruido máximo): `va` se mantiene bajo (~0.05) tras 200 pasos (desorden correcto).
- Votante con `η=0` y ángulo inicial idéntico en todas las partículas: `va=1.000000` exacto (consenso trivial correcto).
- Wrap-around: partícula en `x=9.99` moviéndose en `+x` con `v=0.03` reaparece en `x≈0.02` (contorno periódico correcto).

**Qué encontrás al llegar (para quien siga con el Paso 3):** `SimulationEngine(grid, params).run(T)` hace evolucionar correctamente `N` partículas por `T` pasos con el modelo elegido, ruido y contorno periódico. `step()` está pensado para llamarse desde un loop externo y engancharle el cálculo de observables (Paso 3) y la persistencia (Paso 4) después de cada tick — hoy no hace ninguna de las dos cosas todavía. `Main.java` sigue sin invocar el engine (eso es Paso 5).

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

## Paso 4 — Persistencia: archivos de salida (estático / dinámico / observables)

**Objetivo:** que el motor escriba en disco, en el formato de cátedra (`Contexto_Teorico/docs/teoria/Teorica_1.md`), los archivos que después va a consumir el módulo de animación (independiente, fuera de este alcance) y los que se van a graficar para los observables.

**Qué hacer:**
- Extender `utils/CsvWriter.java` (o dividir en clases más chicas si se prefiere) con:
  - **Archivo estático** (una vez por corrida): `N`, `L` (no hace falta radio/color por partícula — son puntuales y se colorean por ángulo, que es dinámico).
  - **Archivo dinámico** (una vez por tick, append o un archivo por tick a elección — el enunciado acepta ambos formatos, ver `Contexto_Teorico/docs/tp/TP1_Enunciado.md` punto 5): por cada partícula, `x y vx vy` (con `vx = v·cos θ`, `vy = v·sin θ`), precedido por una línea de encabezado con el tiempo `t`.
  - **Archivo de observables:** una línea por tick, `t va S`.
- Definir nombres/ubicación de archivos de salida de forma que no se pisen entre corridas distintas (esto se termina de resolver con el esquema de parámetros del Paso 5, pero dejar la firma del writer ya pensada para recibir una carpeta/prefijo de salida como parámetro).
- Enganchar esta escritura al loop del Paso 2/3: al final de cada tick, volcar el frame dinámico y la línea de observables; al principio de la corrida, volcar el estático.

**Archivos:** `experiment/src/main/java/utils/CsvWriter.java` (extender), enganche en `core/SimulationEngine.java`.

**Qué encontrás al llegar (para quien siga con el Paso 5):** correr una simulación de punta a punta (con parámetros todavía hardcodeados en el código) ya genera en disco los 3 archivos de texto plano completos y con el formato correcto — falta exponer los parámetros desde afuera.

## Paso 5 — CLI / configuración de corridas y barrido de η

**Objetivo:** que `Main.java` permita elegir densidad (`ρ`→`N`), `η`, modelo (Vicsek/Votante), `T`, semilla y carpeta de salida sin tocar código, y facilitar correr varias corridas (barrido de `η`) en una sola invocación.

**Qué hacer:**
- `Main.java`: reemplazar el `args[0]` único actual por parseo de argumentos con nombre (o un archivo de config simple tipo `.properties`/`.txt` — lo que sea más simple de mantener) que arme un `SimulationParams` completo: `rho` (o `N` directo — debe aceptar tanto las densidades altas `2,4,8` como las bajas `1/π, 1/(2π), 1/(3π)` del estudio de clusters, sin tratamiento especial de código para ninguna), `L=10` fijo, `v=0.03` fijo, `rc=1` fijo, `eta`, `model`, `T`, `seed`, carpeta/prefijo de salida.
- Soporte para barrido: aceptar una lista de valores de `η` (separados por coma, o un rango `desde:hasta:paso`) y, opcionalmente, una lista de valores de `ρ`/`N`, y correr una simulación completa por cada combinación, cada una con su propia carpeta/prefijo de salida derivado de los parámetros (ej. `out/vicsek_rho2_eta0.50/`, `out/vicsek_rho0.3183_eta0.50/`).
- Dejar un modo de ejecución "una corrida" simple (para debug rápido) y un modo "barrido" (para generar todos los datos que van a necesitar los gráficos, aunque los gráficos en sí no son parte de este plan).

**Archivos:** `experiment/src/main/java/Main.java` (reescribir), eventualmente nueva clase `cli/RunConfig.java` si el parseo se pone largo.

**Qué encontrás al llegar (para quien siga con el Paso 6):** se puede invocar el jar/clase `Main` con parámetros reales (ej. `mvn compile exec:java -Dexec.args="--rho 4 --eta 0.1,0.5,1.0,2.0 --model vicsek --T 500"`) y obtener carpetas de salida con los 3 archivos por cada combinación.

## Paso 6 — Benchmark del CIM (punto g) + limpieza final y empaquetado

**Objetivo:** cubrir el punto (g) del enunciado (medir tiempos de ejecución del CIM y dejarlos listos para comparar con el TP1) y dejar el código en condiciones de entregar (sin restos de debug, buildable, empaquetable en el zip pedido).

**Qué hacer:**
- Instrumentar el llamado a `nearestNeighbor()` con timing (`System.nanoTime()`), aislado de la escritura a disco (medir solo la búsqueda de vecinos, no I/O). Agregar un modo de ejecución (flag en `Main` o clase separada `benchmark/CimBenchmark.java`) que corra el CIM repetidas veces para valores de `N` similares a los usados en el TP1 (ver `Contexto_Teorico/docs/tp/TP1_Enunciado.md`, punto 4: al menos 10 valores de `N` entre 10 y el máximo posible) y vuelque `N, tiempo_promedio, desvío` a un archivo de texto — mismo formato que usaron para no tener que rehacer el análisis comparativo a mano.
- Limpieza final: repasar que no quede código muerto (verificar que no reaparecieron restos del `matrix` eliminado en el Paso 1), que `Particle.equals`/`hashCode` sigan consistentes, que `pom.xml` compile y corra (`mvn compile exec:java`) sin dependencias faltantes, y que no haya prints de debug olvidados.
- Preparar el *.zip de entrega: solo el código fuente final del motor (`experiment/`), sin `target/`, sin outputs de simulaciones, sin `.git`, sin `Contexto_Teorico/`.

**Archivos:** nueva `experiment/src/main/java/benchmark/CimBenchmark.java` (o método adicional en `Main`), revisión general de todo `experiment/src`.

## Verificación end-to-end (para cualquiera que retome el trabajo)

1. `mvn -f experiment/pom.xml compile` compila sin errores.
2. Correr una simulación corta (`T` chico, ej. 50) para cada combinación de `model ∈ {vicsek, votante}` y al menos una densidad alta (`ρ=2,4,8`, N=200/400/800) y una densidad baja del estudio de clusters (`ρ=1/(3π)`, N=11 — el caso más chico, buen smoke test rápido), y confirmar que:
   - Los 3 archivos de salida (estático, dinámico, observables) se generan y tienen el formato esperado.
   - `va` queda en `[0,1]` en todo momento; con `η=0` y suficientes pasos, `va` tiende a 1 (orden total) y con `η` alto tiende a valores bajos.
   - `S` queda en `(0,1]`; con `η=0` el cluster más grande debería terminar ocupando prácticamente todas las partículas (`S≈1`).
   - Las posiciones nunca quedan fuera de `[0, L)` (wrap-around correcto).
3. Correr el benchmark del CIM para un par de valores de `N` y confirmar que el tiempo crece de forma razonable (no cuadrática) al aumentar `N` a densidad constante.
4. Confirmar que `Main` puede invocarse con distintos parámetros sin tocar código fuente (barrido de `η` genera una carpeta por corrida, sin pisar archivos).
