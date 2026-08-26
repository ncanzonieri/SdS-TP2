# Plan de implementación — TP2 SdS: Vicsek / Votante (motor de simulación)

## Estado (actualizar al terminar cada paso)

- [x] Paso 1 — Modelo de datos y parametrización (compilado y verificado con smoke tests de CIM)
- [ ] Paso 2 — Motor de actualización (Vicsek + Votante, ruido, wrap-around)
- [ ] Paso 3 — Observables por paso: polarización `va(t)` y clusters `S(t)`
- [ ] Paso 4 — Persistencia: archivos de salida (estático / dinámico / observables)
- [ ] Paso 5 — CLI / configuración de corridas y barrido de η
- [ ] Paso 6 — Benchmark del CIM (punto g) + limpieza final y empaquetado

Cuando termines un paso: tildalo, hacé commit (mensaje `TP2 paso N: ...`), pusheá, y avisá al grupo. El siguiente en sentarse arranca leyendo el "Qué encontrás al llegar" del paso que sigue.

## Context

El TP2 pide implementar el algoritmo de bandadas de Vicsek (off-lattice) en una caja `L=10` con contorno periódico, para tres densidades `ρ = 2, 4, 8` (`N = 200, 400, 800`), comparando el modelo estándar (promedio de ángulos de vecinos) contra el modelo de votante (copia el ángulo de un vecino al azar), ambos con ruido `η`. Además hay que calcular y exportar dos observables por paso temporal — la polarización `va` y el tamaño relativo del cluster más grande `S` — y comparar los tiempos de ejecución del Cell Index Method (CIM) contra los medidos en el TP1.

Ya existe en `experiment/` (Java/Maven) un esqueleto reutilizable del TP1: `Particle` (id, x, y, angle), `Grid` (con un CIM funcional de vecinos con contorno periódico, aunque con `L` y `R` hardcodeados como `10`/`1.0`), un prototipo incompleto de `simulateTick()`/`viscek()` (sin ruido, sin wrap-around, velocidad hardcodeada en `10` en vez de `0.03`, sin variante votante), y un `CsvWriter` que solo escribe una foto estática. `Main.java` hoy solo genera partículas al azar y las vuelca a un CSV; nunca llama al loop de simulación. La carpeta `Contexto_Teorico/docs/` del repo ya tiene, en Markdown, el enunciado completo y las ecuaciones exactas (`Contexto_Teorico/docs/tp/TP2_Enunciado.md`, `Contexto_Teorico/docs/teoria/Teorica_2.md`, `Contexto_Teorico/docs/teoria/Teorica_1.md` para el CIM) — son la referencia normativa por sobre cualquier otra nota.

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

## Paso 2 — Motor de actualización (Vicsek + Votante, ruido, wrap-around)

**Objetivo:** implementar correctamente las dos reglas de actualización de ángulo con ruido, actualización de posición con wrap-around periódico, y un loop temporal síncrono (todas las partículas se actualizan a partir del mismo estado "congelado" del paso anterior, no en cascada).

**Qué hacer:**
- Reemplazar `viscek()` por dos métodos separados (o una estrategia `Model` que despache):
  - **Vicsek:** `θ(t+1) = atan2(⟨sin θ⟩r, ⟨cos θ⟩r) + R`, promedio incluyendo a la propia partícula (ya está bien encaminado en el código actual, salvo que hoy no suma el ruido).
  - **Votante:** elegir al azar (con el `Random` con semilla) una partícula del conjunto `{i} ∪ vecinos(i)` y copiar su ángulo, `θ(t+1) = θ_random + R`.
  - `R = U(-η/2, η/2)` en ambos casos (nuevo, hoy no existe ruido en el código).
- Actualización de posición: `x_i(t+1) = x_i(t) + v·cos(θ(t+1))`, `y_i(t+1) = y_i(t) + v·sin(θ(t+1))` (usar `v=0.03` de `SimulationParams`, no el `10` hardcodeado actual), con wrap-around: `x = ((x % L) + L) % L` (mismo criterio para `y`).
- **Sincronía:** calcular todos los `(θ_nuevo, x_nuevo, y_nuevo)` en un buffer a partir de los vecinos ya calculados al inicio del tick, y recién después mutar todas las partículas. El código actual muta en el mismo loop en que lee — funciona de casualidad para los ángulos (los vecinos se leyeron antes de mutar) pero es frágil; con el buffer queda correcto y explícito.
- Nueva clase (sugerido) `core/SimulationEngine.java` con un método `List<ParticleState> step(SimulationParams params)` o `void run(int T)` que hace: `nearestNeighbor()` → actualizar todas las partículas → (dejar un punto de extensión para que el Paso 3 enganche el cálculo de observables por tick, y el Paso 4 el guardado).

**Archivos:** `experiment/src/main/java/models/Grid.java` (o nueva `core/SimulationEngine.java` si se prefiere separar del CIM), reutiliza `SimulationParams` del Paso 1.

**Qué encontrás al llegar (para quien siga con el Paso 3):** un loop temporal que, dado `SimulationParams` con `model=VICSEK` o `VOTANTE`, hace evolucionar correctamente `N` partículas por `T` pasos, con ruido y contorno periódico. Se puede probar imprimiendo posiciones/ángulos por consola paso a paso todavía sin persistencia en archivo.

## Paso 3 — Observables por paso: polarización `va(t)` y clusters `S(t)`

**Objetivo:** en cada tick del loop, calcular los dos observables primarios pedidos por el enunciado (a) `va` y (d) `S`), usando la lista de vecinos que ya devuelve el CIM.

**Qué hacer:**
- `va(t) = |Σ_i (cos θ_i, sin θ_i)| / N` (el `v` de la fórmula del enunciado se cancela al ser constante — dejar un comentario aclarando la simplificación para que quien lea el informe no se confunda). Método simple, por ejemplo en una clase `analysis/OrderParameter.java` o como método estático.
- Clusters: usar Union-Find (Disjoint Set con path compression + union by rank) sobre los pares `(i,j)` que ya salen de `nearestNeighbor()` — por cada partícula `i` y cada vecino `j` en su lista, `union(i,j)`. Al final, tamaño del cluster más grande = el componente con más elementos; `S(t) = tamaño_max / N`. Clase sugerida `analysis/ClusterFinder.java` con método `double largestClusterFraction(Map<Particle,List<Particle>> neighbors, int N)`.
- Enganchar ambos cálculos en el loop del Paso 2: en cada tick, después de actualizar, calcular `va(t)` y `S(t)` y guardarlos en memoria (una lista/array por tick) — la escritura a archivo es el Paso 4, acá solo hace falta que el dato exista.

**Archivos:** nuevas `experiment/src/main/java/analysis/OrderParameter.java`, `experiment/src/main/java/analysis/ClusterFinder.java`; enganche en `core/SimulationEngine.java` (o `Grid.java`) del Paso 2.

**Qué encontrás al llegar (para quien siga con el Paso 4):** el loop de simulación ya produce, por cada tick, una tripla `(t, va, S)` además del estado de las partículas — solo falta persistirlo en disco con el formato correcto.

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
