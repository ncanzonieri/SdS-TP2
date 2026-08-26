# Teorica_2

*Fuente original: `Teorica_2.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion".*

> Nota de extracción: el PDF original son diapositivas (slides). El texto se recuperó por extracción de capas de texto y, en las diapositivas que citan al paper de Vicsek et al. (1995), el PDF contiene el mismo párrafo superpuesto varias veces (restos de texto de versiones/figuras encimadas). Abajo se consolidó ese contenido eliminando las repeticiones redundantes, pero preservando el sentido completo y **todas** las ecuaciones tal cual aparecen en el documento. Las ecuaciones (1), (2) y (3) citadas por el TP2 se transcriben literalmente, en notación matemática.

# Autómatas Celulares — Simulación de Sistemas

## Diapositiva 2 — Ideas Básicas: Autómata Celular

- En general, se discretiza el espacio en una grilla (celdas).
- Cada sitio de la grilla tiene un estado (puede ser ocupado o no por una partícula con velocidad, o el valor de alguna cantidad macroscópica, etc.)
- Reglas (Heurísticas) para definir transición de estados, entre celdas entre un paso temporal y el siguiente.
- En algunos casos el AC pertenece al dominio Microscópico y promediando sobre muchas celdas se llega al dominio Macroscópico.

## Diapositiva 3 — Autómatas Celulares: Definición

- AC son arreglos regulares de celdas individuales de la misma clase.
- Cada celda tiene un numero finito de estados discretos.
- Los estados se actualizan simultáneamente (sincrónicamente) en cada paso temporal.
- Las reglas de actualización son determinísticas y uniformes en tiempo y espacio.
- Las reglas para la evolución de una celda depende solamente de un vecindario local a su alrededor.

## Diapositiva 4 — Autómatas Celulares 1-D

(Título de sección, sin texto adicional.)

## Diapositiva 5 — Autómatas Celulares en una dimensión

Sea una cadena uniforme de celdas:

```
X X X X X
    (i-1) i (i+1)
