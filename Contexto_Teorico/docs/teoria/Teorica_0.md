# Teorica_0

*Fuente original: `Teorica_0.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion".*

## Dictado de la Materia

- Las teóricas son guías que deben ser complementadas con la bibliografía.
- Hay flexibilidad para profundizar en los temas de mayor interés. Método científico.
- En particular, el Trabajo Práctico Final, será a elección entre todos los temas vistos o temas relevantes propuestos por Uds.
- Se puede usar lenguaje de programación a elección.

- Los T.P. se realizarán en forma grupal (2 o 3 personas). Sumarse a uno de los grupos creados en campus.
- Recordar y usar este nombre del grupo para toda comunicación con la Cátedra.
- Las presentaciones de los T.P. son de asistencia obligatoria.
- Los T.P. se entregan como actividad en Campus, subiendo presentación en pdf con links explícitos a animaciones, código, e informe cuando se requiera.
- La implementación del Código y demás documentación debe ser original. Campus cuenta con detección automática de plagios. Hacer uso responsable de la IA.

- Consultar Cronograma y Reglamento completo (lectura obligatoria): ".../Contenido del Curso/Bienvenida/"
- Para Formato de Presentaciones e Informes consultar (lectura obligatoria): ".../Contenido del Curso/Bienvenida/Guías_Formato/"

## Sistemas y Modelos

### Sistema Real

Sistema Real → Modelo Físico-Matemático → Modelo / Implementación Computacional → Simulación

### Definición de Sistema

- Posee componentes relacionadas entre sí que funcionan como un todo.
- Pueden ser físicos o conceptuales y se caracterizan por tener límites, componentes, entradas, salidas y procesos que convierten las entradas en salidas.
- Presentan Observables Medibles y Cuantificables (entradas / salidas).
- Los sistemas también pueden incluir subsistemas e interactuar con otros sistemas y con el ambiente externo.

### Definición de Modelo (de un Sistema)

- Un Modelo es la abstracción de un Sistema "Real".
- Como tal es una aproximación/simplificación del Sistema y NO es único!!
- Hay variables medibles INPUT ( u(t) ) y OUTPUT ( y(t) ) del modelo.
  - INPUT: estímulo
  - OUTPUT: respuesta del modelo
- En general: `y(t) = g( u(t) )`. Este mapeo está dado por una función matemática en un modelo.

Un Objetivo Central de Modelar un Sistema: **Entender y Predecir su comportamiento.**

### Objetivos de la Teoría de Sistemas

- **Modelado y Análisis**: Entender cómo funciona el sistema.
- **Diseño**: De un sistema derivado que funcione con las mismas leyes.
- **Control**: Seleccionar un input para obtener un output deseado.
- **Evaluación de Funcionamiento**: Caracterización detallada del funcionamiento del sistema ante variadas condiciones operativas.
- **Optimización**: Encontrar las variables y parámetros que generan un cierto output objetivo.

### Caracterización de un Sistema

¿Qué es tomar DATOS de un sistema? Medir y Registrar, para un cierto muestreo temporal, los valores de las variables de INPUT y OUTPUT.

**IMPORTANTE:**

```
SIMULACIÓN
INPUT y Parámetros → Herramienta de ANIMACIÓN → Estado del sistema en función del tiempo: OUTPUT "PRIMARIO" ("Videos")
                    → Herramienta de ANÁLISIS → "Observables"
