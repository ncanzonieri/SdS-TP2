# Novel Type of Phase Transition in a System of Self-Driven Particles (Vicsek et al., 1995)

*Fuente original: `NovelTypePhaseTransition2.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: este archivo contiene un resumen y extractos, no la transcripción literal completa del paper (por derechos de autor); para el texto íntegro consultar el PDF original en el Proyecto.*

## 1. Motivación y planteo del problema (resumen del abstract/introducción)

Los autores proponen un modelo minimalista de "partículas autopropulsadas" (self-driven particles) inspirado en sistemas biológicos con interacción de alineación (bandadas de pájaros, cardúmenes de peces, manadas, colonias bacterianas). La idea central: cada partícula se mueve con **rapidez constante** y en cada paso de tiempo adopta la **dirección promedio** de las partículas vecinas dentro de un radio de interacción, más una perturbación aleatoria (ruido). A diferencia de los sistemas de equilibrio (tipo ferromagnético/XY), acá el momento total **no se conserva**, porque el mecanismo que fija la rapidez de cada partícula es una regla dinámica, no una colisión conservativa.

El resultado principal: el sistema exhibe una **transición de fase cinética** entre una fase desordenada (velocidad media del sistema ≈ 0, direcciones aleatorias) y una fase ordenada (velocidad media macroscópica finita, con simetría rotacional espontáneamente rota), al variar el nivel de ruido η y la densidad de partículas ρ. Los autores muestran evidencia numérica de que esta transición es continua (segundo orden), análoga a una transición de fase de equilibrio, con un parámetro de orden que se anula como una ley de potencias en (η_c − η) y en (ρ − ρ_c).

La analogía que proponen: el ruido η juega el rol de la "temperatura", la densidad ρ el rol de la densidad de espines, y la regla de alineación es el análogo dinámico/no-conservativo de la interacción ferromagnética que alinea espines.

## 2. Ecuaciones del modelo (tal como aparecen en el paper — necesarias para programarlo)

### 2.1 Configuración general

- Simulación en una celda cuadrada de lado `L` con **condiciones de contorno periódicas**.
- Partículas puntuales moviéndose **fuera de red** (continuo, no lattice) en el plano.
- Unidad de longitud: el radio de interacción `r = 1`.
- Unidad de tiempo: `Δt = 1` (intervalo entre actualizaciones sucesivas de posición y dirección).
- Condición inicial estándar: en `t = 0`, `N` partículas distribuidas al azar en la celda, todas con la misma rapidez `v`, y direcciones `θ` distribuidas al azar.

### 2.2 Actualización de posición y velocidad

En cada paso de tiempo, la velocidad de **todas** las partículas se calcula **simultáneamente** (actualización paralela/sincrónica), y luego se actualiza la posición de la partícula `i`:

```
x_i(t+1) = x_i(t) + v_i(t+1) · Δt        (regla de actualización de posición)
```

donde `v_i(t+1)` tiene módulo constante `v` (rapidez fija, la misma para todas las partículas) y dirección dada por el ángulo `θ_i(t+1)`.

### 2.3 Regla de alineación con ruido

El ángulo de la partícula `i` en el paso siguiente se obtiene como:

```
θ_i(t+1) = ⟨θ(t)⟩_r  +  Δθ
```

donde:

- `⟨θ(t)⟩_r` es la **dirección promedio** de las velocidades de las partículas (incluyendo a la propia partícula `i`) que están dentro de un **círculo de radio `r`** centrado en `i`. Se calcula como:

```
⟨θ(t)⟩_r = arctan[ ⟨sin θ(t)⟩_r / ⟨cos θ(t)⟩_r ]
```

  (es decir, se promedian por separado las componentes seno y coseno de las direcciones vecinas y se recompone el ángulo con `arctan2` — esto evita el problema de promediar ángulos directamente).

- `Δθ` es un número aleatorio elegido con **distribución uniforme** en el intervalo `[−η/2, +η/2]`. Este término representa el **ruido** y actúa como la variable "tipo temperatura" del sistema.

### 2.4 Parámetros libres del modelo

Para un tamaño de sistema dado, hay tres parámetros libres:
- `η` — amplitud del ruido angular.
- `ρ = N/L²` — densidad de partículas (N partículas en celda de lado L).
- `v` — distancia recorrida por una partícula entre dos actualizaciones (rapidez).

**Límites de interés:**
- `v → 0`: las partículas no se mueven ⇒ el modelo se reduce a un análogo del modelo XY (solo alineación local, sin transporte).
- `v → ∞`: las partículas quedan completamente mezcladas entre updates ⇒ límite de campo medio (mean-field) de un ferromagneto.
- El paper usa **`v = 0.03`** en todas las simulaciones reportadas: suficientemente pequeño para que las partículas siempre interactúen con vecinos reales, pero suficientemente grande para cambiar la configuración de vecinos tras pocos pasos. Verifican que en el rango `0.003 < v < 0.3` el valor exacto de `v` no afecta cualitativamente los resultados.

### 2.5 Parámetro de orden

Para cuantificar la transición, se define la **velocidad media absoluta normalizada** del sistema completo:

```
v_a = (1/(N v)) · | Σ_{i=1}^{N} v_i |
```

- `v_a ≈ 0` si las direcciones individuales están distribuidas al azar (fase desordenada).
- `v_a = 1` en la fase completamente ordenada (todas las partículas moviéndose en la misma dirección).

`v_a` cumple el rol de **parámetro de orden** de la transición, análogo a la magnetización en un ferromagneto.

### 2.6 Leyes de escala cerca de la transición (exponentes críticos)

Asumiendo que en el límite termodinámico (`L → ∞`) el sistema exhibe una transición continua análoga a las de equilibrio:

```
v_a ∝ (η_c(ρ) − η)^β        para η → η_c por debajo, a ρ fija
v_a ∝ (ρ − ρ_c(η))^δ        para ρ → ρ_c por encima, a η fija
```

donde `η_c(ρ)` y `ρ_c(η)` son el ruido crítico y la densidad crítica (en el límite `L → ∞`), y `β`, `δ` son exponentes críticos.

Estos exponentes se estiman graficando `ln v_a` en función de `ln[(η_c(L) − η)/η_c(L)]` y de `ln[(ρ − ρ_c(L))/ρ_c(L)]`, ajustando la pendiente de la recta en la región donde el gráfico es más lineal.

## 3. Metodología de simulación

- **Geometría:** celda cuadrada, condiciones de contorno periódicas, partículas continuas (off-lattice).
- **Tamaños de sistema estudiados** (con N y L correspondientes a densidad fija ρ = 0.4, aprox N/L² ≈ cte):
  - N = 40, L = 3.1
  - N = 100, L = 5
  - N = 400, L = 10
  - N = 4000, L = 31.6
  - N = 10000, L = 50
- **Rapidez fija:** v = 0.03 en todas las corridas reportadas (radio de interacción r = 1, Δt = 1 como unidades).
- **Barrido de parámetros:** para un ρ fijo, se disminuye gradualmente η y se mide `v_a` en estado estacionario (Fig. 2a); alternativamente, a η fijo se aumenta ρ (Fig. 2b, con L = 20).
- **Estadística:** cerca de la transición, con N = 4000 y N = 10000, se promediaron 5 corridas con distintas condiciones iniciales para estimar el error (≈5%), debido a la convergencia lenta y grandes fluctuaciones cerca del punto crítico.
- **Estimación del punto crítico:** para cada L, η_c(L) y ρ_c(L) se ajustan buscando los valores para los cuales los gráficos log-log de `v_a` son "más rectos" en la región relevante (método indirecto, de ahí que los autores den barras de error conservadoras para los exponentes).

## 4. Resultados principales (parafraseado)

- **Diagrama de fases cualitativo (Fig. 1):** para densidad y ruido bajos, las partículas forman grupos que se mueven coherentemente en direcciones aleatorias (clusters locales); para densidad y ruido altos, el movimiento es esencialmente aleatorio con correlación débil; para densidad alta y ruido bajo, aparece **orden macroscópico**: todas las partículas terminan moviéndose espontáneamente en una misma dirección (ruptura espontánea de la simetría rotacional).
- **Transición cinética:** al bajar η (a ρ fija) o al subir ρ (a η fija), `v_a` pasa de ≈0 a valores finitos de manera continua — consistente con una transición de fase de segundo orden fuera de equilibrio.
- **Efecto de tamaño finito:** a medida que aumenta el tamaño del sistema, la región donde los datos muestran comportamiento de escala (scaling) se hace más amplia — evidencia de que en el límite termodinámico existe una verdadera transición (no solo un cruce/crossover suave).
- **Exponentes críticos estimados:**
  - `β = 0.45 ± 0.07` (exponente asociado al ruido crítico, a ρ = 0.4 fija).
  - `δ = 0.35 ± 0.06` (exponente asociado a la densidad crítica, a L = 20 y η = 2.0 fijos).
  - Estos dos exponentes, en principio, se esperaría que coincidieran en el límite termodinámico (por analogía con ferromagnetos desordenados donde η hace de temperatura y ρ de densidad de espines), pero dentro del error numérico los autores no pueden confirmar ni descartar esa igualdad.
- **Ruido crítico extrapolado:** mediante un análisis de escala de tamaño finito, `η_c(L→∞) = 2.9 ± 0.05` para ρ = 0.4 (nótese que el límite de "ruido infinito" del modelo, es decir ruido totalmente aleatorio, corresponde a `η_c → 2π`).
- Los autores remarcan que la naturaleza exacta del diagrama de fases completo (línea crítica η_c(ρ)) y una determinación más precisa de los exponentes quedan fuera del alcance de este trabajo, cuyo objetivo es mostrar la existencia del fenómeno.

## 5. Conclusiones (parafraseado)

- El modelo, a pesar de su extrema simplicidad (una sola regla de alineación + ruido, rapidez constante), produce una fenomenología rica: clustering, transporte colectivo, y una transición de fase cinética genuina entre desorden y orden macroscópico.
- La transición encontrada es un análogo fuera de equilibrio de las transiciones de fase continuas de sistemas en equilibrio (tipo ferromagnético/XY), con la diferencia esencial de que el momento no se conserva (por la autopropulsión con rapidez constante).
- El modelo se presenta como candidato natural para describir fenómenos biológicos de movimiento colectivo (bandadas, cardúmenes, colonias bacterianas) y también fue aplicado posteriormente por los mismos autores a colonias bacterianas reales.
- Se anticipan extensiones futuras: incorporar repulsión de núcleo duro, condiciones de contorno semiperiódicas o abiertas, y variantes en red — todas fuera del alcance de este artículo pero mencionadas como líneas de trabajo futuro.

## 6. Notas para implementación (resumen operativo del algoritmo)

Para programar el modelo de Vicsek según este paper, el pseudocódigo esencial es:

1. Inicializar N partículas en una caja L×L con posiciones y ángulos θ aleatorios; condiciones periódicas de contorno.
2. En cada paso de tiempo, para cada partícula i:
   a. Encontrar vecinos j (incluida i misma) dentro de radio r = 1.
   b. Calcular `θ_i_nuevo = atan2(⟨sin θ_j⟩, ⟨cos θ_j⟩) + Δθ`, con `Δθ ~ Uniforme(−η/2, η/2)`.
3. Actualizar todas las posiciones simultáneamente: `x_i ← x_i + v·(cos θ_i_nuevo, sin θ_i_nuevo)·Δt`, aplicando wrap-around periódico.
4. Repetir; medir el parámetro de orden `v_a = (1/(Nv))|Σ v_i|` en régimen estacionario para distintos (η, ρ).

## 7. Referencia bibliográfica completa

Tamás Vicsek, András Czirók, Eshel Ben-Jacob, Inon Cohen, and Ofer Shochet, "Novel Type of Phase Transition in a System of Self-Driven Particles," *Physical Review Letters* **75**, 1226 (1995).
DOI: 10.1103/PhysRevLett.75.1226