```

La celda `i` tiene un estado `a_i(t)` en el instante `t`.

Cada estado `a_i(t)` está definido por un nro. finito de enteros positivos (`k`) etiquetados desde 0 hasta (`k-1`).

## Diapositiva 6 — Autómatas Celulares en una dimensión

Sea una cadena uniforme de celdas (misma figura que la diapositiva anterior). La celda `i` tiene un estado `a_i(t)` en el instante `t`.

La regla de evolución está dada por el mapeo:

```
a_i(t+1) = f[ a_{i-r}(t), ..., a_i(t), ..., a_{i+r}(t) ]
```

donde:

- `r` es el rango (nro.) de vecinos a considerar.
- `α_j` constantes enteras.
- `f` Función no lineal: "regla del autómata".

## Diapositiva 7 — Autómatas Celulares en una dimensión

Un ejemplo de AC con `k = 2` y `r = 1`:

En general el nro. de posibles combinaciones es `N = k^(2r+1)`.

El nro. total de reglas posibles es `k^N`, en este caso es `2^8 = 256`.

Un AC de 1D cuya regla de actualización solo depende de los primeros vecinos (y de sí mismo) se llama: **"AC Elemental"**.

## Diapositiva 8 — Autómatas Celulares en una dimensión: Subclases de Reglas

- **Regla Totalista:** Todos los `α_j = 1`.
- **Regla Simétrica:** `f[a_{i-r}, ..., a_{i+r}] = f[a_{i+r}, ..., a_{i-r}]`.
- **Regla Legal:** No cambia la configuración nula (todos ceros).
- ...

## Diapositiva 9 — Autómatas Celulares en una dimensión

Hay 4 posibles patrones de Autómatas Celulares en 1-D:

1. Desaparece con el tiempo.
2. Evoluciona a un tamaño fijo finito.
3. Crece indefinidamente a una velocidad fija.
4. Crece y se contrae periódicamente.

## Diapositiva 10 — Autómatas Celulares en una dimensión

Ejemplos de Wolfram (1984, *Nature*, 311, p. 419).

## Diapositiva 11 — Autómatas Celulares 2-D

(Título de sección, sin texto adicional.)

## Diapositiva 12-13 — Autómatas Celulares 2D: Definiciones de Vecindad

Vecindario **Von Neumann** de alcance `r`:

```
N_{i,j}^{(vN)} := { (k,l) ∈ L : |k - i| + |l - j| ≤ r }
```

Vecindario **Moore** de alcance `r`:

```
N_{i,j}^{(M)} := { (k,l) ∈ L : |k - i| ≤ r y |l - j| ≤ r }
```

Se muestran figuras con los vecindarios de Von Neumann y Moore para `r = 1` y `r = 2` (Von Neumann arriba, Moore abajo, según la figura del libro de referencia).

## Diapositiva 14 — Autómatas Celulares 2D: "Juego de la vida"

(Título de sección, sin texto adicional.)

## Diapositiva 15 — Autómatas Celulares 2D: "Vida"

En la década de 1970, Conway definió un autómata celular que simula la evolución de colonias de organismos vivos.

Las reglas son:

- Se considera 8 vecinos (Vecindad de Moore, `r = 1`).
- Cada celda tiene dos estados posibles "Viva" o "Muerta" (`k = 2`).
- Las Celdas Vivas permanecerán vivas en el siguiente paso temporal si tiene 2 o 3 vecinos vivos, de lo contrario morirá.
- Las Celdas Muertas se transformarán en Vivas solamente si tiene exactamente 3 vecinos vivos.

## Diapositiva 16 — Autómatas Celulares 2D: "Vida" — Implementación

- **Condición Inicial:**
  - Puede ser al azar (cada celda "Viva" o "Muerta").
  - Puede ser una configuración predeterminada.
- **Condición de Contorno:**
  - Puede ser periódica o no.

## Diapositiva 17 — Autómatas Celulares 2D: "Vida" — Patrones Estables

"Vida" contiene muchos patrones que permanecen estables de iteración en iteración cuando no son perturbados por otros objetos. La evolución en el tiempo de configuraciones iniciales aleatorias, con igual probabilidad (1/2) de estar vivo o muerto, muestra que en el límite de dominio grande y tiempo largo aproximadamente el 3% de las celdas están vivas.

## Diapositiva 18 — Autómatas Celulares 2D: "Vida" — Ejemplo de Evolución (50x50)

"Vida" en una grilla de 50×50 con condiciones periódicas de contorno. Se muestra el estado inicial (inicialización aleatoria con igual probabilidad de vivo/muerto) y los estados en los tiempos 141 a 148.

## Diapositiva 19 — Autómatas Celulares 2D: "Vida" — Ejemplo de Evolución (50x50)

"Vida" en una grilla de 50×50 con condiciones periódicas de contorno: porcentaje de celdas vivas en función del tiempo (iteraciones). El límite para dominio y tiempo grandes todavía no se alcanza en el rango graficado (0 a 250 iteraciones, porcentaje de celdas vivas entre 0 y 60%).

## Diapositiva 20 — Autómatas Celulares 2D: "Vida"

(Diapositiva de imagen/ejemplo, sin texto adicional recuperado.)

## Diapositiva 21 — "Game of life" 3D (tiempo)

(Diapositiva de imagen/ejemplo, sin texto adicional recuperado.)

## Diapositiva 22 — Autómatas Celulares 3D (x,y,z)

(Diapositiva de imagen/ejemplo, sin texto adicional recuperado.)

## Diapositiva 23 — Autómatas Celulares: Modelos de Fluidos 2D "Lattice Gas"

(Título de sección, sin texto adicional.)

## Diapositiva 24 — Autómatas Celulares: Fluidos 2D — (Antes) Ecuación de Navier Stokes

- Conservación de la masa
- Conservación de la energía
- Conservación del momento
- Hipótesis de medio Continuo

Ecuación de Continuidad + Condiciones de Contorno.

## Diapositiva 25 — Autómatas Celulares: Fluidos 2D — (Antes) Ecuación de Navier Stokes

Variables: Velocidad, viscosidad Cinemática, Presión `P = p/ρ_0`.

- Ecuaciones Diferenciales No Lineales.
- Solución Analítica en pocos casos.
- En general se usan métodos numéricos.

## Diapositiva 26 — Número de Reynolds

Número adimensional que considera fuerzas inerciales vs. viscosas, en función de la Velocidad Característica y la Longitud Característica.

- `Re << 1` → Flujo Laminar
- `Re >> 1` → Flujo Turbulento

## Diapositiva 27 — Modelo FHP

Frisch, Hasslacher y Pomeau (1986) definieron un modelo "lattice gas" que es equivalente a resolver las ecuaciones de Navier-Stokes.

## Diapositiva 28 — Modelo FHP

- Retícula triangular con simetría hexagonal.
- Cada nodo tiene 6 primeros vecinos a la misma distancia.
- Los vectores que unen estos nodos se llaman "lattice vectors" o velocidades de la retícula.

## Diapositiva 29 — Modelo FHP

- Cada nodo tiene asociada una Celda.
- La Celda puede estar vacía u ocupada por varias partículas.
- Todas las partículas tienen la misma masa (=1) y son indistinguibles.
- Evolución. Cada paso temporal tiene 2 etapas:
  - Propagación (se mueve según velocidades).
  - Colisión (adquieren nuevas velocidades, según las reglas de colisión).

`r` es el vector posición de un nodo. `r + c_i` son las posiciones de sus vecinos.

## Diapositiva 30 — Autómatas Celulares: Fluidos 2D

- Todas las posibles colisiones deben conservar el momento (además de la masa).
- ¿Cómo serían las de 5 y 6 partículas?
- ¿Y las de 2 a 60º o 120º?

## Diapositiva 31-32 — Implementación: Codificación estado de cada Celda

Cada celda se codifica con un byte: un bit indica si el nodo es sólido (barrera), otro bit indica presencia de partícula "random" (rest particle) y los 6 bits restantes indican ocupación en cada una de las 6 direcciones posibles de la retícula.

Hay 256 estados posibles.

## Diapositiva 33 — Implementación: Ejemplo Tabla de mapeo de estados (sin considerar colisiones de 4 partículas)

Primero los que no cambian:

- Desde `00000000` hasta `00111111` (de 0 a 63)
- y desde `10000000` hasta `10111111` (de 128 a 191)

## Diapositiva 34 — Implementación: Tabla de mapeo de estados — Presencia de sólido

- Desde `01000000` hasta `01111111` (de 64 a 127)
- y desde `11000000` hasta `11111111` (de 192 a 255)

Al colisionar con un sólido la partícula regresa por donde vino: A pasa a D, B pasa a E, C pasa a F, …

## Diapositiva 35 — Implementación: Tabla de mapeo de estados — Colisión Frontal Binaria

AD, BE y CF: cada una puede pasar a cualquiera de las otras 2 con igual probabilidad. (Se muestra un ejemplo gráfico en la diapositiva original.)

## Diapositiva 36 — Implementación: Tabla de mapeo de estados

Finalmente, Colisión de 3 partículas (se muestra un ejemplo gráfico en la diapositiva original).

## Diapositiva 37 — Condimentos Finales

1. **Promedios Macroscópicos.** Por lo menos 16×16 celdas y 10 pasos temporales.
2. **Fuerza Impulsora.** Incluir momentum desde los bordes o cambiando con alguna probabilidad las velocidades de algunas celdas en una dirección deseada.
3. **Remapeo de la grilla hexagonal** para cálculo de vecinos (ver bibliografía).

## Diapositiva 38 — Autómatas Celulares: Fluidos 2D — Ejemplo

Fluido alrededor de una barrera (de largo L).

- Grilla de 1929 × 960
- 100.000 pasos
- Promedios cada 32×32 celdas y cada 100 pasos temporales.

Pregunta planteada: ¿Cómo se puede cambiar el nro. de Reynolds en estas simulaciones?

## Diapositiva 39 — Autómatas Celulares: "Off - Lattice"

(Título de sección, sin texto adicional.)

## Diapositiva 40 — Autómatas Celulares: "Off-Lattice" — Bandadas de agentes autopropulsados

Geometría: celda cuadrada de lado `L`, radio de interacción `r = 1`, cada partícula tiene velocidad `v`.

**Definiciones:**

- Cada partícula es puntual y se mueve en el continuo dentro de la celda de lado `L`.
- `r` es el radio de interacción entre partículas.
- `v` es la velocidad de módulo `v` y dirección dada por el ángulo `θ`.
- El paso temporal es `dt = 1`.

Referencia: **Vicsek et al. (1995)**.

## Diapositiva 41 — Autómatas Celulares: "Off-Lattice" — Bandadas de agentes autopropulsados

**Condiciones Iniciales:**

- A `t = 0`, se generan `N` partículas distribuidas al azar (random) en la celda.
- Todas tienen igual módulo `v = 0.03`.
- Y direcciones `θ` distribuidas al azar (random).

## Diapositiva 42 — Autómatas Celulares: "Off-Lattice" — Bandadas de agentes autopropulsados — Evolución temporal

> El modelo de Vicsek et al. (1995) usa la actualización más simple posible de direcciones/posiciones. En la mayoría de las simulaciones del paper original, las condiciones iniciales son: (i) en `t = 0` las `N` partículas se distribuyen al azar en la celda; (ii) todas tienen el mismo módulo de velocidad `v`; (iii) las direcciones `θ` son aleatorias. Las velocidades `{v_i}` de las partículas se determinan simultáneamente en cada paso temporal, y la posición de la partícula `i` se actualiza según la Ecuación (1). La velocidad `v_i(t+1)` se construye con módulo constante `v` y dirección dada por el ángulo `θ(t+1)`, obtenido de la Ecuación (2).

**Ecuación (1) — Actualización de posición:**

```
x_i(t + 1) = x_i(t) + v_i(t) Δt
```

**Ecuación (2) — Actualización del ángulo de dirección:**

```
θ(t + 1) = ⟨θ(t)⟩_r + Δθ
```

Donde `⟨θ(t)⟩_r` es el promedio de los ángulos de todas las partículas dentro del radio `r` (incluyendo a la propia partícula `i`), calculado como:

```
⟨θ(t)⟩_r = arctan2[ ⟨sin(θ(t))⟩_r / ⟨cos(θ(t))⟩_r ]
```

Y `Δθ` es un número aleatorio elegido con probabilidad uniforme en el intervalo `[-η/2, η/2]` (ruido tipo "temperatura").

En consecuencia, hay tres parámetros libres para un tamaño de sistema dado: `η` (ruido), `ρ` (densidad) y `v` (módulo de velocidad, es decir la distancia que recorre una partícula entre dos actualizaciones).

## Diapositiva 43 — Autómatas Celulares: "Off-Lattice" — Bandadas de agentes autopropulsados

(Continuación gráfica de la fórmula `arctan2[...]` de la diapositiva anterior — Ecuación (2) reiterada visualmente.)

## Diapositiva 44 — Autómatas Celulares: "Off-Lattice" — Bandadas de agentes autopropulsados

El sistema tiene 3 variables relevantes:

- Módulo de la velocidad (`v`)
- Densidad (`ρ = N / L²`)
- Amplitud del ruido (`η`)

Se define el **parámetro de orden** (`v_a`) como:

**Ecuación (3) — Parámetro de orden (velocidad media normalizada):**

```
v_a = (1 / (N v)) · | Σ_{i=1}^{N} v_i |
```

Interpretación (según el paper de Vicsek et al., 1995, citado en la diapositiva): si las direcciones de movimiento de las partículas están distribuidas al azar, esta velocidad es aproximadamente cero; en la fase de movimiento coherente (con dirección de velocidades ordenada), `v_a ≈ 1`. Por lo tanto, la velocidad media normalizada puede considerarse como un parámetro de orden. Esta transición de fase cinética ocurre porque las partículas se mueven con velocidad absoluta constante, por lo cual —a diferencia de los sistemas físicos estándar— el momento neto de las partículas que interactúan no se conserva durante las "colisiones" (interacciones de alineación).

Casos descriptos en la bibliografía citada (esquema cualitativo):

- Distribución inicial aleatoria de direcciones.
- Para densidades y ruido bajos: las partículas tienden a formar grupos que se mueven coherentemente en direcciones aleatorias.
- Para densidades y ruido altos: las partículas se mueven al azar con alguna correlación.
- El caso más interesante: densidad alta y ruido bajo → el movimiento se ordena a escala macroscópica y todas las partículas tienden a moverse en una misma dirección, espontáneamente seleccionada.

`v_a` tiende a cero para el desorden total, y a 1 para partículas "polarizadas" (movimiento alineado).

## Diapositiva 45 — Autómatas Celulares: "Off-Lattice" — Bandadas de agentes autopropulsados

Ejemplos numéricos mostrados en la diapositiva:

- `v_a ≈ 0` para total desorden: `N = 300`, `L = 7`, `η = 2`.
- `v_a ≈ 1` para partículas "polarizadas": `N = 300`, `L = 5`, `η = 0.1`.

## Diapositiva 46 — Autómatas Celulares: "Off-Lattice" — Bandadas de agentes autopropulsados

Bajas densidades y bajo ruido: se tienden a formar grupos que se mueven coherentemente. Ejemplo: `N = 300`, `L = 25`, `η = 0.1`.

Se puede estudiar cómo varía `v_a`, por ejemplo, en función de `η`.

## Diapositiva 47 — Comentarios Finales

(Título de sección, sin texto adicional.)

## Diapositiva 48 — Autómatas Celulares: Informe

**Formato:**

- Redacción Técnica.
- Ecuaciones numeradas.
- Afirmaciones, Conclusiones, descripciones BASADAS en DATOS.
- Figuras: Referenciarlas, Leyendas, Ejes, Tamaño de Fuente...
- PROMEDIAR varias REALIZACIONES.
- Usar Latex (Ej.: www.overleaf.com).
- Ver documentación en ".../GuíasFormato/".

## Diapositiva 49 — Fin
