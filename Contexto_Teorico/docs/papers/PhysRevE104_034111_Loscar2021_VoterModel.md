# Noisy Multistate Voter Model for Flocking in Finite Dimensions (Loscar, Baglietto & Vazquez, 2021)

*Fuente original: `2021PhysRevE104034111.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: este archivo contiene un resumen y extractos, no la transcripción literal completa del paper (por derechos de autor); para el texto íntegro consultar el PDF original en el Proyecto.*

## 1. Motivación y planteo del problema (resumen del abstract/introducción)

El paper estudia una variante del modelo de Vicsek en la que la regla de alineación **no es un promedio** de las direcciones vecinas (como en Vicsek 1995) sino una **regla de "votante" (voter-like)**: cada partícula simplemente **copia** la dirección de **un único vecino elegido al azar** dentro de un radio de interacción `R = 1`, más ruido. Es el análogo "flocking" del *noisy voter model* (modelo de votante con ruido) clásico de dinámica de opiniones, generalizado a un número continuo de estados angulares (de ahí "multistate voter model", MSVM).

La motivación viene de un trabajo experimental con peces cíclidos (Jhawar et al. 2020) que mostró que la polarización de un cardumen aumenta cuando el grupo es más chico, y que ese efecto se explica con una dinámica de copia simple (voter-like) más ruido demográfico en un modelo de **campo medio** (mean-field, MF) — sin necesidad de reglas de promediado tipo Vicsek. Un resultado analítico previo de los mismos autores (Vazquez, Loscar & Baglietto 2019) para el MSVM en MF mostró que ese orden parcial es solo un efecto de tamaño finito: en el límite termodinámico (N→∞), **cualquier ruido positivo destruye completamente el orden** (transición en ruido cero), a diferencia del modelo de Vicsek donde la transición ocurre a ruido crítico positivo.

La pregunta central de este paper: **¿qué pasa cuando las partículas están en el espacio (no en MF) y además se mueven?** ¿El movimiento de las partículas puede sostener orden macroscópico pese a la naturaleza "destructiva" del ruido tipo votante? Estudian tres escenarios progresivos:
1. Campo medio (MF, interacción todos-con-todos).
2. Caso estático (v = 0): partículas fijas en los sitios de una red cuadrada (red 1D y red 2D), interactuando con primeros vecinos.
3. Caso dinámico (v > 0): partículas moviéndose en un espacio continuo 2D, interactuando con vecinos dentro de radio R = 1.

## 2. Ecuaciones del modelo (tal como aparecen en el paper — necesarias para programarlo)

### 2.1 Definición general (caso dinámico, Sec. II)

`N` partículas se mueven a rapidez constante `v` en una caja cuadrada 2D de lado `L` con **condiciones de contorno periódicas**. La densidad `ρ = N/L²` se fija en **ρ = 0.5** salvo que se indique lo contrario. Posición y velocidad de la partícula `i` en el tiempo `t`:

```
r_i^t = (x_i^t, y_i^t)
v_i^t = (v cos θ_i^t, v sin θ_i^t)
```

Condición inicial: posición aleatoria dentro de la caja, dirección `θ` aleatoria.

**Regla de actualización** (paso de tiempo `Δt = 1`, actualización en paralelo/sincrónica para todas las partículas a la vez):

```
r_i^{t+1} = r_i^t + v_i^t · Δt                     (1a)

θ_i^{t+1} = θ_j^t + ξ_i^{t+1}                       (1b)
```

donde:
- `θ_j^t` es la dirección de movimiento de una partícula `j` elegida **al azar entre los vecinos** que están dentro de un disco de radio `R = 1` centrado en `r_i^t` (es decir, la partícula `i` **copia** a un vecino elegido al azar, no promedia).
- `ξ_i^{t+1}` es un ángulo aleatorio elegido **uniformemente** en el intervalo `[−ηπ, ηπ)`, con amplitud de ruido `η` (0 < η < 1).
- Si la partícula `i` no tiene vecinos dentro de `R`, su dirección cambia solamente por el ruido `ξ`.

Esta es la diferencia clave respecto de Vicsek: en Vicsek la nueva dirección es el **promedio angular** de todos los vecinos (incluida la propia partícula) + ruido; acá es la dirección de **un solo vecino copiado al azar** + ruido.

### 2.2 Parámetro de orden y susceptibilidad

```
φ(t) ≡ (1/(vN)) · | Σ_{i=1}^{N} v_i^t |
     = (1/N) · sqrt[ (Σ_{i=1}^N cos θ_i^t)²  +  (Σ_{i=1}^N sin θ_i^t)² ]        (2)
