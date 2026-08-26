# SdS Apuntes parte 1

*Fuente original: `SdS Apuntes parte 1.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion".*

## Unidad 1 - Sistemas y Modelos

### Sistema

Un sistema posee componentes relacionadas entre sí que funcionan como un todo. Puede ser físico o conceptual y se caracteriza por tener límites, componentes, entradas, salidas y procesos que convierten las entradas en salidas. Presentan Observables Medibles y Cuantificables (entradas / salidas). Los sistemas también pueden incluir subsistemas e interactuar con otros sistemas y con el ambiente externo.

Un modelo es la abstracción de un sistema "real". Como tal es una aproximación/simplificación del Sistema y NO es único. Hay variables medibles INPUT (u(t)) y OUTPUT (y(t)) del modelo.

- INPUT: estímulo
- OUTPUT: respuesta del modelo

En general: y(t) = g (u(t)). Este mapeo está dado por una función matemática en un modelo. Un objetivo central de modelar un sistema es entender y predecir su comportamiento.

Los objetivos de la teoría de sistemas son:

- **Modelado y Análisis**: Entender cómo funciona el sistema.
- **Diseño**: De un sistema derivado que funcione con las mismas leyes.
- **Control**: Seleccionar un input para obtener un output deseado.
- **Evaluación de Funcionamiento**: Caracterización detallada del funcionamiento del sistema ante variadas condiciones operativas.
- **Optimización**: Encontrar las variables y parámetros que generan un cierto output objetivo.

### Caracterización de un Sistema

Tomar datos de un sistema consiste en medir y registrar para un cierto muestreo temporal los valores de las variables de INPUT y OUTPUT. Una simulación offline se ejecuta en una computadora sin interactuar en tiempo real.

El flujo del proceso es el siguiente:

1. **Inputs y parámetros**: condiciones iniciales y configuraciones del sistema que querés simular.
2. **Simulación**: el modelo procesa esos inputs y genera cómo evoluciona el sistema en el tiempo.
3. **Output primario**: el "estado del sistema en función del tiempo", que es la información cruda de la simulación (por ejemplo, colas, tiempos de espera, niveles de inventario, etc.). Ese output se puede usar para:
   - a. Herramientas de análisis: generan indicadores o métricas ("observables") que sirven para evaluar el desempeño del sistema.
   - b. Herramientas de animación: producen representaciones visuales o "videos" para entender mejor el comportamiento dinámico.

En la caracterización, se puede dibujar un gráfico que muestra cómo estudiar el comportamiento del sistema cambiando parámetros de entrada.

El eje X es el "input o parámetro" (algo controlable, como velocidad de servicio, capacidad, etc.) y el eje Y es lo "observable" (la medida de desempeño resultante, como tiempo medio de espera). Las barras de error indican la variabilidad (incertidumbre estadística) de cada punto.

Siguiendo con el análisis de los resultados de una simulación, podemos ver el siguiente esquema:

**Output primario**: es la serie temporal de las variables del sistema (por ejemplo, velocidades individuales de partículas, número de clientes en cola cada segundo, etc.). Es la información más detallada.

**Observable primario**: es una variable que evoluciona en el tiempo y resume el comportamiento del sistema (por ejemplo, temperatura promedio). En el gráfico, se ve cómo esa variable tiene una respuesta transitoria (cuando el sistema todavía se está estabilizando) y luego llega a una respuesta permanente (equilibrio).

**Observable escalar**: es un valor único que no depende del tiempo, como la temperatura en equilibrio o el tiempo medio de espera. Es lo que se usa para comparar configuraciones del sistema, dado un conjunto de inputs y parámetros.

### Estado de un Sistema

El estado de un sistema es la información necesaria tal que y(t) queda unívocamente determinada por esta información y por u(t), t ≥ t0. Definimos esta información como el estado x(t), donde sus componentes se denominan variables de estado.

La "Dinámica de un Sistema" está dada por las relaciones matemáticas del modelo entre los input (u(t)), los output (y(t)) y el estado (x(t)). Las ecuaciones de estado son el conjunto de ecuaciones necesarias para especificar el estado x(t) para t ≥ t0 dados x(t0) y u(t), t ≥ t0. El espacio de estados es el conjunto de todos los posibles valores que pueda tomar el estado.

Las "Ecuaciones de Estado" son en general ecuaciones diferenciales. El Sistema queda totalmente definido si tenemos las ecuaciones correspondientes.

### Clasificación de Modelos

Podemos clasificar los modelos según el uso de memoria en:

- **Modelos Estáticos (sin memoria)**: la salida y(t) en un instante depende solo de los valores actuales de la entrada u(t). No tienen memoria: el sistema "olvida" el pasado; no importa qué ocurrió antes (u(τ<t)). Ecuaciones algebraicas: se describen con relaciones directas (no hay derivadas ni integrales). Ejemplo: un circuito de corriente continua, donde la corriente depende instantáneamente de la tensión aplicada (I=V/R).
- **Modelos Dinámicos (con memoria)**: la salida y(t) sí depende de lo que pasó antes (u(τ<t), incluyendo condiciones iniciales (u(t=0)). El sistema "recuerda" su estado previo, y su evolución depende de ese historial. Ecuaciones diferenciales: describen cómo varía el sistema en el tiempo. Ejemplo: un oscilador armónico, donde la posición depende no solo de la fuerza actual, sino también de la velocidad y posición inicial.

Ahora, podemos clasificarlos también en:

- **Modelos Lineales**: En caso de linealidad las ecuaciones que definen al sistema/modelo se reducen a una forma con parámetros A, B, C y D. Cumplen el principio de superposición (si u1 produce y1 y u2 produce y2, entonces au1+bu2 produce ay1+by2).
- **Modelo No Lineal**: No cumplen con el principio de superposición. El output no es proporcional al input.

Dentro de la dinámica no lineal, existe lo que se conoce como Teoría del Caos. Un sistema caótico es determinista (sus ecuaciones están bien definidas), pero su comportamiento es impredecible a largo plazo debido a tres propiedades:

1. **Sensibilidad a las condiciones iniciales**: Pequeñísimas diferencias en los valores iniciales producen trayectorias muy distintas con el tiempo. Se mide con el exponente de Lyapunov, que indica cuán rápido divergen esas trayectorias. Ejemplo: el clima, donde cambios minúsculos en el estado atmosférico generan pronósticos muy diferentes.
2. **Transitividad topológica**: Cualquier región del espacio de fases (el espacio que representa todos los estados posibles del sistema) eventualmente se superpone con cualquier otra región. Esto implica que el sistema "explora" todo el espacio posible y nunca se queda en una sola zona.
3. **Órbitas periódicas densas**: Para cualquier punto del espacio de fases, existe una órbita periódica arbitrariamente cercana. Esto significa que el caos está "entrelazado" con regularidad: el sistema nunca se repite exactamente, pero siempre hay patrones cerca.

Por otro lado, se puede clasificar los modelos según cómo evoluciona el estado del sistema en el tiempo:

- **Modelos de Estados Continuos**: las variables de estado pueden tomar cualquier valor dentro de un rango continuo y evolucionan sin saltos en el tiempo. La representación típica son ecuaciones diferenciales ordinarias (ODE) o parciales (PDE).
- **Modelos de Estados Discretos**: las variables de estado cambian en saltos o eventos específicos, y toman valores de un conjunto finito o contable. La representación típica son cadenas de Markov, procesos de eventos discretos, diagramas de estados. Las variables de estado son:
  - números enteros.
  - ON / OFF
  - HIGH / MEDIUM / LOW

Ahora, podemos plantear otra distinción según si el comportamiento del sistema es predecible o incorpora aleatoriedad.

- **Modelos Deterministas**: no hay incertidumbre, si usamos los mismos parámetros e inputs, siempre se obtiene el mismo resultado. Las variables evolucionan de forma totalmente predecible, siguiendo reglas fijas (ecuaciones matemáticas).
- **Modelos Estocásticos**: incorporan aleatoriedad o incertidumbre. Aun con los mismos inputs y parámetros, el resultado puede cambiar en cada simulación. Las variables siguen procesos probabilísticos.

El **Método de Monte Carlo** es uno de los enfoques más usados en simulación estocástica. Un modelo Monte Carlo es un algoritmo numérico que utiliza números aleatorios para estimar el comportamiento de sistemas complejos o inciertos. Se basa en repetir muchas veces un experimento aleatorio y observar los resultados.

- Usan variables aleatorias para modelar incertidumbre.
- Son útiles cuando no existe una solución analítica exacta.
- Requieren muchas simulaciones (corridas) para aproximar una solución.
- Los resultados son promedios estadísticos (esperanza, varianza, etc.).

Un ejemplo es la estimación de π. Se generan puntos aleatorios dentro de un cuadrado y se mira cuántos caen dentro de un círculo inscrito.

Otra forma de clasificar los modelos y simulaciones es según cómo evolucionan en el tiempo:

- **Simulación basada en tiempo discreto**: El tiempo avanza en pasos fijos: t=0,1,2,… o por intervalos definidos (por ejemplo, cada 0.1 segundos). En cada paso de tiempo, se evalúa el estado completo del sistema, aunque no haya ocurrido nada relevante. Un ejemplo es la integración numérica de una ecuación diferencial.
- **Simulación basada en eventos discretos**: El tiempo salta de un evento al siguiente. No hay una frecuencia fija; el sistema solo se actualiza cuando ocurre algo significativo (un evento). Se usa cuando:
  - Los eventos son poco frecuentes o irregulares.
  - Es necesario optimizar el rendimiento (no evaluar a cada paso fijo).

### Simulación vs. Animación

En una animación, los cuadros se generan artificialmente:

- A mano (dibujos).
- Cuadro a cuadro con muñecos (stop motion).
- Por computadora (CGI).
- O usando una simulación como motor (por ejemplo, en videojuegos o física de partículas).

En animación, no importa si el sistema es real o simulado, lo importante es que la ilusión de movimiento sea convincente.

La idea del cinematógrafo es la base de la animación: mostrar imágenes estáticas a velocidad suficiente (~10 cuadros/seg) para crear la ilusión de movimiento, aprovechando una propiedad del ojo humano (persistencia de la imagen en la retina).

Una simulación busca representar el comportamiento real o idealizado de un sistema a través de:

- Ecuaciones diferenciales (modelos físicos como osciladores, fluidos, etc.).
- Interacción de agentes (modelos sociales, de tráfico, etc.).
- Algoritmos o heurísticas (estrategias, inteligencia artificial, logística...).

Es un programa que genera una evolución temporal del sistema basada en modelos matemáticos o lógicos.

Entonces, una ANIMACIÓN puede estar generada a mano o puede estar generada a partir de una SIMULACIÓN. Una SIMULACIÓN puede generar una sucesión temporal de datos susceptible de ser animados.

### Estadística

Algunos de los conceptos fundamentales de estadística que debemos recordar son:

- Histograma
- Distribución de Probabilidad (con todos los yi menores a 1).
- Densidad de Probabilidad (PDF): es continua, a partir de datos finitos se la puede aproximar. Su integral es igual a uno. Algún yi particular podría ser mayor a uno.

Para simulaciones estocásticas, se repiten corridas (con distintas semilla) un cierto número de realizaciones y luego se reporta el observable como el promedio (µ) de los observables obtenidos. Su error asociado, usualmente es el desvío estándar (σ) (si se trata de una distribución de Gauss).

### Regresiones

Cuando hablamos de regresión en el contexto de modelado de sistemas físicos o simulaciones, nos referimos a ajustar datos experimentales con modelos que representan el comportamiento real del sistema, no con funciones arbitrarias. Se busca:

- Usar modelos con fundamento teórico (física, biología, economía, etc.).
- Ajustar datos a ecuaciones que describen el comportamiento del sistema.
- Validar el modelo no solo por el ajuste, sino por su significado físico o conceptual.

Tenemos distintos modelos para armar las regresiones:

- Modelo Exponencial: y(t) = a·e^(b·t)
- Modelo Senoidal: y(t) = a·sin(ω·t + φ)
- Modelo Lineal: y(t) = a·t + b

Dados los datos y un modelo teórico se puede definir el error del modelo en función de un coeficiente del mismo:

- Datos (promedios de simulaciones): (xi, yi)
- Ajuste modelo (lineal u otro cualquiera): f(xi, c)

Entonces, el Error del Ajuste es una función de c. El valor del coeficiente c que minimiza el error (E) es el que mejor ajuste del modelo a los datos produce.

Los datos se ajustan con funciones que provienen de algún modelo teórico. No con funciones arbitrarias (no con polinomios de grado N, "splines", etc.).

## Unidad 2 - Sistemas de Muchas Partículas

Nosotros vamos a trabajar con los sistemas físicos, y los problemas están generalmente compuestos por un número de partículas.

- **Problema de 1 cuerpo**: Integrable. Tiene solución analítica.
- **Problema de 2 cuerpos**: Integrable. Tiene solución analítica.
- **Problema de 3 cuerpos**: No Integrable. Sin solución analítica porque hay más grados de libertad. Se integra numéricamente.
- **Problema de N cuerpos**: Se integra numéricamente. Se usa la Dinámica Molecular.
- **Si N es muy grande**: Mecánica Estadística - Teoría Cinética

### Materia Activa

La materia activa está compuesta por unidades auto-propulsadas, capaces de convertir energía almacenada o del medioambiente en movimiento sistemático. Tienen energía en un reservorio interno y tienen su propio "motor". El ingreso de energía al sistema se da en forma local, al nivel de la unidad/partícula/agente y no en forma macroscópica a través de los límites del sistema. Las propiedades de sistemas fuera del equilibrio son:

- Estructuras emergentes con comportamiento colectivo cualitativamente diferente al de los componentes individuales.
- Transiciones orden-desorden.
- Formación de patrones en las escalas mesoscópicas.
- Etc.

Podemos ver los siguientes ejemplos de materia activa: en el caso de una bandada de aves, vemos que los movimientos de los distintos puntos forman una figura mucho más grande. Otro ejemplo es la simulación de peatones.

Se tiene una ecuación diferencial para cada peatón que lleva a un sistema de ecuaciones diferenciales acopladas. Se usan Métodos de Dinámica Molecular. A veces también se le agrega una fuerza de fluctuación que es una fuerza ruidosa que tiene valor medio cero pero cierto desvío estándar y hace que las partículas vibren.

En este caso, cuanto más grande es (el ruido), más se parecen unificar las partículas (nota: revisar sentido exacto en la fuente original, el fragmento del PDF es ambiguo en este punto).

### Comportamiento Emergente

En estos ejemplos, tenemos lo que se conoce como comportamiento emergente, que no es fácilmente predecible. Por ejemplo, si tenemos agentes "suicidas" cuya prioridad de supervivencia no es el individuo (insectos sociales), entonces hay un beneficio para el conjunto. En cambio, los agentes "egoístas" cuya prioridad de supervivencia es el individuo (todos los animales que no sean insectos sociales) generan un perjuicio para el conjunto.

Este tipo de comportamiento se da cuando tenemos muchos agentes simples con interacciones sencillas. Emergen espontáneamente patrones o comportamientos complejos, y la escala espacial característica de los mismos es mayor que la escala de un agente.

### Muchas Partículas Interactuantes

Todos los sistemas vistos hasta ahora consisten en partículas que interactúan entre sí de a pares y en función de las distancias. Para interacciones de largo alcance se deben calcular las distancias entre todas las partículas. Para interacciones de corto alcance sólo son relevantes las distancias a los vecinos cercanos.

Un método que permite detectar en forma eficiente qué partículas están cerca de otras es **Cell Index Method (CIM)**. El Método de Fuerza Bruta mide las distancias de todas las partículas con todas las partículas. La complejidad crece ~ N². Usando el CIM la complejidad crece lineal con N.

Lo que vamos a querer averiguar es la identidad de las partículas que están a distancia menor a rc. Por ahora, las partículas son puntuales. La idea del método es dividir el espacio en celdas, asignar las partículas a las celdas según su ubicación y calcular distancias solo entre partículas de celdas vecinas, y la propia.

Si el dominio tiene lados de longitud L y MxM celdas, entonces L/M es la longitud del lado de cada celda. Pero este M (que elegimos nosotros a diferencia de L) sería incorrecto para el radio rc, porque no está contemplando únicamente celdas vecinas. Entonces, disminuimos M para que L/M > rc (radio de interacción entre partículas).

Notemos que identificar a qué celdas pertenecen todas las moléculas es rápido y se podría hacer en todos los pasos temporales. Además, vemos que hay una simetría, pues dij = dji, lo que reduce a la mitad el tiempo de cálculo. Entonces, dada una celda, solamente vamos a tomar las distancias para las que están arriba y a la derecha.

Las condiciones de periódicas de contorno establecen que si una partícula se "va" del dominio de análisis, se reinserta con la misma velocidad por el lado contrario. Por ejemplo, la partícula en celda 10 es vecina de la que está en la celda 6 y su distancia es del orden de L/M. El problema puede o no tener estas condiciones.

### Reglas Generales de Simulaciones

Recordemos que la simulación es offline, se genera el output y recién allí se utilizan herramientas de análisis o animación. El formato de archivos para guardar simulaciones y su posterior visualización se define según el caso.

## Unidad 3 - Autómatas Celulares

Se trata de discretizar en una grilla (celdas), donde cada sitio de la grilla tiene un estado (puede ser ocupado o no por una partícula con velocidad, o el valor de alguna cantidad macroscópica, etc.). Existen reglas (Heurísticas) para definir la transición de estados, entre celdas entre un paso temporal y el siguiente. En algunos casos el AC pertenece al dominio Microscópico y promediando sobre muchas celdas se llega al dominio Macroscópico.

Los AC son arreglos regulares de celdas individuales de la misma clase. Cada celda tiene un número finito de estados discretos que se actualizan simultáneamente (sincrónicamente) en cada paso temporal. Las reglas de actualización son determinísticas y uniformes en tiempo y espacio. Las reglas para la evolución de una celda dependen solamente de un vecindario local a su alrededor.

### Autómatas Celulares 1-D

Sea una cadena uniforme de celdas (como un string). Cada estado ai(t) está definido por un número finito de enteros positivos (k) etiquetados desde 0 hasta (k-1). Si el valor ai-1 se actualizó y debo modificar ai, se toma el valor viejo.

La regla de evolución está dada por un mapeo, donde:

- r es el rango (nro.) de vecinos a considerar.
- αj constantes enteras.
- f es la Función no lineal: "regla del autómata".

Veamos el siguiente ejemplo de AC con k = 2 y r = 1: en general el nro. de posibles combinaciones es N = k^(2r+1). El número total de reglas posibles es k^N, en este caso es 2^8=256. Podríamos poner por ejemplo que en la línea 0, si hay dos 1 entonces en ai(t) tenemos un 1. Un AC de 1D cuya regla de actualización solo depende de los primeros vecinos (y de sí mismo) se llama: "AC Elemental".

Existen subclases de reglas. Hay 4 posibles patrones de Autómatas Celulares en 1-D:

1. Desaparece con el tiempo.
2. Evoluciona a un tamaño fijo finito.
3. Crece indefinidamente a una velocidad fija.
4. Crece y se contrae periódicamente.

### Autómatas Celulares 2-D

Primero, debemos definir la vecindad, para lo que tenemos dos definiciones: la vecindad de Von Neumann y la de Moore. Básicamente, la diferencia está en que Von Neumann no incluye las diagonales como sí lo hace Moore.

#### El Juego de la Vida

Tomemos el caso del "Juego de la Vida". En la década de 1970, Conway definió un autómata celular que simula la evolución de colonias de organismos vivos. Las reglas son:

- Se consideran 8 vecinos (Vecindad de Moore, r = 1).
- Cada celda tiene dos estados posibles "Viva" o "Muerta" (k = 2).
- Las Celdas Vivas permanecerán vivas en el siguiente paso temporal si tienen 2 o 3 vecinos vivos, de lo contrario morirá.
- Las Celdas Muertas se transformarán en Vivas solamente si tienen exactamente 3 vecinos vivos.

En la implementación:

- **Condición Inicial**:
  - Puede ser al azar (cada celda "Viva" o "Muerta").
  - Puede ser una configuración predeterminada.
- **Condición de Contorno**:
  - Puede ser periódica o no.

Pueden aparecer patrones estables. Un ejemplo de evolución (50x50), con estados a tiempos 141 a 148, se ilustra en el apunte original.

### Fluidos en 2D y el Modelo FHP

Ahora, podemos tomar el caso de los fluidos en 2D. La ecuación de Navier-Stokes relaciona la velocidad del fluido con la presión y la viscosidad. Sale a partir de:

- Conservación de la masa
- Conservación de la energía
- Conservación del momento
- Hipótesis de medio continuo

Estas ecuaciones para algunos casos particulares tienen solución analítica, pero en general se usan métodos numéricos.

Se pueden diferenciar números adimensionales, como por ejemplo el que relaciona la velocidad en un medio con la velocidad del sonido en el mismo medio. Otro es el número de Reynolds. Cuando la viscosidad es alta, R es muy bajo y existe un flujo laminar. En cambio cuando prevalecen las fuerzas inerciales, tenemos un flujo turbulento.

Nosotros vamos a ver el **Modelo FHP** (en nombre de Frisch, Hasslacher, and Pomeau), que definieron en 1986 un modelo "lattice gas" que es equivalente a resolver las ecuaciones de Navier-Stokes.

El autómata FHP consiste en un arreglo hexagonal de celdas (cada celda tiene 6 vecinas). Los vectores que unen estos nodos se llaman "lattice vectors" o velocidades de la retícula. Cada nodo tiene asociada una celda, que puede estar vacía u ocupada por varias partículas. Todas las partículas tienen la misma masa (=1) y son indistinguibles. La evolución está dada por:

- Una propagación (se mueve según velocidades).
- Colisión (adquieren nuevas velocidades, según las reglas de colisión).

Tenemos r el vector posición de un nodo y r + ci las posiciones de sus vecinos. Todas las posibles colisiones deben conservar el momento (además de la masa).

Vemos en un caso que la probabilidad es de 0,5. En el caso de dos partículas a 60 y 120 grados, para no perder el impulso se debe tomar como si se "traspasaran" y no colisionaran.

La implementación para la codificación del estado de cada celda utiliza un valor random para la toma de decisiones en la simulación. En el caso de colisionar con un sólido, el impulso no se conserva.

Veamos el caso de una colisión frontal binaria: AD, BE y CF, cada una puede pasar a cualquiera de las otras 2 con igual probabilidad, según una tabla de transición.

La colisión de 3 partículas representa otro caso: si viene por una roja, sale por una de las azules, según otra tabla de transición.

Por último, se consideran:

1. **Promedios Macroscópicos**: por lo menos 16x16 celdas y 10 pasos temporales.
2. **Fuerza Impulsora**: incluir momentum desde los bordes o cambiando con alguna probabilidad las velocidades de algunas celdas en una dirección deseada.
3. **Remapeo de la grilla hexagonal** para cálculo de vecinos (ver bibliografía).

### Autómatas Celulares Off-Lattice

No va a contar con una grilla, pero es un AC porque existen reglas de cómo se mueven. Cada partícula es puntual y se mueve en el continuo dentro de la celda de lado L.

Vemos que r es el radio de interacción entre partículas, v es la velocidad de módulo v y dirección dada por el ángulo θ, y el paso temporal es dt = 1.

Podemos plantear las condiciones iniciales:

- En t = 0, se generan N partículas distribuidas al azar en la celda.
- Todas tienen igual módulo v = 0.03.
- Y direcciones θ distribuidas al azar.

Entonces el sistema tiene 3 variables relevantes:

- Módulo de la velocidad (v)
- Densidad (ρ = N/L²)
- Amplitud del ruido (η)

Se define el parámetro de orden (va), el cual tiende a cero para total desorden y a 1 para partículas "polarizadas". Tomemos el caso de bandadas de agentes autopropulsados.

## Unidad 4 - Simulaciones Dirigidas por Eventos

Ahora, vamos a tomar un enfoque en el que se actualiza el sistema cada vez que hay un cambio de estado, por ejemplo tras la colisión de dos partículas. Antes actualizábamos el sistema con el paso temporal, y en el caso de una partícula que viajaba sola en el espacio, únicamente la desplazábamos teniendo en cuenta su posición y velocidad.

### Dinámica Molecular Regida Por Eventos

Simular el movimiento de N partículas que colisionan es importante para entender y predecir las propiedades de los sistemas físicos como la dinámica microscópica de gases, la difusión, mecánica estadística, transiciones de fase, medios granulares, etc. Las mismas técnicas se pueden aplicar para visualizar este tipo de sistemas con aplicaciones en el cine o videojuegos.

Nuestro sistema será el siguiente:

- N partículas confinadas en movimiento (no van a ser puntuales).
- Cada partícula tiene definida su posición, velocidad, radio y masa.
- Las partículas tienen interacciones elásticas entre ellas y con el contorno.
- Si no hay otras fuerzas que actúen sobre las partículas, éstas viajan en línea recta y a velocidad constante entre colisiones.
- Si fuesen partículas macroscópicas sometidas a un campo gravitatorio, éstas siguen sus trayectorias balísticas entre colisiones.

El enfoque de simulación "dirigida por eventos" es válido cuando se produce un choque instantáneo (de duración infinitesimal), cuando el tiempo de vuelo (entre choques) es mucho mayor al de duración del choque y cuando hay una densidad media-baja de partículas, pues por ejemplo en una bolsa de canicas habría constantemente fricciones y este sistema no funcionaría.

El algoritmo para esta simulación es el siguiente:

1. Se definen las posiciones y velocidades iniciales, los radios y tamaño de la caja.
2. Se calcula el tiempo hasta el primer choque (evento!) (tc).
3. Se evolucionan todas las partículas según sus ecuaciones de movimiento hasta tc.
4. Se guarda el estado del sistema (posiciones y velocidades) en t = tc.
5. Con el "operador de colisión" se determinan las nuevas velocidades después del choque, solo para las partículas que chocaron.
6. Ir a 2).

### Dinámica Molecular de Esferas Rígidas

La implementación para esferas rígidas contempla que la partícula i tiene definida su posición (xi, yi), su velocidad (vxi, vyi), su radio Ri y supondremos masa = 1 para todas las partículas. El tiempo tc es el mínimo de todos los tiempos de choque entre partículas vecinas y paredes. El vuelo libre de las partículas en x (y lo mismo en y) está dado por una ecuación de movimiento rectilíneo uniforme.

Vimos que primero se definen las posiciones y velocidades iniciales, los radios y tamaño de la caja. En este caso se generan partículas de a una, con posiciones y velocidades al azar dentro de la caja y tal que cada partícula nueva (i) no se superponga con ninguna de las existentes (j) ni con las paredes.

Luego, se hace el cálculo del tiempo de choque (tc) con paredes.

Si ahora queremos tomar el caso de los choques entre partículas, se vuelve un poco más complicado. Vamos a plantear una ecuación de encuentro para dos partículas circulares. Reemplazando y simplificando, se obtiene el tiempo de colisión.

El siguiente paso es evolucionar todas las partículas según sus ecuaciones de movimiento hasta tc. Y luego se guarda el estado del sistema (posiciones y velocidades) en t = tc (paso 4). Con el "operador de colisión" se determinan las nuevas velocidades después del choque, solo para las partículas que chocaron (paso 5). El operador colisión para el caso de paredes es sencillo.

Para el caso de colisión entre dos partículas, debemos contemplar que pueden tener distinta masa y, en nuestro caso, se genera un choque elástico sin fricción ni rotación. A partir de la conservación del Impulso (Jx, Jy) antes y después del choque, las velocidades se transforman según las ecuaciones correspondientes.

### Partículas en Presencia de Gravedad

Veamos ahora nuevamente el algoritmo pero en el caso de la presencia de una fuerza que cambia la trayectoria de las partículas, como por ejemplo la gravedad. El segundo paso plantea que se calcula el tiempo hasta el primer choque (evento!) (tc). En este caso, si reemplazamos las ecuaciones de posición en la ecuación de encuentro obtendremos un polinomio de grado 4 (~t⁴), el cual se puede resolver con métodos analíticos o numéricos. Si bien conceptualmente no es más difícil este problema, la implementación sí presenta una mayor dificultad.

Una vez hallado tc se evolucionan todas las partículas según sus ecuaciones de movimiento. Luego, se sigue con el paso 4 guardando el estado del sistema (posiciones y velocidades) en t = tc y con el paso 5 determinando las nuevas velocidades después del choque, solo para las partículas que chocaron. Esto se realiza igual que antes mediante el operador de colisión, tanto para el choque con paredes como el choque entre partículas. La presencia de la gravedad sólo cambia el problema del vuelo y tiempos entre choques pero no cambia el choque en sí mismo.

### Obstáculos Fijos

Tomemos ahora el caso de la presencia de un obstáculo fijo, como por ejemplo una columna. Queremos ver cómo se actualiza la velocidad tras el choque con este obstáculo. El choque va a ser radial, pero el obstáculo va a actuar como una pared ya que es inmóvil. En la dirección radial, va a cambiar la velocidad y en la tangencial se va a mantener igual, como pasaba con la pared. Para este caso, es conveniente hacer un cambio de sistema de coordenadas, definiendo un operador de colisión mediante una matriz de colisión.

Finalmente el Operador de Colisión (para partículas de igual masa) resulta según la expresión dada en el apunte (S.E.U.O.).

### Conceptos de Estadística

- **Histograma**: yi = Ni
- **Distribución de Probabilidad**: yi = Ni / N → Todos los yi son menores a uno.
- **Densidad de Probabilidad**: yi = Ni / (dxi · N) → La PDF es continua, a partir de datos finitos se la puede aproximar. Su integral es igual a uno. Algún yi particular podría ser mayor a uno.

### Selección de Eventos

Si graficamos los eventos en función del tiempo en este nuevo sistema, tenemos un diagrama de eventos.

Si esto tiene muchos eventos, para no saturar el disco se pueden saltear algunos eventos a la hora de realizar el guardado, tomando por ejemplo cada 10 eventos. Entonces, según el número de partículas, si hubiera demasiados eventos, guardar un estado cada 10 o cada 100 eventos.

Por otro lado, nos podría interesar conocer el estado del sistema en un tiempo regular, como por ejemplo qué sucede cada un segundo. Para el postproceso, podemos definir un dt (paso temporal) del tamaño de interés y se toma el primer evento que sucede justo después del tiempo deseado.

---

*Nota de extracción: el documento original incluye figuras, diagramas y expresiones matemáticas renderizadas como imágenes/fórmulas que no se transcriben literalmente aquí (el extractor de texto del proyecto no captura ecuaciones ni gráficos); se describe su contenido en el texto circundante tal como aparece en la fuente. El texto verbal se preservó de forma completa.*