(Simulación off-line)
```

Ejemplo ilustrativo tomado de la bibliografía del curso (Soria et al., *Safety Science* 50 (2012) 1584–1588): se muestra la relación entre tiempos de evacuación de hormigas y la concentración de citronella (repelente), presentando el efecto "faster is slower" en el sistema de hormigas mediante una figura de valor medio y desvío estándar del tiempo de evacuación para cada concentración.

**Cadena de observables:**

- OUTPUT primario → Observable primario → Observable escalar.
- Para inputs y parámetros dados:
  - Observable primario: evoluciona en el tiempo (serie temporal). Ej.: Temperatura, Posiciones.
  - Observable escalar: no depende del tiempo. Ej.: Temperatura en el Equilibrio, Caudal (Q = ΔN / Δt), Nro. de Partículas, Curva de descarga.

### Definición de Modelo (de un Sistema)

```
System
INPUT u(t) → Modelo y = g(u) → OUTPUT
```

### El Estado de un Sistema

Es la información necesaria tal que y(t) queda unívocamente determinada por esta información y por u(t), para t ≥ t₀.

Definimos esta información como el estado x(t), donde sus componentes se denominan variables de estado.

La "Dinámica de un Sistema" está dada por las relaciones matemáticas del modelo entre los input (u(t)), los output (y(t)) y el estado (x(t)).

### El Espacio de Estados

**Definición: "Ecuaciones de Estado"**
Son el conjunto de ecuaciones necesarias para especificar el estado x(t) para t ≥ t₀, dados x(t₀) y u(t), t ≥ t₀.

**Definición: "Espacio de los Estados"**
Es el conjunto de todos los posibles valores que pueda tomar el estado.

El Sistema queda totalmente definido si tenemos las ecuaciones:

- Las "Ecuaciones de Estado" son en general ecuaciones diferenciales:

$$\dot{x}(t) = f(x(t), u(t), t), \quad x(t_0) = x_0$$

$$y(t) = g(x(t), u(t), t)$$

### Modelado con Espacio de Estados

```
u(t) → Modelo: ẋ = f(x, u, t), y = g(x, u, t) → y = g(u)
```

### Espacio de Fases

Las variables de estado: x(t) = ( x₁(t), x₂(t), x₃(t), ... )

Representación bidimensional: Espacio de Fases (ej.: x₁(t) vs. x₃(t)).

**Ejemplo — Oscilador Amortiguado**

Ecuación de Estado: $m\ddot{x} = -kx - \gamma\dot{x}$

Las variables de estado: Posición (x), velocidad (ẋ).

**Ejemplo — Oscilador de Duffing**

Ecuación de Estado: $m\ddot{x} = \alpha x - \beta x^3 - \gamma\dot{x} + \cos(\omega t)$

Las variables de estado: Posición (x), velocidad (ẋ).

## Clasificación de Modelos

### Modelos Estáticos y Dinámicos

- **Modelos Estáticos**: y(t) no depende de u(τ < t) (sin memoria). Ecuaciones Algebraicas. Ej.: Circuito Corriente Continua.
- **Modelos Dinámicos**: y(t) sí depende de u(τ < t), en particular de u(t = 0) (con memoria). Ecuaciones Diferenciales. Ej.: Oscilador armónico.

### Modelos Lineales

La idea de "linealidad" es que la suma de dos estímulos (input) produce la suma de sus respectivas respuestas (output): "Principio de Superposición".

$$g(a_1 u_1 + a_2 u_2) = a_1 g(u_1) + a_2 g(u_2)$$

En caso de linealidad las ecuaciones que definen al sistema/modelo se reducen a:

$$\dot{x}(t) = Ax(t) + Bu(t)$$
$$y(t) = Cx(t) + Du(t)$$

donde A, B, C y D son los parámetros del modelo.

### Modelos No-Lineales

No cumplen con el principio de superposición. El output no es proporcional al input.

**Dinámica No-Lineal: "Teoría del Caos"**

1. **Sensibilidad a las Condiciones Iniciales**: Infinitesimales diferencias en el Input producen outputs muy diferentes (las trayectorias en el espacio de fases difieren exponencialmente con el tiempo: exponente de Lyapunov).
2. **Transitividad Topológica**: Dos regiones cualquiera del espacio de fases se superpondrán en algún momento al evolucionar el sistema.
3. **Órbitas Periódicas Densas**: Cualquier punto del espacio de fases puede ser aproximado infinitesimalmente por una órbita periódica.

Ejemplo de espacio de fases: Atractor de Lorenz.

### Modelos de Estados Continuos y Discretos

- **Continuos**: Las variables de estado son números reales. "Ecuaciones Diferenciales".
- **Sistemas de Estado Discretos**: Las variables de estado son, por ejemplo: números enteros, ON / OFF, HIGH / MEDIUM / LOW.

### Modelos Deterministas y Estocásticos

- **Determinismo**: Demonio de Laplace. Conoce todas las condiciones iniciales y todas las leyes de la naturaleza; entonces puede determinar la evolución futura del universo (sistema).
- **Estocástico**: Si al menos uno de los inputs es random. Se considera al azar (ignorancia sobre algunos procesos). Se plantea el modelo en términos de probabilidades.

### Modelo Estocástico: Monte Carlo

- Algoritmos que involucran números aleatorios.
- Se toman promedios para reportar observables.
- Origen del nombre: "Casino de Monte-Carlo" (Mónaco).

**Ejemplos de aplicación:**

- Estimación de π por Monte Carlo.
- Interacción de radiación de neutrones con la materia.
- Difusión: Random Walk.

**Coeficiente de Difusión**

A partir de la trayectoria de un caminante aleatorio (random walk) se puede estimar el coeficiente de difusión D a través de la relación entre el desplazamiento cuadrático medio ⟨z²⟩ y el tiempo t: ⟨z²⟩ ∝ D·t.

**Importante:** Para calcular ese coeficiente, no alcanza una trayectoria. Se deben simular muchas y promediar el desplazamiento cuadrático.

- En 1 dimensión: ⟨z²⟩ = 2 D t
- En 2 dimensiones: ⟨z²⟩ = 4 D t
- En 3 dimensiones: ⟨z²⟩ = 6 D t

## Clasificación de Modelos y Simulaciones

### Basados en Tiempo Discreto

El sistema evoluciona cada un cierto tiempo discreto fijo (dt), generalmente pequeño respecto del tiempo total de la evolución del sistema.

Ejemplo: Integración numérica de una ecuación diferencial.

### Basados en Eventos

El sistema evoluciona en la medida que suceden "eventos", los cuales son instantáneos y producen un cambio en el estado del sistema.

**Ejemplo: Filas y Procesos (Teoría de Colas)**

Componentes:

- Entidades / Clientes que esperan por un Recurso / Servicio.
- Servidores que proveen el recurso por el cual esperan los clientes.
- La Fila es el espacio donde los clientes esperan ordenados.

Esquema: Arribo de Clientes → Fila → Servidor → Partida de Clientes.

- La Fila tiene: Capacidad (a veces infinita) y Comportamiento (p. ej. FILO, FIFO, etc.).
- Los eventos son el arribo o partida de un cliente.
- La variable de estado natural es la "Longitud de la Fila".

## Simulación vs. Animación

### El cinematógrafo

Sucesivas fotografías de un objeto en movimiento permiten reproducirlo al observar la secuencia obtenida, gracias a la persistencia de la imagen en la retina (~1/10 segundo).

En la Animación, las imágenes sucesivas son creadas para generar la ilusión de movimiento.

Imágenes creadas mediante:

- Dibujos (papel o computadora).
- Objetos o muñecos que se mueven cuadro a cuadro.
- Simulación.

### Simulación Computacional

Un programa que reproduce el comportamiento de un sistema:

- Sistema Físico. Ecuaciones diferenciales.
- Interacción de Agentes.
- Algoritmos. Heurística.

El output puede ser una Evolución Temporal u otro tipo de output (que se podría animar).

**¿Cuál es la diferencia?**

1. Una ANIMACIÓN puede estar generada a mano o puede estar generada a partir de una SIMULACIÓN.
2. Una SIMULACIÓN puede generar una sucesión temporal de datos susceptible de ser animados.

## Conceptos de Estadística y Regresiones

### Conceptos de Estadística

**Consejos previos:**

- Para análisis/postprocesamiento de datos salidos de la simulación, usar: Python, Matlab, R, Octave, ...
- No es recomendable analizar datos con planillas (Excel o similar).
- Para simulaciones usar Java, C(++), o similar.

**Temas:** Histograma, Distribución de Probabilidad, Función de Densidad de Probabilidad (PDF), Error Muestral - Error de Medición.

**Histograma**

- Distribución de Probabilidad: y_i = N_i
- Distribución de Probabilidad normalizada: y_i = N_i / N
- Densidad de Probabilidad (PDF: Probability Density Function): y_i = N_i / (dx_i · N), donde dx_i es el ancho del bin.

Notas:

- La PDF es continua; a partir de datos finitos se la puede aproximar.
- Su integral es igual a uno. Algún y_i particular podría ser mayor a uno (no está acotado).
- En cambio, en la distribución de probabilidad normalizada, todos los y_i son menores a uno.

**Error Muestral o de Medición**

Para simulaciones estocásticas, se repiten corridas (con distinta semilla) un cierto número de realizaciones y luego se reporta el observable como el promedio de los observables obtenidos.

Su error asociado, usualmente, es el desvío estándar (σ), si se trata de una distribución de Gauss, reportado como µ ± σ.

**IMPORTANTE:** Ejemplo de output promedio: L = 45.4 ± 0.3 cm. Si el error es 0.3 cm no tiene sentido informar mayor precisión en el valor de L. Por ejemplo, "L = 45.423457 ± 0.323428 cm" no sería un formato correcto.

El Error Muestral o de Medición se representa gráficamente mediante barras de error sobre el observable en función del input o parámetro. (Se ilustra nuevamente con el ejemplo de evacuación de hormigas de Soria et al., *Safety Science* 50 (2012) 1584–1588, mostrado más arriba.)

### Conceptos de Regresiones

Ajuste de datos con modelos teóricos (no con polinomios, "splines", o funciones arbitrarias).

Ejemplos de ajuste sobre datos que son promedios de simulaciones, en función de un input o parámetro:

- Modelo Exponencial.
- Modelo Senoidal.
- Modelo Lineal.

**Error del Ajuste**

Dados los datos (x_i, y_i) (promedios de simulaciones) y un modelo teórico f(x_i, c), se puede definir el error del modelo en función de un coeficiente c del mismo:

$$E(c) = \sum_i [y_i - f(x_i, c)]^2$$

El valor del coeficiente c\* que minimiza el error E(c) es el que produce el mejor ajuste del modelo a los datos. Se ilustra este concepto con el caso del Modelo Lineal.

**Reiteramos:** Los datos se ajustan con funciones que provienen de algún modelo teórico. No con funciones arbitrarias (no con polinomios de grado N, "splines", etc.)

---

FIN

Gracias por su atención!