```

(mide el nivel de alineación colectiva — magnitud de la velocidad media normalizada del sistema).

```
χ ≡ N · [ ⟨φ²⟩ − ⟨φ⟩² ]        (3)
```

(susceptibilidad: amplitud de las fluctuaciones de φ en el estado estacionario; `⟨φ^m⟩` es el m-ésimo momento de φ promediado sobre realizaciones en estado estacionario).

### 2.3 Caso de campo medio (MF, Sec. III) — R = L

En MF la dinámica angular es independiente de las posiciones, y se implementa con **actualización secuencial/aleatoria** (una partícula al azar por paso, `Δt = 1/N`):

```
θ_i(t + Δt) = θ_j(t) + ξ_i(t + Δt)        (4)
```

(se elige una partícula `i`, copia el estado de otra partícula `j` elegida al azar entre todas, con ruido). Nota metodológica importante: los resultados de esta actualización secuencial ("random update") se relacionan con los de la actualización paralela mediante la transformación `N → 2N` (paralelo a partir de secuencial) o `N → N/2` (secuencial a partir de paralelo), resultado demostrado por Blythe & McKane (2007) para modelos tipo votante.

**Resultados de escala en MF:**

```
⟨φ⟩_MF ~ (η² N)^{-1/2}      para η ≪ 1  y  η²N ≫ 1        (5)

χ_MF = N · g(η² N)                                          (6)
```

donde `g` es una función suave de la variable de escala `x_MF ≡ η²N`. De (6) se deduce que el ruido crítico (ubicación del pico de χ) escalea como:

```
η_c^MF ~ N^{-1/2}        (7)
```

**Conclusión de la sección MF:** transición orden-desorden **en ruido cero** (`η_c = 0`) en el límite termodinámico: φ = 1 para η = 0 (consenso absorbente), φ = 0 para cualquier η > 0 cuando N → ∞.

### 2.4 Caso estático en 1D y 2D (Sec. IV) — v = 0, red cuadrada

Cada partícula ocupa un sitio de una red cuadrada de `d` dimensiones (`N = L^d` sitios) e interactúa solo con sus `2d` primeros vecinos, con condiciones periódicas. Actualización secuencial (random update), `Δt = 1/N`: una partícula al azar copia el estado de un primer vecino al azar, con ruido de amplitud η.

**Escalas en 1D:**

```
η_c^{1D} ~ N^{-1}          (8)
χ_max ~ N                  (9)

χ_{1D} = N · g₁(ηN)        (10)
```

con variable de escala `x_{1D} ≡ ηN`, y `⟨φ⟩_{1D} ~ x_{1D}^{-1/2}` para `x_{1D} ≫ 1`.

**Escalas en 2D** (dimensión marginal — requiere una corrección logarítmica, por analogía con el modelo de reacción catalítica de Fichthorn-Gulari-Ziff, FGZ):

Se define un **ruido efectivo**:

```
η̂ ≡ η √(−ln η)        (definición general usada en 2D y en el caso dinámico)
```

y para el caso estático 2D:

```
η̂_c^{2D} = η_c^{2D} · √(−ln η_c^{2D})        (13)

χ_{2D} = N · g₂(η̂² N)                          (11)

η̂_c^{2D} ≈ B · N^{-1/2}        con B = 1.3 ± 0.04        (12)
```

Ajuste directo (sin transformar) del ruido crítico original: `η_c^{2D} ≈ A·N^{-α}` con `A ≈ 0.96` y exponente efectivo `α(N)` dependiente de N. Partiendo de (12)-(13) se deriva:

```
(2α − 1)·ln N − 2·ln(A/B) − ln(ln N) − ln α = 0        (14)
```

y, resolviendo aproximadamente para α cerca de 1/2:

```
η_c^{2D} ≈ A · N^{-α(N)}                                          (15a)

α(N) ≈ 1/2 + [ ln(A/B) + (1/2)ln(ln N) ] / (ln N − 1)             (15b)

