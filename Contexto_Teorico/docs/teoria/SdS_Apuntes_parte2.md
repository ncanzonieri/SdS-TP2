# SdS Apuntes parte 2

*Fuente original: `SdS Apuntes parte 2.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion".*

## Unidad 5 - Simulaciones Dirigidas por el Paso Temporal

Ahora vamos a tener un tiempo regular en el que vamos a actualizar el estado del sistema. El mismo consiste de N partículas que interactúan mediante fuerzas que en general dependen de la distancia entre ellas. Se contempla una integración numérica de las ecuaciones de movimiento. El tiempo avanza en cantidades discretas dt (el paso temporal). Las interacciones pueden ser de largo o corto alcance. En cualquier caso los "choques" no son instantáneos sino que tienen una duración de varios pasos temporales.

Este esquema es útil en el caso de partículas en contacto la mayor parte del tiempo:

- O bien interacciones de largo alcance.
- O bien de corto alcance pero con alta densidad.

También en los casos donde tiempo de vuelo (entre choques) << duración del choque.

### Desarrollo de Taylor

El espíritu es tomar una función y aproximarla en un entorno mediante un polinomio de un grado arbitrario. Vemos que a mayor orden, cada vez se acorta más la "distancia" a la función.

### Algoritmos de Euler

Para resolver las ecuaciones diferenciales de la evolución del sistema, vamos a tomar una serie de algoritmos. En primer lugar, podemos contemplar la fuerza y realizar un desarrollo directo, pero esto es poco preciso. En este caso se realiza un desarrollo de Taylor a partir del t conocido en un dt. Vemos por ejemplo que en el segundo término se tiene la velocidad, ya que es la derivada de la posición en función del tiempo.

Una modificación consiste en usar la velocidad ya actualizada en lugar de la del paso anterior. En este caso, se hace la misma cuenta (en cuanto a costo computacional) y se tiene una mejoría. El orden distinto en el cálculo nos brinda un poco más de precisión.

### Algoritmos de Verlet

Se hace una idea similar, utilizando un desarrollo de Taylor pero se contempla hasta delta t al cubo. Se puede hacer un "truco": la idea central es escribir la posición de la partícula ri en los instantes t+Δt y t−Δt. Cada una de estas expresiones se expande alrededor de t, incluyendo términos de velocidad, fuerza (aceleración) y derivadas de orden superior. Luego, al sumar ambas expresiones, los términos lineales en la velocidad (±Δt·vi(t)) se cancelan, al igual que los términos de tercer orden, quedando únicamente los términos de posición en t, las aceleraciones multiplicadas por Δt² y un error de orden O(Δt⁴).

Este procedimiento es ingenioso porque elimina la dependencia directa de la velocidad y permite avanzar la posición usando solo las posiciones previas y las fuerzas actuales, garantizando una integración más estable y con error global del orden Δt². Por eso el método de Verlet es muy popular en simulaciones de dinámica molecular: es sencillo, conservativo y no requiere almacenar ni calcular explícitamente las velocidades en cada paso.

En la variante **Leap-Frog** (viene del juego en que una persona se pone en cuclillas y la otra la salta por arriba) se calculan las velocidades y posiciones en tiempos desfasados. Esto lo hacemos porque queremos "engañar" al sistema. En lugar de tomar un paso dt, estamos tomando un paso dt/2. Achicar el paso mejora la aproximación, como vimos en el desarrollo de Taylor. No lo achicamos numéricamente porque si tenemos dt muy chicos, vamos a tener que hacer muchísimos más pasos.

Las desventajas son que se tienen estas dos variables en tiempos distintos, por lo que se debe hacer una transformación en la velocidad con los promedios para ajustarla.

Otra variante es **Velocity-Verlet**, donde también se hacen pasos intermedios con dts más pequeños. La idea es avanzar primero la posición usando la velocidad actual y la aceleración conocida, luego calcular la nueva aceleración a partir de la fuerza en el tiempo actualizado, y finalmente corregir la velocidad combinando la aceleración inicial y la final. Esto se interpreta como un esquema en dos pasos: primero se calcula una velocidad intermedia que sirve para mover la partícula, y después, con la fuerza en el nuevo tiempo, se termina de ajustar la velocidad. De esta forma se logra un algoritmo estable, que conserva bien la energía en el tiempo y que además entrega velocidades confiables, algo que el Verlet original no hacía directamente.

Otro algoritmo es el de **Beeman**, donde se evalúa la función aceleración en distintos pasos. La idea principal es que no solo se usan la posición, velocidad y aceleración en el tiempo actual, sino también la aceleración del paso anterior. De este modo se incorpora más información histórica, lo que reduce el error en el desarrollo de Taylor.

En la práctica, Beeman utiliza una combinación lineal de las aceleraciones presente y pasada para predecir la nueva posición. Una vez calculada la posición en el nuevo tiempo, se obtiene la aceleración correspondiente y se corrige la velocidad con un promedio ponderado de las aceleraciones pasada, presente y futura.

La ventaja es que el error en las posiciones se mantiene del orden de Δt⁴, mientras que el de las velocidades mejora respecto a Verlet clásico y Velocity Verlet, quedando en el orden de Δt³. Esto hace que el método conserve mejor las cantidades físicas a lo largo del tiempo, como la energía total en simulaciones de dinámica molecular. Otra ventaja es que podríamos contemplar aceleraciones que dependan de la velocidad, cosa que antes no hacíamos, era en base a las posiciones.

### Algoritmos Predictor-Corrector

La idea es predecir las posiciones y velocidades en un tiempo futuro para conocer las fuerzas futuras y así hacer las correcciones a nuestras predicciones. Tomemos el primer caso, el **Algoritmo Euler Predictor-Corrector**.

El **Algoritmo Gear Predictor-Corrector** consiste en realizar un desarrollo de Taylor de un orden arbitrario de derivadas. El superíndice p significa que es predicha, y el subíndice q es el orden de derivada.

El delta R va a ser el factor de corrección. El alpha es un número llamado coeficiente del predictor Gear, se encuentra en una tabla y depende del integrador. En base al orden tomado, se debe ir a ella y tomar el valor correspondiente.

- Para el caso r2 = f(r), las fuerzas solo dependen de las posiciones.
- Para el caso r2 = f(r, r1), las fuerzas dependen de las posiciones y las velocidades.

### Elección del Paso Temporal

Es importante diferenciar el dt del sistema y el que se usa para realizar los guardados de datos de la simulación, es decir, el estado del sistema.

Si es muy corto, dijimos que la simulación va a requerir demasiadas iteraciones. Si es muy largo, se iban a tener pérdidas o incluso inconsistencias en las posiciones de las partículas. Entonces, vamos a intentar cuantificar el error que estamos cometiendo en la resolución del sistema.

Un caso simple es comparar con la solución analítica. Un caso realista es, si el sistema es conservativo, definir una métrica basada en la conservación de la energía. Para los sistemas no conservativos podemos repetir simulaciones con dts cada vez menores hasta que los resultados cambien menos que un dado error.

### Casos de Estudio

- **Oscilador amortiguado.**
- **Gas de Lennard-Jones.**
- **Sistema gravitatorio**: si tuviéramos partículas puntuales con masa, al tener distancias muy chicas nos podría romper todo el sistema y dar una fuerza muy grande, por lo que hay que prestar atención a la aclaración del TP.

Recordemos que las fuerzas se suman. Antes de sumar Fuerzas, para cada partícula, conviene proyectar las fuerzas normal y tangencial (generadas por cada una de las demás partículas en contacto) en las componentes cartesianas (x,y). Vamos a tener que resolver 3n sistemas. Finalmente la fuerza sobre cada partícula i debido a la interacción con las demás partículas (j) resulta de la suma correspondiente.

## Unidad 6 - Sistemas Granulares

Los medios granulares son sistemas de partículas del orden macroscópico (granos de arena por ejemplo o incluso polvo). Una de las principales características es que disipan energía al entrar en contacto. Esto se debe a que presentan interacciones a través de fuerzas de contacto normales (deformación viscoelástica) y tangenciales (rozamiento). Tienen características muy particulares que los distinguen de sólidos, líquidos y gases.

Un ejemplo es el flujo granular gravitatorio en silos.

### Propiedades

La **ley de Janssen** establece que en los medios granulares, a diferencia de por ejemplo el agua, la presión dentro del medio granular no depende de la altura de la columna, sino que crece asintóticamente con la profundidad.

Otra relación empírica es la **ley de Beverloo**, que establece que el caudal Q constante de un silo se obtiene por análisis dimensional, es decir que se deduce sólo a partir de las unidades físicas de las variables relevantes, sin resolver toda la mecánica granular. Cuanto más diámetro, mayor va a ser el caudal, que se mide en cantidad de partículas por unidad de tiempo. El parámetro c es una constante empírica adimensional que corrige el tamaño efectivo del orificio.

### Simulaciones en Medios Granulares

Este tipo de sistemas son densos, es decir que las partículas están en contacto constantemente, por lo que tchoque >> tvuelo. Se utiliza un método de elemento discreto, la dinámica molecular para granulares.

Se considera a las partículas como círculos y se permite que haya superposición entre dos de ellas. Es una forma de representar algo que en la realidad no sucede: en el mundo real se deforman y luego intentan volver a su forma original.

Podemos considerar un límite físico y también contemplar cierta superposición, definiendo las variables geométricas correspondientes. Entonces, para hacer las ecuaciones se integran numéricamente las ecuaciones de movimiento acopladas: las traslaciones y las rotaciones.

Para partículas circulares, podemos dejar de lado las rotaciones, y el resultado será similar. En este caso, vamos a tener dos direcciones fundamentales: la normal (que apunta desde el centro de masa i hasta el j) y la tangencial, en la cual se van a producir los rozamientos.

Para las paredes esto es análogo, pero tiene fijas las direcciones tangenciales y normales. No hay que calcularlas todo el tiempo como sí es el caso de las partículas.

La suma de fuerzas se aplica de igual manera para las de corto alcance y las de largo, como ya vimos en unidades anteriores. En este sistema funciona bien la idea de Cell Index Method, para ver quiénes están en contacto con quiénes.

Antes de sumar fuerzas, para cada partícula, conviene proyectar las fuerzas normal y tangencial (generadas por cada una de las demás partículas en contacto) en las componentes cartesianas (x,y). Finalmente la fuerza sobre cada partícula i debido al contacto con las demás partículas, paredes u obstáculos (j) resulta de esa suma.

Para elegir el paso temporal, se debe considerar el método de integración. En este caso, a diferencia de la unidad anterior, no vamos a utilizar la conservación de la energía, por lo que tenemos que usar el tercer método de la unidad anterior (repetir con dts decrecientes). Es importante establecer la diferencia entre el paso Δt de la simulación y el Δt2 para guardar el estado del sistema.

### Partículas de Formas Arbitrarias

Para el caso de partículas más complejas, se utiliza el concepto de **esferopolígonos**, que es un método para simular interacciones disipativas y conservativas entre dos cuerpos rígidos con formas complejas en dos dimensiones.

La idea matemáticamente es utilizar una **suma de Minkowski**, que establece que dados dos conjuntos de puntos P y Q en un espacio Euclídeo, esta suma está dada por P+Q={ x+y | x ∈ P, y ∈ Q}. Esto es equivalente a arrastrar un conjunto alrededor del perfil del otro.

La fuerza de interacción entre dos partículas i, j considera los solapamientos entre vértices (Vi) de un polígono y lados del otro (Ej) y viceversa (Vj y Ei).

## Unidad 7 - Simulación de Multitudes

Un grupo de personas caminando pueden relacionarse de dos maneras, normal (o cooperativa) o competitiva (o de stress). En condiciones normales o cooperativas, cada persona prioriza confort y seguridad: mantiene su velocidad deseada sin apuro, respeta distancias y anticipa maniobras. Emergen flujos ordenados (carriles espontáneos, "cremallera" en cuellos de botella) y la relación flujo–densidad es estable; en modelos, usamos fuerzas suaves y tiempos de reacción más largos.

En condiciones competitivas o de estrés, la meta es salir rápido: sube la velocidad deseada, bajan las distancias y aparecen empujes y bloqueos. Surgen arcos en puertas, oscilaciones stop-and-go, "herding" y el efecto faster-is-slower (más prisa, menor caudal). Los modelos requieren términos de contacto/fricción más fuertes y tiempos de relajación cortos. Elegir el régimen guía la calibración y las métricas que validamos.

### Condiciones Competitivas o de Estrés

En las condiciones competitivas, podemos tomar como ejemplo la evacuación de un recinto. Cuanto más se apuran a salir, mayor fuerza ejercen sobre la salida. Vemos que con el tiempo tienden a formarse como una especie de arcos. Esto de que cuanto más se apuran, más tardan en salir se conoce como **Faster Is Slower**. Hay un punto óptimo de velocidad y salida.

Lo primero que se hizo para estos casos fue simulaciones, pero faltaba verificar si esto efectivamente sucede en la realidad. Se experimentó primero con un silo en 2D con un plano inclinado. Se encontró que para un ángulo determinado, se llega a un punto óptimo. El τ es la diferencia de tiempo entre la salida de una partícula y la siguiente, y es proporcional al tiempo de evacuación. Se puede ver entonces que el fenómeno de Faster Is Slower existe en medios granulares.

Luego, se probó con hormigas, pero no se obtuvo resultado favorable, por lo que se pasó a ovejas. Se les abre una puerta luego de una noche sin comer, por lo que se comportan competitivamente. Se puede ver que sí se cumple el fenómeno de FIS, tomando la velocidad inicial grupal vs el τ. Las velocidades varían según las temperaturas (low y high), ya que las ovejas se comportan de distinta manera en distintas épocas del año. Tienden a moverse más rápido en invierno.

Finalmente, se experimentó con humanos variando el grado de competitividad. Se puede ver que hay una mayor continuidad en los fotogramas cuando la competitividad es baja.

### Condiciones Normales o Cooperativas

El primer experimento consistió en un sistema de humanos voluntarios que tenían que caminar hacia marcas al azar. Ante eventos de choque hay aceleraciones o desaceleraciones grandes, así como cambios de dirección bruscos. La idea es justamente ver cuál de estas dos opciones toman los humanos para evitar una colisión.

### Observables en Dinámica Peatonal

En la dinámica peatonal se tienen dos observables fundamentales:

- El **diagrama fundamental**, que es la relación entre la densidad y la velocidad.
- El **caudal específico** = Peatones / (Tiempo × Ancho de Puerta).

Un ejemplo experimental del diagrama fundamental muestra que al haber mayor densidad, se baja la velocidad para evitar colisiones. Podemos pensarlo como en una autopista cuando está congestionada.

La **capacidad del sistema** es el punto máximo del caudal específico. El gráfico de caudal específico en función de la densidad tiene forma de campana, y el punto máximo es esa capacidad c.

Las regulaciones adoptan un caudal específico de 1.33 p/m/s (con p siendo personas), ya que de los datos experimentales se obtienen valores de 1.25 a 2.0 p/m/s. Para condiciones normales se asume caudal de salida proporcional al ancho de salida.

### Modelos Microscópicos

Se llaman microscópicos porque tienen en cuenta partícula por partícula. Se los puede clasificar en:

- **Continuos / Basados en Fuerzas**: Descripción continua del espacio.
  - Partículas Newtonianas.
  - Posición y Velocidad en el Continuo.
- **Discretos / Basados en Reglas**: Son tipo autómatas celulares, hay una discretización del espacio.
  - Espacio Discretizado en una Grilla.
  - Transición de estados basados en Reglas.
  - Autómatas Celulares.

Existen tres modelos que vamos a usar.

#### Social Force Model

Tenemos una ecuación diferencial para cada partícula, al igual que en sistemas granulares. Se resuelve con los mismos métodos de integración que vimos en el TP anterior.

Se tiene una fuerza de contacto, una fuerza social (intenta evitar colisiones mediante fuerzas de largo alcance — debe ser descartada) y la de deseo, que es la de autopropulsión de la partícula que quiere ir a un punto determinado.

En la fuerza de contacto, la función g vale cero si no hay contacto, porque justamente es la fuerza que ocurre cuando dos partículas están en contacto o con un cierto overlap.

La fuerza social, como se dijo, va a ser descartada porque se ejerce una fuerza en las partículas en la puerta que en la realidad no existe.

La fuerza de autopropulsión necesita un target, es decir un punto al cual dirigirse. La fórmula contempla también una velocidad deseada. Notemos que si la velocidad deseada y la actual, así como la dirección, son iguales, la fuerza será cero. El τ es una constante que representa el tiempo que tarda una persona parada en llegar a una velocidad deseada desde el reposo.

Este modelo representa cualitativamente por ejemplo la formación de carriles en un espacio donde hay dos direcciones de movimiento.

#### Autómata Celular Bionics-Inspired

Se llama así porque está inspirado en hormigas. Se toma una grilla cuadrada, y cada celda puede estar ocupada o no por un peatón, que NO se puede mover en diagonal. Las vecinas a las que sí se puede mover contienen las probabilidades.

El **campo estático (S)** tiene que ver con la geometría, pero como este no varía, está fijo durante la simulación. Las probabilidades suben cuando se está más cerca de la puerta.

El **campo dinámico (D)** se modifica por la presencia de partículas. Representa un rastro visual dejado por partículas que pasaron antes. El campo dinámico tiene su propia dinámica de difusión y decaimiento.

A t = 0 el campo es cero: Dij = 0. Si una partícula pasa del sitio (i,j) a uno vecino, Dij → Dij + 1. En cada paso, el campo dinámico D decae con una probabilidad δ ∈ [0,1] y difunde con probabilidad α ∈ [0,1] hacia una de sus celdas vecinas. D = D(t, δ, α).

Para actualizar el autómata:

1. El campo dinámico D es modificado de acuerdo a las reglas de decaimiento y difusión.
2. Para cada partícula la probabilidad pij para moverse a una celda desocupada (i,j) se calcula según una fórmula de probabilidad.
3. Cada partícula elige una celda a la cual intentar moverse de acuerdo a las probabilidades (Pij).
4. Si hay conflicto (dos partículas eligieron la misma celda), se resuelve probabilísticamente. La partícula elegida ejecuta el movimiento.
5. Se incrementa D según los movimientos de las partículas.

Estas reglas se aplican a todas las partículas en el mismo paso temporal, es decir se ejecutan en forma sincronizada.

#### Contractile Particle Model

Es una especie de híbrido porque tiene reglas pero vive en el continuo. Las reglas son arbitrarias, al no tener fuerza no se deben resolver ecuaciones. La partícula puede oscilar entre dos radios, donde el radio mínimo es el mínimo físico y el máximo es el espacio personal. La velocidad es una función del radio, ya que si se está en el radio mínimo, la partícula no se va a mover.

Cuando no hay contacto, se aplican unas ecuaciones de movimiento y de variación del radio. Cuando hay contacto, se colapsan los radios al mínimo durante un paso dt y aparece una velocidad de escape.

Como no hay fuerzas que se estén sumando, el caudal no depende de la cantidad de partículas que tenga el sistema. Además, es 50 veces más rápido al no tener que hacer esa cuenta.

Variando el número de partículas, se estudian distintas densidades y se mide la velocidad promedio para construir el diagrama fundamental. Una variación en los parámetros permite ajustar el modelo a un caso experimental.

> **Nota del apunte original**: "A partir de acá no sirve para el TP."

### Modelos de Navegación

El siguiente modelo trae ahora la elusión de obstáculos, mediante las mismas fuerzas que vimos anteriormente. Lo que se hace es tomar un target temporario para no chocar contra el obstáculo.

### Data-Driven Simulation

La simulación data-driven no parte de ecuaciones de interacción prefijadas sino de datos reales de trayectorias. Para cada agente i se construye un estado local si(t) con variables observables: posiciones y velocidades relativas de los vecinos dentro de su campo de percepción y su objetivo (dirección/puerta). Con ese estado actual se buscan en el dataset situaciones parecidas —vecinos más cercanos en ese espacio de estados— y se imita la respuesta que allí se observó: la nueva velocidad o el desplazamiento Δxi que las personas reales tomaron en contextos similares. En la práctica suele usarse k-NN o una pequeña regresión entrenada sobre muestras (s, Δx), con un blending para suavizar.

La ventaja es que el movimiento resultante hereda realismo (gestos de evitación, carriles, ceder el paso) sin ajustar a mano fuerzas o parámetros; además se adapta a distintos contextos si el dataset los contiene. La limitación es de cobertura: si el estado actual cae fuera de lo observado, la predicción puede degradarse; por eso conviene curar datos (a partir de video y tracking), normalizar los estados y restringir el radio de percepción para mantener la similitud significativa. En resumen, simular es consultar y reproducir conductas humanas previamente medidas, no resolver una dinámica analítica.

### Software de Simulación

Existen distintos niveles de complejidad en la navegación peatonal, según el software.

Los inputs generales de estos softwares son:

- Geometría.
- Ocupación / Demanda (caudales de llegada).
- Ubicación de Servidores y Tiempo de Procesos.
- Matriz Origen-Destino. Lista de tareas.
- Plan de Evacuación.

Los observables son:

- Tiempos de tránsito y de Evacuación.
- Tiempos de espera en procesos.
- Curvas de Población.
- Mapas de densidad.
- Animaciones 2-D.
- Ocupación por sectores.
- Etc.

---

*Nota de extracción: el documento original incluye figuras, diagramas y expresiones matemáticas renderizadas como imágenes/fórmulas que no se transcriben literalmente aquí (el extractor de texto del proyecto no captura ecuaciones ni gráficos); se describe su contenido en el texto circundante tal como aparece en la fuente. El texto verbal se preservó de forma completa.*
