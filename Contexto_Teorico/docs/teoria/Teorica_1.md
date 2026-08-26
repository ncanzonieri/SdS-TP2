# Teorica_1

*Fuente original: `Teorica_1.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion".*

## Sistemas Físicos

### Sistemas de Muchas Partículas

- Problema de 1 cuerpo: Integrable. Tiene solución analítica.
- Problema de 2 cuerpos: Integrable. Tiene solución analítica.
- Problema de 3 cuerpos: No Integrable. Sin solución analítica. Se integra numéricamente.
- Problema de N cuerpos: Se integra numéricamente. Dinámica Molecular.
- Si N es muy grande: Mecánica Estadística - Teoría Cinética.

### Sistemas de Muchas Partículas. Ejemplos

- **Interacción Gravitatoria** — Galaxia M101: ~170.000 años luz de diámetro, ~10¹² estrellas.
- **Flujos Granulares.**

### Materia Activa. Definición

- Está compuesta por unidades auto-propulsadas, capaces de convertir energía almacenada o del medioambiente en movimiento sistemático.
- El ingreso de energía al sistema se da en forma local, al nivel de la unidad/partícula/agente, y no en forma macroscópica a través de los límites del sistema.
- Propiedades de sistemas fuera del equilibrio:
  - Estructuras emergentes con comportamiento colectivo cualitativamente diferente al de los componentes individuales.
  - Transiciones orden-desorden.
  - Formación de patrones en las escalas mesoscópicas.
  - Etc.

### Materia Activa. Ejemplos

- **Materia Viva**: Turbulencia de bacterias, cardumen de sardinas, bandada de estorninos (starlings).
- **Materia Viva: Peatones Simulados — Social Force Model**
  - Una ecuación diferencial para cada peatón lleva a un sistema de ecuaciones diferenciales acopladas.
  - Métodos de Dinámica Molecular.
  - $m_i\ddot{r}_i = F_{GRANULAR} + F_{SOCIAL} + F_{DRIVING}$
- **Materia Viva: Peatones "Freezing by Heating"**
  - $\langle F_{FLUCTUATION} \rangle = 0$, $\text{STD}(F_{FLUCTUATION}) = \theta$
  - $m_i\ddot{r}_i = F_{GRANULAR} + F_{SOCIAL} + F_{DRIVING} + F_{FLUCTUATION}$
- **Materia Viva: Peatones Egoístas "Faster is Slower"**
  - Gráfico: Tiempo Medio de Evacuación (para 200 personas, en segundos) vs. Velocidad Deseada (m/s), mostrando un mínimo/comportamiento no monótono en el rango 0–8 m/s (aprox. 60–150 s).
- **Materia Viva: Hormigas — Egreso ante Emergencia**
  - Comparación 100% Hormigas vs. 100% Humanos.
  - En hormigas: "Faster is Faster!" (a diferencia del caso humano).
- **Materia Viva: Comportamiento Emergente**
  - Agentes "suicidas" cuya prioridad de supervivencia no es el individuo (insectos sociales) → beneficio para el conjunto.
  - Agentes "egoístas" cuya prioridad de supervivencia es el individuo (todos los animales que no sean insectos sociales) → perjuicio para el conjunto.
  - Caso ilustrativo: egreso por puerta angosta.
- **Aplicaciones en Cine.**

### Concepto de Comportamiento Emergente

- Muchos agentes simples.
- Interacciones sencillas.
- Emergen espontáneamente patrones o comportamientos complejos.
- La escala espacial característica de los mismos es mayor que la escala de 1 agente.
- (Ej.: Materia activa, Insectos sociales, Sistema nervioso, etc.)

## Muchas Partículas Interactuantes

- Todos los sistemas vistos hasta ahora consisten en partículas que interactúan entre sí de a pares y en función de las distancias.
- Para interacciones de largo alcance se deben calcular las distancias entre todas las partículas.
- Para interacciones de corto alcance solo son relevantes las distancias a los vecinos cercanos.

### Detección de Vecinos — Lista de Vecinos: "Cell Index Method" (CIM)

- El método de Fuerza Bruta mide las distancias de todas las partículas con todas las partículas. La complejidad crece ~N².
- Usando el CIM la complejidad crece linealmente con N (a densidad constante). (Si se aumenta la densidad, crece cuadráticamente pero con un prefactor menor.)
- Referencia: *"Computer simulation of liquids"*, Allen & Tildesley, 1987.

**¿Qué se quiere averiguar?** La identidad de las partículas que están a distancia menor a r_c.

**Idea general del CIM**: Consiste en dividir el espacio en celdas, asignar las partículas a las celdas según su ubicación, y calcular distancias solo entre partículas de celdas vecinas y la propia.

**Elección del tamaño de celda**: Si el dominio tiene lados de longitud L y hay M×M celdas, entonces L/M es la longitud del lado de cada celda.

- Si M es demasiado grande, L/M puede resultar menor que r_c, lo cual sería incorrecto para el radio de interacción r_c.
- Al disminuir M de forma que L/M > r_c (radio de interacción de las partículas), M resulta correcto para ese r_c.

**Observaciones adicionales:**

- Identificar a qué celdas pertenecen todas las moléculas es rápido y se podría hacer en todos los pasos temporales.
- Por simetría (d_ij = d_ji): para cada celda (por ejemplo la 13) alcanza con mirar solo las 4 celdas vecinas (por ejemplo 9, 14, 19 y 18), lo cual reduce a la mitad el tiempo de cálculo.
- Condiciones Periódicas de Contorno: por ejemplo, la partícula en la celda 10 puede ser vecina de la que está en la celda 6, con una distancia del orden de L/M.

**Ejemplo de Lista de Vecinos:**

| id de la partícula "i" | ids de las partículas cuyas distancias son menores que r_c |
|---|---|
| 1 | 5, 17, 32 |
| 2 | - |
| 3 | 8, 12 |
| 4 | - |
| 5 | 1, 6, 25, 104, 67 |
| ... | ... |

### Lista de Vecinos — Trabajo Práctico

- Implementar el "Cell Index Method".
- Estudiar la eficiencia del algoritmo en función del tamaño de las celdas de la grilla.
- Pensar un criterio para definir cantidad y tamaño de celdas en función del área y la densidad de las partículas.
- Para testear:
  - Generar N partículas con radio en forma random, con distribución uniforme, dentro del área cuadrada de lado L.
  - Se deberá poder determinar los vecinos cuya distancia borde-a-borde sea menor a r_c, para L y M dados (N y estos últimos 3 parámetros como inputs).
  - Comparar con el método de fuerza bruta (que mide, para cada partícula, la distancia a todas las demás partículas).
- Para testear: usar un Visualizador de Vecinos.

*FIN de "Cell Index Method".*

## Reglas Generales de Simulaciones

**IMPORTANTE:**

```
SIMULACIÓN
INPUT y Parámetros → Herramienta de ANIMACIÓN → Estado del sistema en función del tiempo: OUTPUT ("Videos")
                    → Herramienta de ANÁLISIS → "Observables"