η_c^{2D} ≈ 1.8 · (N ln N)^{-1/2}        para N ≫ 1                (15c)
```

**Exponentes numéricos obtenidos** (ajustes de potencia a los datos de simulación, Fig. 2):
- MF: `η_c^MF ~ N^{-α}` con `α = 0.5 ± 0.015`; `χ_max ~ N^γ` con `γ = 1.01 ± 0.01`.
- 1D: `α = 0.99 ± 0.02`; `γ = 0.997 ± 0.005`.
- 2D: `α = 0.56 ± 0.01` (exponente aparente, sin corrección logarítmica); `γ = 0.99 ± 0.01`.

**Conclusión de la sección estática:** tanto en 1D como en 2D (red estática), la transición ocurre también en **ruido cero** en el límite termodinámico — igual que en MF.

### 2.5 Caso dinámico v > 0 en 2D continuo (Sec. V)

Simulación en espacio continuo 2D con la dinámica en paralelo definida en la Sec. II (Ecs. 1a-1b), condiciones periódicas, interacción local con radio `R = 1`, densidad `ρ = 0.5` fija.

Se observa numéricamente que, a diferencia de MF y de los casos estáticos, el **ruido crítico satura a un valor positivo** `η_c(v, N→∞) > 0` cuando `v` es suficientemente grande — es decir, aparece una verdadera fase ordenada sostenida por el movimiento de las partículas, análoga a la del modelo de Vicsek.

**Escala del ruido efectivo (tipo Family-Vicsek con dos exponentes β y z):**

```
η̂_c(v,N) ≡ η_c(v,N) · √(−ln η_c(v,N))        (16)

η̂_c(v,N) ~ v^β · f(v^z N)        (17)

f(x) ~ x^{-α}   para x ≪ 1
f(x) ~ const    para x ≫ 1                    (18)
```

Límites:

```
η̂_c(v, N→∞) ~ v^β        (19)     (límite termodinámico)
η̂_c(v→0, N)  ~ N^{-α}     (20)     (límite de rapidez cero)

β = z·α        (21)     (relación de escala entre exponentes)
```

**Valores ajustados:** `β = 1.01 ± 0.02` (del ajuste `η̂_c(v,∞) ≈ C·v^β`, con `C = 0.095 ± 0.01`); asumiendo `α = α_{2D} = 1/2` (el mismo exponente del caso estático 2D) se obtiene `z = 2.02 ± 0.04` de la relación (21). Esto lleva a la forma de escala simplificada, usada para colapsar los datos:

```
η̂_c(v,N) ~ v · f(v² N),   con f(x) ~ x^{-1/2} para x≪1,  f(x) ~ const para x≫1        (22)
```

**Comportamiento asintótico del ruido crítico efectivo, régimen de rapidez baja:**

```
η̂_c(v,∞) ≈ C · v,        C = 0.095 (ajuste para v ≲ 0.75)        (23)
```

De ahí, deshaciendo la corrección logarítmica (mismo procedimiento algebraico que en la Sec. 2.4):

```
2(β − 1)·ln v − 2·ln(C/D) + ln(−ln v) + ln β = 0        (24)

η_c(v,∞) ≈ D · v^{β(v)}                                          (25a)

β(v) ≈ 1 + [ ln(C/D) + (1/2)ln(−ln v) ] / (ln v + 1/2)           (25b)

η_c(v,∞) ≈ C · v · (−ln v)^{-1/2}        para v ≪ 1              (25c)
```

Esta es la expresión final para el **ruido de transición del modelo de votante para flocking (FVM)** en función de la rapidez, en el límite termodinámico y régimen de baja velocidad.

También vale, a partir de (22):

```
η̂_c(v,N) ~ N^{-1/2}        para v²N ≪ 1        (26)
```

y se define el **tamaño de cruce** (crossover) entre el régimen dominado por tamaño finito y el régimen saturado en `v`:

```
N_cross ~ v^{-2}
```

**Comparación explícita con Vicsek:** el paper cita que en el modelo de Vicsek (régimen de baja densidad y baja rapidez) el ruido crítico escala como `η_c ~ v^{0.45}` (Rubio Puzzo, De Virgiliis & Grigera 2019), mientras que en el modelo de votante para flocking (FVM) se obtiene `η_c ~ v·(−ln v)^{-1/2}` — un exponente efectivo superlineal, distinto del caso Vicsek, y además el ruido crítico del FVM es sustancialmente menor que el del modelo de Vicsek para una misma rapidez y densidad.

## 3. Metodología de simulación (resumen)

- **Condiciones de contorno:** periódicas en todos los casos (MF, red 1D/2D, espacio continuo 2D).
- **Densidad fija:** ρ = N/L² = 0.5 en el caso dinámico continuo (salvo que se indique otro valor).
- **Radio de interacción:** R = 1 en el caso dinámico; en el caso estático, interacción con los `2d` primeros vecinos de la red.
- **Ruido:** ξ uniforme en `[−ηπ, ηπ)`, con `0 < η < 1` (nótese la diferencia de convención con Vicsek 1995, donde el ruido está en `[−η/2, η/2]` sin factor π).
- **Tipos de actualización:**
  - MF y casos estáticos (1D, 2D): actualización **secuencial/aleatoria** (`Δt = 1/N`, una partícula actualizada por paso) — esto permite comparación directa con resultados analíticos previos del MSVM y del modelo de votante con ruido (NVM).
  - Caso dinámico continuo: actualización **paralela/sincrónica** (todas las partículas a la vez, `Δt = 1`) — la convención estándar en modelos de flocking (Vicsek-like).
  - Los autores verifican que ambos esquemas dan resultados equivalentes bajo el reescaleo `N ↔ 2N`.
- **Rapidezes estudiadas en el caso dinámico:** v = 0.1 y v = 1.0 en las figuras principales (Fig. 5); barrido más amplio de v (incluyendo v pequeños) en Fig. 6 para extraer los exponentes β, z.
- **Tamaños de sistema (N):** barridos en cada escenario (MF, 1D, 2D estático, 2D dinámico) para hacer el análisis de escala de tamaño finito (finite-size scaling) y extrapolar al límite termodinámico N → ∞.
- **Medición de observables:** promedios de φ y χ en la ventana temporal estacionaria (en MF, entre t=10⁶ y t=2×10⁷), sobre 10 realizaciones independientes.
- **Determinación del punto de transición η_c(N):** ubicación del **máximo (pico) de la susceptibilidad χ** como función de η, para cada N.

## 4. Resultados principales (parafraseado)

- **Campo medio:** transición orden-desorden en `η_c = 0` (ruido nulo) en el límite termodinámico; para cualquier η > 0 fijo, φ → 0 cuando N → ∞. Buen colapso de datos con la variable de escala `x_MF = η²N`.
- **Redes estáticas (1D y 2D, v = 0):** mismo tipo de transición en ruido cero. En 1D la variable de escala es `ηN`; en 2D, por ser dimensión marginal (analogía con el modelo FGZ de reacciones catalíticas), se requiere el ruido efectivo `η̂ = η√(−ln η)` para lograr un buen colapso con exponente universal 1/2, análogo al de MF.
- **Caso dinámico (v > 0):** aparece un comportamiento cualitativamente distinto — el ruido crítico ya **no** se anula con N, sino que **satura a un valor positivo** `η_c(v,∞) > 0` que crece con la rapidez v. Esto significa que el movimiento de las partículas **es capaz de sostener orden macroscópico** pese al carácter "destructivo" del ruido tipo votante que domina en MF y en las redes estáticas.
- Comparando v = 0.1 y v = 1.0: a mayor rapidez, mayor orden (φ más alto) y menores fluctuaciones (χ menor) — el movimiento tiene un efecto "ordenador" análogo al de Vicsek.
- La escala de Family-Vicsek con exponentes `β ≈ 1` y `z ≈ 2` permite colapsar todas las curvas de η_c(v,N) para distintas velocidades en una sola curva maestra (Fig. 6b).
- Para rapidez baja (`v ≪ 1`), el ruido crítico en el límite termodinámico se comporta como `η_c(v,∞) ≈ C·v·(−ln v)^{-1/2}` — un crecimiento aproximadamente lineal en v, con corrección logarítmica, y con exponente efectivo (ligeramente mayor a 1) que se acerca lentamente a 1 cuando v→0.

## 5. Conclusiones (parafraseado)

- El modelo de votante para flocking (FVM, flocking voter model) —donde cada partícula copia la dirección de un vecino al azar en vez de promediar, como en Vicsek— muestra un comportamiento crítico marcadamente distinto según haya o no movimiento de partículas:
  - **Sin movimiento** (MF, o redes estáticas 1D/2D): el ruido, por más pequeño que sea, destruye completamente el orden en el límite termodinámico (transición en ruido cero, `η_c = 0`).
  - **Con movimiento** (`v > 0` en espacio 2D continuo): el desplazamiento de las partículas introduce correlaciones espaciales suficientes para sostener una fase ordenada genuina hasta un ruido crítico positivo `η_c(v) > 0`, que crece con la rapidez.
- Esto es un resultado no trivial dentro de la literatura del modelo de votante: agregar ruido externo a la dinámica de copia típicamente destruye el orden colectivo en cualquier dimensión finita; acá se muestra que el **movimiento de las partículas puede revertir ese efecto**.
- La aproximación de campo medio, que predice transición en ruido cero, **falla** para describir el caso realista con partículas moviéndose a rapidez finita — remarcando la importancia de modelar explícitamente el espacio y el movimiento (relevante, por ejemplo, para reinterpretar los experimentos con peces de Jhawar et al. 2020).
- Quedan abiertas como líneas futuras: estudiar correlaciones posición-velocidad entre partículas para entender el mecanismo microscópico del ordenamiento inducido por movimiento, y desarrollar una descripción teórica más allá de MF que incorpore esas correlaciones.

## 6. Notas para implementación (resumen operativo del algoritmo, caso dinámico — el relevante para el TP2)

1. Inicializar N partículas en caja L×L (density ρ = N/L² = 0.5 típico), posiciones y ángulos θ aleatorios; condiciones periódicas.
2. En cada paso de tiempo (actualización en paralelo), para cada partícula i:
   a. Buscar vecinos dentro de radio R = 1 (sin incluir necesariamente a la propia partícula — a diferencia de Vicsek, acá se **copia**, no se promedia).
   b. Si hay al menos un vecino, elegir uno `j` al azar entre ellos y tomar `θ_j^t` como base; si no hay vecinos, mantener `θ_i^t` como base.
   c. `θ_i^{t+1} = θ_base + ξ`, con `ξ ~ Uniforme(−ηπ, ηπ)`.
3. Actualizar posiciones: `r_i^{t+1} = r_i^t + v·(cos θ_i^{t+1}, sin θ_i^{t+1})·Δt`, con wrap-around periódico.
4. Medir en estado estacionario: `φ = (1/N)·sqrt[(Σcos θ_i)² + (Σsin θ_i)²]` y `χ = N·(⟨φ²⟩ − ⟨φ⟩²)`.
5. Repetir para distintos (η, N, v) para ubicar el pico de χ (η_c) y estudiar el escaleo con N y v — comparar contra las fórmulas de escala (Ecs. 17, 22, 25c) y contra el modelo de Vicsek (que promedia en vez de copiar).

## 7. Referencia bibliográfica completa

Ernesto S. Loscar, Gabriel Baglietto, and Federico Vazquez, "Noisy multistate voter model for flocking in finite dimensions," *Physical Review E* **104**, 034111 (2021).
DOI: 10.1103/PhysRevE.104.034111

### Referencias clave citadas dentro del paper (útiles para contexto del TP2)

- T. Vicsek, A. Czirók, E. Ben-Jacob, I. Cohen, and O. Shochet, *Phys. Rev. Lett.* **75**, 1226 (1995) — el modelo de Vicsek original (paper [1] del TP2).
- G. Baglietto and F. Vazquez, *J. Stat. Mech.* (2018) 033403 — introduce la dinámica de copia (voter-like) noiseless para flocking, antecedente directo del FVM.
- F. Vazquez, E. S. Loscar, and G. Baglietto, *Phys. Rev. E* **100**, 042301 (2019) — resultados analíticos del MSVM en campo medio, base teórica de las Ecs. (5)-(7) de este paper.
- J. Jhawar, R. G. Morris, U. R. Amith-kumar, M. Danny Raj, T. Rogers, H. Rajendran, and V. Guttal, *Nat. Phys.* **16**, 488 (2020) — experimento con peces cíclidos que motiva el estudio.
- J. Toner and Y. Tu, *Phys. Rev. Lett.* **75**, 4326 (1995) — teoría hidrodinámica del orden de largo alcance en el modelo de Vicsek.
- M. L. Rubio Puzzo, A. De Virgiliis, and T. S. Grigera, *Phys. Rev. E* **99**, 052602 (2019) — escala `η_c ~ v^0.45` en el modelo de Vicsek, usada para comparación.