```

### Animaciones

- La animación es un resultado (postproceso) separado de la Simulación.
  - El simulador genera como outputs archivos con posiciones y velocidades.
  - Luego el visualizador levanta esos datos y genera la animación (exportar a un .avi).
- Visualizadores recomendados:
  - Matlab / Octave
  - Matplotlib (Python)
  - Ovito (www.ovito.org) — admite formatos de archivo similares a los descriptos.
  - Otro.

**Resultados** = Herramienta de ANIMACIÓN ("Videos") + Herramienta de ANÁLISIS ("Observables").

### Formato de archivos para guardar simulaciones y su posterior visualización

**Info Dinámica** (el nro. de fila es la identidad de la partícula 1, 2, ..., N):

```
t1
x1 y1 vx1 vy1   (partícula 1)
x2 y2 vx2 vy2   (partícula 2)
....
xN yN vxN vyN   (partícula N)
t2
x1 y1 vx1 vy1   (partícula 1)
x2 y2 vx2 vy2   (partícula 2)
....
xN yN vxN vyN   (partícula N)
```

**Info Estática** = constante en el tiempo (el nro. de fila es la identidad de la partícula 1, 2, ..., N):

```
N     (Heading con el Nro. total de Partículas)
L     (Longitud del lado del área de simulación)
r1 c1 (radio y color de la partícula 1)
r2 c2 (radio y color de la partícula 2)
....
rN cN (radio y color de la partícula N)
```

### Reglas Generales Trabajos Prácticos — Entregables (para TP2 en adelante)

- Código Fuente de las simulaciones implementadas.
- Soporte de la Presentación Oral en formato *.PDF (solo con imagen ilustrativa de las animaciones y un link visible).
- Las Animaciones solo se muestran durante la presentación oral, pero no deben ser entregadas ni como archivo independiente, ni insertadas en el *.PDF.

## Presentaciones — Formato (para TP2 en adelante)

**Estructura sugerida (para 3 personas, 3 partes, tiempo ≤ 15 minutos, orden de exposición aleatorio):**

- Intro (< 1 min): Descripción del Sistema y Modelo Matemático.
- Implementación (~3 min): Arquitectura, UML, pseudocódigo.
- Simulaciones (~2 min): Configuración del sistema particular a simular, parámetros fijos y variables, definición de outputs y observables.
- Resultados (~8 min): Animaciones, Estudio paramétrico/estadístico.
- Conclusiones (< 1 min).

**Formato:**

- Numerar las diapositivas.
- Usar carátulas/separadores para cada sección.
- Estructurar de forma coherente títulos y subtítulos.

**Algunos consejos** (citando y basándose en James C. Garland, *"Advice to Beginning Physics Speakers"*, Physics Today, julio de 1999):

- Usar un mínimo de ecuaciones; no escribir mucho texto.
- Cumplir con el tiempo establecido.
- Practicar la charla previamente: la práctica ayuda a fluir la exposición y a evitar quedar atrapado en líneas de razonamiento confusas; se recomienda no escribir el discurso para luego leerlo o recitarlo, algo mal visto en el ámbito científico (a diferencia de otras disciplinas). El artículo original también trata brevemente sobre otros aspectos prácticos de dar una charla (por ejemplo, cómo presentarse ante el público y vestimenta apropiada), que no se detallan aquí por tratarse de una cita de una fuente externa (Physics Today) — ver el artículo original *AdviceToBeginningPhysicsSpeakers.pdf* en el Proyecto para el texto completo.
- Interactuar con la audiencia:
  - Hablar alto.
  - Mirar a los ojos a personas en distintos sectores de la sala.
  - No mirar el piso o las paredes.
- Al final, ante las preguntas de la audiencia:
  - Permitir que quien pregunta termine la pregunta.
  - Repetir la pregunta en voz alta para que todos la oigan.
  - Dar respuestas breves, sin hablar de otros temas relacionados.
- Con varios expositores:
  - Cada uno tiene un tiempo definido.
  - No superponerse.
  - Responder preguntas por orden.

---

Sistemas Físicos — FIN
