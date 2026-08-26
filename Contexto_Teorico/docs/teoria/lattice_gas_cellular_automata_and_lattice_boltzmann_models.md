# Lattice-Gas Cellular Automata y Lattice Boltzmann Models

*Fuente original: `lattice gas cellular automata and lattice boltzmann models.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes sustanciales y parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

## 0. Sobre el documento fuente

El PDF corresponde al libro *Lattice-Gas Cellular Automata and Lattice Boltzmann Models — An Introduction* de Dieter A. Wolf-Gladrow (Alfred Wegener Institute, Bremerhaven), publicado por Springer (2000, versión revisada 2005). Es un texto de nivel introductorio/de grado pensado originalmente como apunte de un curso dictado en la Universidad de Bremen. Cubre dos familias de métodos "bottom-up" para simular flujos (y otras ecuaciones diferenciales no lineales): los autómatas celulares de gas reticular (LGCA) y su descendiente más flexible, los modelos de Lattice Boltzmann (LBM). El libro está organizado en: (1) introducción e idea básica, (2) autómatas celulares en general, (3) LGCA (HPP, FHP, FCHC, PI, modelos térmicos), (4) mecánica estadística necesaria (ecuación de Boltzmann, BGK, Chapman-Enskog, máxima entropía) y (5) LBM (D2Q9, modelos 3D, estabilidad, aplicaciones a océano y difusión). Estas notas siguen ese mismo orden.

---

## 1. Introducción: la idea básica

### 1.1 La ecuación de Navier-Stokes y el número de Reynolds

El punto de partida del libro es la ecuación de Navier-Stokes para flujo incompresible:

∂u/∂t + (u·∇)u = −∇P + ν∇²u, con ∇·u = 0

donde u es la velocidad, P = p/ρ₀ la presión cinemática y ν la viscosidad cinemática. Distintos fluidos (aire, agua, aceite) comparten la misma forma de ecuación aunque sus interacciones microscópicas sean completamente distintas — esta observación es, según el autor, la motivación conceptual de fondo de los LGCA/LBM: si microdinámicas muy distintas de la real pueden dar la misma ecuación macroscópica, se puede diseñar un "micro-mundo" artificial extremadamente simple (partículas en una red) que reproduzca Navier-Stokes en el límite macroscópico.

Adimensionalizando la ecuación con la velocidad U y la escala L del obstáculo aparece un único parámetro adimensional, el número de Reynolds:

Re = UL/ν

Dos flujos con igual Re y misma geometría son "dinámicamente similares" — esta ley es el puente entre los flujos reales (metros, segundos) y las simulaciones en una red de paso y velocidad unitarios, donde la viscosidad es también adimensional. Re bajo → flujo laminar; Re ~ 100 → aparecen calles de vórtices de von Kármán; Re alto → turbulencia.

### 1.2 La idea de fondo de LGCA/LBM

Se imagina una red (por ejemplo cuadrada) con una celda por cada enlace a un vecino próximo; cada celda está vacía o contiene a lo sumo una partícula de masa unitaria (principio de exclusión, análogo al de Pauli). La velocidad de la partícula es el vector que conecta el nodo con su vecino ("velocidad de red"). La dinámica es puramente local: en cada paso de tiempo hay una **colisión** (redistribución de partículas en un nodo conservando masa y momento) seguida de una **propagación** (streaming) de cada partícula a lo largo de su enlace. Los valores macroscópicos (densidad, momento) se obtienen promediando ("coarse graining") sobre muchos nodos.

La pregunta central del libro es: ¿bajo qué condiciones estos promedios obedecen realmente Navier-Stokes? La respuesta, encontrada recién en 1986 por Frisch, Hasslacher y Pomeau, requiere tres ingredientes:

1. Conservación de masa y momento en las colisiones.
2. **Simetría suficiente de la red** — un tensor de cuarto rango construido con las velocidades de red debe ser isótropo. En 2D, simetría quíntuple (cuadrada) no alcanza; simetría hexagonal (red triangular) sí.
3. Que la microdinámica no posea "invariantes espurios" adicionales a masa y momento, que introducirían restricciones no físicas.

### 1.3 Enfoque "bottom-up" vs. "top-down"

Los métodos clásicos (diferencias finitas, volúmenes finitos, elementos finitos, espectrales) parten de la EDP y la discretizan ("top-down"): el problema típico es garantizar que las cantidades conservadas sigan conservándose tras la discretización, y lidiar con inestabilidades numéricas. LGCA/LBM invierten el camino ("bottom-up"): parten de un modelo microscópico discreto que por construcción conserva masa y momento, y la EDP macroscópica se *deriva* después mediante un análisis multi-escala (expansión de Chapman-Enskog). Los LGCA son incondicionalmente estables; los LBM tienen buenas propiedades de estabilidad pero no garantizadas en general. La contrapartida es que construir el modelo microscópico adecuado para una EDP dada requiere cierta "intuición", y que detectar todos los invariantes espurios posibles no siempre es posible.

También se distingue de la dinámica molecular (MD): en MD se busca reproducir con precisión la física microscópica real (ecuaciones de estado realistas), mientras que LGCA/LBM solo aspiran a reproducir la ecuación macroscópica de interés, con relaciones presión-densidad puramente isotérmicas y una microdinámica deliberadamente simplificada para ser eficiente computacionalmente.

---

## 2. Autómatas celulares (contexto, capítulo 2)

El libro dedica un capítulo (que puede saltearse en primera lectura, según el propio autor) a los autómatas celulares (CA) en general, como contexto histórico y conceptual de los LGCA. Un CA es un arreglo regular de celdas idénticas, cada una con un número finito de estados discretos, que se actualizan sincrónicamente en el tiempo mediante una regla local determinista (o, en algunos casos, probabilística) que depende solo de una vecindad finita. Se repasa la historia (Ulam, von Neumann y Zuse hacia 1950; el juego "Life" de Conway en 1970; los trabajos de clasificación de Wolfram en 1983-86) y el caso de los CA unidimensionales de 2 estados con vecindad de radio 1, que admiten 2⁸ = 256 reglas distintas (numeradas 0-255 según la interpretación binaria de la tabla de verdad). Wolfram propuso una clasificación cualitativa en cuatro clases de comportamiento (homogéneo, periódico, caótico, complejo) que no tiene análogo evidente en el caso de reglas totalísticas de rango mayor.

Un punto conceptual importante que el libro subraya: aunque un CA puede parecerse formalmente a una discretización de una EDP (por ejemplo, la ecuación de difusión discretizada por diferencias finitas tiene la misma forma que una regla de CA con coeficientes reales), las diferencias son profundas — los CA trabajan con un número finito de estados acotados, mientras que las discretizaciones numéricas usuales no están acotadas y pueden ser inestables; y sobre todo, la mayoría de las reglas de CA no respetan ninguna ley de conservación, mientras que las EDP de la física sí. La conexión real entre EDP y autómatas de red no es formal sino que está anclada en las leyes de conservación — este es exactamente el terreno de los LGCA.

También se menciona la irreversibilidad típica de los CA (muchas configuraciones iniciales distintas colapsan en la misma configuración futura — "configuraciones del Jardín del Edén" son estados que nunca pueden alcanzarse por evolución, solo inicializarse) y el crecimiento de la entropía de Shannon asociado, como contraste útil frente a los LGCA, que sí son (microscópicamente) reversibles.

---

## 3. Autómatas celulares de gas reticular (LGCA)

### 3.1 El modelo HPP (el primer LGCA, y por qué fracasa)

Propuesto por Hardy, de Pazzis y Pomeau en 1973. Vive sobre una red cuadrada: en cada nodo hay 4 celdas, una por dirección (arriba, abajo, izquierda, derecha), cada una vacía o con una partícula de masa unitaria. La evolución alterna colisión C y propagación S: E = S∘C. La única colisión no trivial es la "frontal": dos partículas entrantes por direcciones opuestas rotan ambas 90° (en el mismo sentido) tras chocar; todas las demás configuraciones quedan igual. Aplicar la colisión dos veces devuelve el estado original (C² = I). El modelo tiene simetría partícula-hueco y, por la estructura de la red cuadrada, se desacopla en dos sub-redes (como en un tablero de ajedrez) — un fenómeno análogo a la "inestabilidad de tablero de ajedrez" de ciertos esquemas de diferencias finitas.

El resultado central de esta sección es negativo: **HPP no reproduce Navier-Stokes** en el límite macroscópico. La razón (que se demuestra formalmente más adelante, en la sección de tensores de red) es que el tensor de cuarto rango construido con las velocidades de la red cuadrada no es isótropo — el término de advección no lineal queda "contaminado" por la orientación de la red. HPP además posee invariantes espurios (por ejemplo, la diferencia entre partículas que se mueven en direcciones paralelas y antiparalelas a un eje de la red se conserva, sin contraparte física real).

El libro dedica bastante espacio a la implementación práctica de HPP en C/FORTRAN mediante *multi-spin coding*: cada bit de una palabra de máquina codifica el estado de una celda de un nodo distinto, de modo que operaciones booleanas (AND, OR, XOR) sobre palabras enteras actualizan miles de nodos en paralelo con muy pocas instrucciones — una técnica de programación específica de LGCA poco documentada en la literatura general, que el autor resalta como aporte del libro. También se explica cómo inicializar los arreglos booleanos con probabilidades que reproduzcan valores dados de densidad y momento (a partir de un ansatz lineal Nᵢ = ρ/4 + (1/2)cᵢ·j) y cómo hacer el "coarse graining" (promediado espacial en bloques, típicamente de 32×32 o 64×64 nodos) para obtener campos macroscópicos de baja varianza.

### 3.2 El modelo FHP: el primer LGCA exitoso

Propuesto por Frisch, Hasslacher y Pomeau en 1986, sobre una red **triangular** con simetría hexagonal (invariante bajo rotaciones de 60°). Cada nodo tiene 6 enlaces con vecinos a igual distancia, y las velocidades de red son

cᵢ = (cos(πi/3), sin(πi/3)), i = 1,...,6, con |cᵢ| = 1

El estado de un nodo se describe con 6 bits (más un séptimo, opcional, para partículas en reposo en las variantes con partícula de reposo). Las colisiones consideradas en la versión mínima (FHP-I) son de dos tipos: (a) colisiones frontales de 2 partículas, que pueden rotar el par 60° a la izquierda o a la derecha — elegido al azar con igual probabilidad, lo cual introduce una regla **no determinista** (a diferencia de HPP) necesaria para restaurar la simetría de reflexión (paridad) a nivel macroscópico; y (b) colisiones simétricas de 3 partículas (equiespaciadas), que sirven específicamente para destruir un invariante espurio (la misma "diferencia entre direcciones opuestas" que aparecía en HPP). Variantes más ricas (FHP-II, FHP-III) agregan partículas en reposo, colisiones de 2 cuerpos "con espectador" y colisiones de 4 cuerpos; todas dan la misma forma de ecuación macroscópica (teorema de universalidad) y solo difieren en el valor del coeficiente de viscosidad, que en general disminuye cuantas más colisiones estén disponibles (más "mezcla").

Zanetti (1989) mostró que incluso las variantes de FHP conservan ciertos invariantes espurios adicionales, no locales, llamados invariantes de Zanetti ("staggered invariants"); afortunadamente la inicialización estándar no los excita por encima del nivel de ruido, así que en la práctica no distorsionan la dinámica hidrodinámica.

#### 3.2.1 Microdinámica booleana y ecuación de Liouville

El estado de la red se describe con variables booleanas nᵢ(t, r) (1 si la celda i del nodo r está ocupada en el instante t, 0 si no). La regla de evolución completa de FHP-I se puede escribir como una única expresión de álgebra booleana (AND, OR, XOR, NOT) que combina los cuatro casos de colisión posibles (incluyendo el bit aleatorio ξ que decide el sentido de rotación); el libro da también el código C correspondiente, construido a partir de máscaras de bits (`db1,db2,db3` para las tres orientaciones de colisión de 2 cuerpos, `triple` para la de 3 cuerpos). A nivel probabilístico, la evolución global del conjunto de configuraciones posibles obedece una ecuación de Liouville (determinista) o, cuando hay reglas probabilísticas como en FHP, su generalización, la ecuación de Chapman-Kolmogorov, que describe cómo evoluciona la distribución de probabilidad P sobre el espacio de todas las configuraciones microscópicas posibles.

#### 3.2.2 Distribución de equilibrio: teorema de Frisch, Hasslacher, Pomeau

Este es uno de los resultados teóricos centrales del libro. Se define el número medio de ocupación Nᵢ(t,r) = ⟨nᵢ(t,r)⟩, y a partir de él la densidad de masa y de momento:

ρ = Σᵢ Nᵢ,  j = ρu = Σᵢ cᵢNᵢ

El teorema (demostrado originalmente por Frisch, Hasslacher y Pomeau, 1987, y reproducido en el libro) establece que, bajo la condición de balance semi-detallado y en ausencia de invariantes espurios, la única solución de equilibrio compatible es una **distribución de tipo Fermi-Dirac**:

Nᵢ^eq = 1 / (1 + exp(h + q·cᵢ))

con h escalar y q vector, ambos determinados por los multiplicadores de Lagrange asociados a la conservación de masa y momento. La aparición de una distribución de Fermi-Dirac (y no de Maxwell-Boltzmann) es consecuencia directa del principio de exclusión (cada celda admite 0 o 1 partícula). La demostración usa la desigualdad x·log(x/y) + y − x ≤ 0, típica de argumentos tipo teorema H, para mostrar que log(Nᵢ/(1−Nᵢ)) debe ser un invariante de colisión y por tanto una combinación lineal de masa y momento.

Expandiendo esta distribución a bajo número de Mach se obtiene, para FHP-I,

Nᵢ^eq(ρ,u) ≈ ρ/6 + (ρ/3)(cᵢ·u) + ρG(ρ)Qᵢₐᵦuₐuᵦ + O(u³)

con G(ρ) = (1/3)(6−2ρ)/(6−ρ) y Qᵢₐᵦ = cᵢₐcᵢᵦ − (1/2)δₐᵦ. El término cuadrático en u es el que, en el análisis macroscópico, dará origen al término de advección no lineal de Navier-Stokes.

#### 3.2.3 Del micro al macro: análisis multi-escala (Chapman-Enskog)

Esta es la derivación más extensa y demandante del capítulo 3 (el propio autor la señala como uno de los pasajes más exigentes del libro). La idea es que en la evolución conviven procesos con escalas de tiempo muy distintas: relajación local al equilibrio (muy rápida, escala ε⁰), ondas sonoras y advección (escala ε⁻¹) y difusión (escala ε⁻², mucho más lenta), donde ε es un parámetro pequeño asociado a la relación entre la escala espacial de variación macroscópica y la unidad de red. Se introducen entonces tiempos multi-escala t₁ = εt*, t₂ = ε²t* y se expande Nᵢ alrededor de su valor de equilibrio local Nᵢ⁽⁰⁾(ρ(r,t), u(r,t)):

Nᵢ = Nᵢ⁽⁰⁾ + εNᵢ⁽¹⁾ + O(ε²)

Sustituyendo esta expansión en las leyes de conservación microscópicas y ordenando por potencias de ε se obtienen, a primer orden, la ecuación de continuidad y la ecuación de Euler:

∂ρ/∂t + ∇·(ρu) = 0
∂(ρu)/∂t + ∇·P⁽⁰⁾ = 0

donde el tensor de flujo de momento de orden cero, P⁽⁰⁾ₐᵦ = Σᵢ cᵢₐcᵢᵦNᵢ^eq, involucra el **tensor de advección de momento** de cuarto rango T^(MA)ₐᵦᵧᵨ = Σᵢ cᵢₐcᵢᵦQᵢᵧᵨ, que para FHP resulta isótropo:

T^(MA)ₐᵦᵧᵨ = (3/4)(δₐᵧδᵦᵨ + δₐᵨδᵦᵧ − δₐᵦδᵧᵨ)

Comparando P⁽⁰⁾ con el tensor de flujo de momento "real" (Pₓₓ = ρu² + p, etc.) aparece un factor de corrección g(ρ) = (3−ρ)/(6−ρ), siempre menor que 1: este es el llamado **problema de invariancia galileana** (el "g-disease"). Se origina en que la distribución de equilibrio de un LGCA es de tipo Fermi-Dirac (por el principio de exclusión) y no de tipo Maxwell-Boltzmann, y la red solo es invariante ante ciertas traslaciones discretas, no ante boosts galileanos arbitrarios. La solución práctica adoptada es un reescaleo del tiempo t → t/g(ρ), que "cura" el problema solo de forma sintomática (persisten efectos secundarios, como que la vorticidad se advecta a una velocidad g(ρ)u ≠ u). El libro anticipa que este defecto desaparecerá naturalmente al pasar a los modelos de Lattice Boltzmann, donde se pueden usar distribuciones de equilibrio distintas de Fermi-Dirac.

Incluyendo los términos de segundo orden en ε (calculados originalmente por Frisch et al. 1987 y Hénon 1987) se recupera finalmente, en el límite incompresible, la ecuación de Navier-Stokes completa:

∇·u = 0
∂u/∂t + (u·∇)u = −∇P + ν∇²u

con ν la viscosidad cinemática (reescalada), cuyo valor depende del modelo concreto (FHP-I/II/III) y de la densidad por celda. Se define también el "coeficiente de Reynolds" R* = Re/(L·Ma) = c_s g(d)/ν(d) como medida (independiente de la geometría) de cuán buena es la relación señal/viscosidad de cada variante, y se observa que FHP-III (con colisiones de 4 cuerpos, "saturado") logra los valores más altos.

FHP no posee ecuación de energía independiente: en FHP-I, conservación de masa y de energía cinética son esencialmente lo mismo (todas las partículas tienen |c|=1); en variantes con partículas de reposo, algunas colisiones no conservan energía cinética.

### 3.3 Tensores de red e isotropía: por qué HPP falla y FHP funciona

Esta sección formaliza matemáticamente la afirmación central del libro. Se definen los tensores de red de rango n como Lα₁...αₙ = Σᵢ cᵢα₁ ··· cᵢαₙ, construidos con los momentos de las velocidades de red; por la simetría de la red son invariantes ante el grupo de simetría del reticulado. Un tensor simétrico de rango 2 en D dimensiones tiene a lo sumo D(D+1)/2 componentes independientes, y uno de rango 4 bastantes más — la pregunta es si, dadas las restricciones de simetría de una red concreta, ese número de componentes independientes colapsa exactamente a la forma isótropa (proporcional a combinaciones de deltas de Kronecker) o no.

- **Red cuadrada (HPP, D2Q4):** el tensor de rango 2 es isótropo (∝ δₐᵦ), pero el de rango 4, Lₐᵦᵧᵨ = 2δₐᵦᵧᵨ (delta generalizada, no nula solo si los 4 índices coinciden), **no** es isótropo. Consecuencia directa: HPP no puede dar Navier-Stokes.
- **Red triangular (FHP, D2Q7):** tanto el tensor de rango 2 (Lₐᵦ = 3δₐᵦ) como el de rango 4 (Lₐᵦᵧᵨ = (3/4)(δₐᵦδᵧᵨ+δₐᵧδᵦᵨ+δₐᵨδᵦᵧ)) resultan isótropos gracias a la simetría hexagonal (6 direcciones equiespaciadas 60°). Por eso FHP sí reproduce Navier-Stokes.
- **FCHC (4D, D4Q24):** también isótropo hasta rango 4 (resultado de Wolfram, 1986), lo cual permite construir un modelo 3D válido mediante una hipercubo centrado en las caras de dimensión 4 con una dirección "extra" tratada de forma especial (ver 3.4 más abajo).

Para **modelos multi-velocidad** (varias longitudes de velocidad conviviendo en la misma red, como D2Q9), el tensor de rango 4 de la red pura suele no ser isótropo, pero la isotropía se puede recuperar introduciendo **pesos** wᵢ distintos para cada grupo de velocidades de igual módulo, definiendo tensores de red generalizados Gα₁...αₙ = Σᵢ wᵢcᵢα₁···cᵢαₙ. Este es exactamente el mecanismo que después permite construir la distribución de equilibrio del D2Q9 en el capítulo de LBM (con pesos 4/9, 1/9, 1/36).

### 3.4–3.6 Modelos en 3D: FCHC y el modelo de interacción por pares (PI)

Encontrar una red con simetría suficiente para 3D resultó mucho más difícil que en 2D. Si uno se restringe a modelos de una sola velocidad, la única solución conocida es el **FCHC** (Face-Centered HyperCube), una red centrada en las caras de un hipercubo de **4 dimensiones** (24 velocidades, D4Q24), con una cuarta dirección espacial "artificial" que en la práctica se implementa con solo dos capas y condición periódica (su componente de momento se comporta como un escalar pasivo). Existen varias variantes de reglas de colisión para FCHC (FCHC-1 a FCHC-8 en la nomenclatura del libro, con distinto número de partículas en reposo y distinto coeficiente de Reynolds máximo), todas bastante más complejas de codificar que las de FHP.

Como alternativa más manejable, Nasilowski (1989) propuso el modelo de **interacción por pares (PI)**, que funciona tanto en 2D (red cuadrada) como en 3D (red cúbica) con reglas mucho más simples de programar con operadores de bits. La diferencia clave es que el estado de cada celda no se codifica con un único bit sino con D+1 bits (un "bit de masa" y D "bits de momento", uno por componente cartesiana), de modo que el momento se define componente a componente y puede, contraintuitivamente, no apuntar en la misma dirección que la velocidad de la celda. Esta libertad extra de la definición del momento es precisamente lo que permite recuperar isotropía en una red que, por sí sola (cuadrada o cúbica), no tendría suficiente simetría. La interacción en cada nodo se descompone en una secuencia de interacciones entre pares de celdas (primero en x, luego en y, etc.), de ahí el nombre del modelo.

### 3.7 Modelos multi-velocidad y térmicos

Cuando se necesitan más grados de libertad (por ejemplo, para incluir una ecuación de energía independiente y obtener modelos "térmicos"), se recurre a redes con varias velocidades distintas conviviendo (rest particles, partículas de módulo 1, partículas de módulo √2, etc.), como D3Q19, D2Q9, D2Q13, D2Q21, y redes de muy alta velocidad para flujos transónicos/supersónicos (D2Q25, D2Q57, D2Q129). Estas familias reaparecen luego en el capítulo de LBM, donde son más manejables.

---

## 4. Herramientas de mecánica estadística (capítulo 4)

Este capítulo intermedio provee el aparato teórico (ecuación de Boltzmann continua, aproximación BGK, expansión de Chapman-Enskog, principio de máxima entropía) que después se reutiliza tanto para completar la derivación de Navier-Stokes de FHP a segundo orden como, sobre todo, para construir los modelos de Lattice Boltzmann del capítulo 5.

### 4.1 La ecuación de Boltzmann

Partiendo de la jerarquía BBGKY (Bogoliubov-Born-Green-Kirkwood-Yvon) y de las hipótesis usuales (solo colisiones binarias, caos molecular, sin efecto de fuerzas externas en la dinámica local de colisión), se llega a la ecuación de Boltzmann para la función de distribución de una partícula f(x,v,t):

∂f/∂t + v·∇ₓf + (K/m)·∇ᵥf = Q(f,f)

con el integral de colisión

Q(f,f) = ∫d³v₁ ∫dΩ σ(Ω)|v−v₁| [f(v')f(v₁') − f(v)f(v₁)]

**Invariantes de colisión y distribución de Maxwell.** El integral de colisión posee exactamente cinco invariantes elementales: ψ₀=1, (ψ₁,ψ₂,ψ₃)=v, ψ₄=v² (proporcionales a masa, momento y energía cinética). Cualquier combinación lineal de ellos anula el integral de colisión, y se demuestra que las únicas f positivas con Q(f,f)=0 son de la forma exp(a+b·v+cv²) con c<0 — lo que conduce, tras fijar las constantes con la densidad, velocidad media y temperatura, a la **distribución de Maxwell(-Boltzmann)**:

f^(M) = n (m/2πk_BT)^(3/2) exp(−m(v−u)²/2k_BT)

**Teorema H de Boltzmann.** Se define H(t) = ∫d³v d³x f ln f, y se demuestra (con un argumento de simetría bajo intercambio de partículas entrantes/salientes y la desigualdad (b−a)(ln a − ln b) ≤ 0) que dH/dt ≤ 0, con igualdad si y solo si f es la distribución de Maxwell — este es el análogo continuo de la irreversibilidad/aumento de entropía que ya se había mencionado para los CA en general.

### 4.2 La aproximación BGK

El integral de colisión completo es muy costoso de evaluar. Bhatnagar, Gross y Krook (1954, e independientemente Welander) propusieron sustituirlo por un operador de relajación lineal hacia el equilibrio local:

J(f) = ω (f^M(x,v) − f(x,v))

donde ω es la frecuencia de colisión (o su inverso, τ = 1/ω, el "tiempo de relajación"), y f^M es el **Maxwelliano local** — con la misma densidad, velocidad y temperatura que f en cada punto y en cada instante. Este operador conserva los mismos invariantes de colisión que Q(f,f) y respeta también la tendencia hacia el equilibrio (una versión débil del teorema H). **Esta es la aproximación de colisión que después se usa, casi sin excepción, en los modelos de Lattice Boltzmann modernos** (de ahí el nombre "LBGK").

### 4.3 De Boltzmann a Navier-Stokes: la expansión de Chapman-Enskog

Se trata de la misma técnica de análisis multi-escala ya usada para FHP en el capítulo 3, ahora aplicada de forma más sistemática a la ecuación de Boltzmann con aproximación BGK. El parámetro pequeño es el número de Knudsen Kn = λ/L (cociente entre el camino libre medio y la escala característica del sistema). Se expande

f = f⁽⁰⁾ + εf⁽¹⁾ + ε²f⁽²⁾ + ...

con f⁽⁰⁾ = f^M (la maxwelliana local), y se muestra que la desviación de primer orden vale

f⁽¹⁾ = −(1/ω)(∂ₜ⁽¹⁾f⁽⁰⁾ + vₐ∂ₓₐ⁽¹⁾f⁽⁰⁾)

es decir, proporcional a los gradientes espaciales y temporales del equilibrio local. Calculando con esta f⁽¹⁾ el tensor de esfuerzos de primer orden P̂⁽¹⁾ₐᵦ e integrando, se obtiene finalmente la parte disipativa de Navier-Stokes con una expresión explícita para la **viscosidad dinámica**:

μ = n k_BT / ω

(y ν = μ/ρ = k_BT/(ωm)). Este resultado — viscosidad inversamente proporcional a la frecuencia de colisión ω — es el que se traslada directamente, con las adaptaciones de la red discreta, a la fórmula de viscosidad de los modelos de Lattice Boltzmann BGK del capítulo 5.

### 4.4 El principio de máxima entropía

Se introduce, siguiendo a Shannon (1948), la entropía informacional S(P₁...Pₙ) = −Σᵢ Pᵢ log₂Pᵢ como medida de la "falta de información" de una distribución de probabilidad, y se demuestra el **teorema de máxima entropía**: la distribución que maximiza S sujeta a un conjunto de restricciones lineales (por ejemplo, valores dados de densidad y momento) tiene necesariamente la forma exponencial

f(x) = exp[−λ₀ − Σᵢ λᵢRᵢ(x)]

con los multiplicadores de Lagrange λᵢ determinados por las restricciones. Este resultado, puramente informacional/variacional, es la vía "elegante" que se usa en el capítulo 5 para derivar las distribuciones de equilibrio de los LBM (y que, aplicada con la restricción de ocupación 0/1 en el caso de LGCA, reproduce exactamente la distribución de Fermi-Dirac ya vista en la sección 3.2.2).

---

## 5. Modelos de Lattice Boltzmann (LBM)

### 5.1 De LGCA a LBM

Los LGCA sufren varias "enfermedades" — anisotropía del tensor de advección (curada pasando de HPP a FHP/PI), ruido estadístico intrínseco de las variables booleanas (que obliga a promediar sobre dominios grandes, con el consiguiente costo de memoria), violación de invariancia galileana (curada solo sintomáticamente reescalando el tiempo), invariantes espurios (los de Zanetti), y dependencia explícita de la presión con la velocidad en modelos de una sola velocidad (curada con modelos multi-velocidad). El libro resume estas patologías, sus causas y sus "terapias" en una tabla.

McNamara y Zanetti (1988) dieron el paso decisivo: en vez de simular variables booleanas ruidosas, proponen trabajar directamente con los **números medios de ocupación** Fᵢ(x,t) ∈ [0,1] (interpretables como funciones de distribución continuas), que evolucionan según

Fᵢ(x+cᵢ, t+1) = Fᵢ(x,t) + Ωᵢ({Fⱼ(x,t)})

con Ωᵢ la versión "aritmética" (continua) del mismo operador de colisión del LGCA subyacente. Esto elimina el ruido de golpe, aunque el operador de colisión sigue siendo no lineal y costoso. Higuera y Jiménez (1989) mostraron que puede linealizarse; y, en un paso posterior de simplificación y abstracción, Koelman (1991), Qian et al. (1992) y otros reemplazan directamente el operador de colisión por la aproximación **BGK** de la sección 4.2 — dando lugar a los modelos LBGK, hoy el estándar de facto.

Se muestra formalmente que la ecuación de Lattice Boltzmann (discreta) es una discretización particular de la ecuación de Boltzmann continua con BGK (resultado de Sterling y Chen, 1996): eligiendo el paso espacial igual a la velocidad de red por el paso temporal (comportamiento "lagrangiano"), la discretización se vuelve **exacta y explícita**, sin necesidad de resolver un sistema — este es un punto sutil pero importante: la ecuación cinética reticular

Fᵢ(x + cᵢΔt, t+Δt) − Fᵢ(x,t) = −(1/τ)[Fᵢ − Fᵢ^(eq)]

no es una aproximación adicional de la discretización de la ecuación de Boltzmann continua, sino que coincide con ella exactamente bajo esa elección de paso de red.

### 5.2 El modelo BGK en 2D: D2Q9

Este es el modelo tratado con mayor detalle en el libro, y sirve de "modelo de referencia" análogo al rol que jugó FHP en el capítulo de LGCA. Un LBM queda definido por tres ingredientes: (1) la red (D2Q9: 9 velocidades, incluyendo el reposo), (2) las distribuciones de equilibrio (de tipo Maxwell discreto) y (3) la ecuación cinética (BGK). A diferencia de un LGCA, que queda definido solo por la red y las reglas de colisión, en un LBM las colisiones no están "definidas" explícitamente: solo se manifiestan como relajación hacia el equilibrio local.

**La red D2Q9** (siguiendo la notación DkQb de Qian et al., k = dimensión, b = número de velocidades) tiene velocidades

c₀ = (0,0); c₁,c₂,c₃,c₄ = (±c,0),(0,±c); c₅,c₆,c₇,c₈ = (±c,±c)

**Los pesos Wᵢ** de la distribución de equilibrio en reposo se determinan exigiendo que los momentos de las velocidades de red hasta cuarto orden coincidan exactamente con los de la distribución de Maxwell continua (condición más estricta que la mera isotropía de los tensores de red vista en 3.3). Resolviendo el sistema de ecuaciones de momentos se obtiene

W₀ = 4/9 ρ₀,  W₁ = 1/9 ρ₀ (direcciones 1-4),  W₂ = 1/36 ρ₀ (direcciones 5-8),  con k_BT/m = c²/3

**La distribución de equilibrio general** F⁽⁰⁾ᵢ(ρ,j) se obtiene aplicando el principio de máxima entropía (definiendo una entropía relativa ponderada por 1/Wᵢ, siguiendo a Koelman) bajo las restricciones de conservación de masa y momento, y expandiendo hasta segundo orden en el momento/velocidad. El resultado, escrito ya en términos de la velocidad macroscópica u = j/ρ, es:

Fᵢ = (4/9)ρ[1 − (3/2)(u²/c²)]  para i=0

Fᵢ = (1/9)ρ[1 + 3(cᵢ·u)/c² + (9/2)(cᵢ·u)²/c⁴ − (3/2)(u²/c²)]  para i=1,2,3,4

Fᵢ = (1/36)ρ[1 + 3(cᵢ·u)/c² + (9/2)(cᵢ·u)²/c⁴ − (3/2)(u²/c²)]  para i=5,6,7,8

Esta fórmula (o variantes de ella con distinto número de velocidades) es la que se usa en la enorme mayoría de las implementaciones prácticas de LBM.

**La ecuación cinética** (BGK, con eventual fuerza de cuerpo Kα) es

Fᵢ(x+cᵢΔt, t+Δt) = (1−ω)Fᵢ(x,t) + ωFᵢ⁽⁰⁾(x,t) + [términos de fuerza]

con ω = Δt/τ la frecuencia de colisión (0<ω<2 por estabilidad, ver 5.6). El **algoritmo** de simulación queda entonces: (1) inicializar Fᵢ con las Fᵢ⁽⁰⁾ locales dadas ρ(x,0) y j(x,0); (2) en cada paso, "colisionar" (relajar hacia el equilibrio local con peso ω) y "propagar" (streaming a los vecinos según cᵢ); (3) recalcular ρ y j sumando las Fᵢ propagadas; (4) recalcular las nuevas Fᵢ⁽⁰⁾ y repetir. Es, en esencia, el mismo esquema colisión+propagación de los LGCA, pero sobre variables continuas y sin ruido.

Aplicando la expansión de Chapman-Enskog (idéntica en espíritu a la de la sección 3.2.3/4.3, pero ahora sobre la red D2Q9) se recupera Navier-Stokes con presión p = ρk_BT/m y **viscosidad cinemática**

ν = (c²/3)(1/ω − 1/2)Δt = (2−ω)/(6ω) · c²Δt

A diferencia de FHP, aquí el término de advección resulta **galileanamente invariante sin necesidad de reescalar el tiempo** — el "g-disease" de los LGCA no aparece, precisamente porque la distribución de equilibrio del LBM no está atada al principio de exclusión (no es Fermi-Dirac) y puede elegirse libremente de tipo Maxwell discreto.

### 5.3 Modelos 3D

Se presentan variantes con 15 y 19 velocidades (D3Q15, D3Q19), con distintas propuestas de distribución de equilibrio (Koelman; Chen et al.), como extensión directa del esquema D2Q9 a tres dimensiones.

### 5.4 El "método del ansatz": construir modelos de Lattice Boltzmann a medida

En contraste con el método de máxima entropía (elegante pero que oculta la libertad real disponible), el libro presenta un método alternativo, más flexible: proponer una forma funcional razonable para las Fᵢ⁽⁰⁾ (por ejemplo lineal o cuadrática en las cantidades conservadas) con coeficientes libres, y fijar esos coeficientes *durante o después* de la expansión multi-escala, exigiendo que se obtenga exactamente la EDP macroscópica deseada. Este método es el que se usa después para derivar modelos de Lattice Boltzmann para la ecuación de difusión (lineal y no lineal, en cualquier número de dimensiones) y para modelos térmicos con ecuación de energía.

### 5.5 – 5.6 Modelos térmicos y estabilidad

Se describen brevemente modelos con ecuación de energía (térmicos). En cuanto a estabilidad: a diferencia de los LGCA (incondicionalmente estables), los LBM **no** tienen garantizado un teorema H y por tanto pueden ser numéricamente inestables. Para flujo uniforme se muestra analíticamente que la perturbación respecto del equilibrio decae geométricamente con factor (1−ω), lo que exige 0<ω<2 (equivalentemente τ>1/2) para estabilidad. Para perturbaciones no uniformes se recurre al análisis de estabilidad lineal de von Neumann (el mismo método clásico usado para esquemas de diferencias finitas: se ensaya una perturbación de Fourier uⱼ,ₙ = Uⁿe^(ikjΔx) y se exige que el factor de amplificación λ cumpla |λ|≤1), aplicado aquí a la ecuación de advección, a la de difusión y finalmente a la ecuación cinética BGK completa sobre D2Q7/D2Q9/D3Q15. Se concluye que la estabilidad depende no solo de ω sino también del flujo de fondo (uniforme o de corte) y del tamaño de grilla (la estabilidad empeora al refinar la malla).

### 5.7 Condiciones de frontera para LBM

Se retoman los mismos cinco tipos de condiciones de frontera vistos para LGCA (periódicas, entrada, salida, no-deslizamiento, deslizamiento). Para no-deslizamiento (u=0 en la pared) el esquema estándar es el **bounce-back** ("rebote"): en vez de aplicar la colisión normal en un nodo de frontera, cada distribución entrante se invierte y sale por la dirección opuesta en el siguiente paso — Fᵢ(xᵦ+cᵢ,t+1) = Fᵢ₊₃(xᵦ,t) —, lo cual da u=0 en promedio entre el estado entrante y saliente. Existen dos variantes: bounce-back "completo" (la pared coincide con los nodos) y "de punto medio" (la pared física queda a mitad de camino entre el último nodo fluido y un nodo "seco" auxiliar) — esta última da resultados de mayor precisión, verificado comparando con la solución analítica exacta del flujo de Poiseuille plano (perfil parabólico u(y) = (K/2ν)(L²−y²) bajo fuerza constante K). Para deslizamiento se usa reflexión especular, Fᵢ(xᵦ+cᵢ,t+1) = Fᵢ₋₃(xᵦ,t). Se advierte que la localización efectiva de la frontera de un obstáculo no coincide exactamente con la posición de los nodos y depende de la dirección (capas de Knudsen anisótropas), lo cual importa especialmente para obstáculos pequeños.

### 5.8 Aplicación: circulación oceánica con LBM (modelo de Munk)

Como aplicación física concreta, el libro implementa un LBM D2Q9 extendido con fuerzas adicionales (esfuerzo del viento, fuerza de Coriolis, fricción) para simular la **circulación oceánica forzada por el viento** en una cuenca rectangular barotrópica — el problema clásico resuelto analíticamente por Munk (1950) para explicar la intensificación de corrientes de borde oeste (Corriente del Golfo, Agulhas, Kuroshio). La ecuación de vorticidad del problema de Munk,

∂/∂t(∇²ψ) + J(ψ,∇²ψ) + β∂ψ/∂x − A∇⁴ψ + (∂Tᵧ/∂x − ∂Tₓ/∂y) = 0

(con ψ función de corriente, β el parámetro de variación del efecto Coriolis con la latitud, y A la viscosidad de remolino) tiene solución analítica exacta en su versión linealizada y estacionaria, y define una escala característica (escala de Munk) W_M = (A/β)^(1/3) para el ancho de la corriente de borde oeste. Los resultados del LBM (con los términos no lineales de las distribuciones suprimidos para comparar con el caso lineal) se contrastan tanto con esta solución analítica como con un modelo de diferencias finitas del problema no lineal completo. El interés práctico señalado es que los LBM son muy simples de programar (sin necesidad de resolver ninguna ecuación elíptica, a diferencia de los modelos oceánicos clásicos tipo MOM) y muy adecuados para computación masivamente paralela, gracias a la localidad estricta de las "colisiones".

### 5.9 Aplicación: un LBM para la ecuación de difusión

Se construye, con el método del ansatz de la sección 5.4, probablemente el LBM más simple posible: sobre una red con solo 2D velocidades (una por cada sentido de cada eje cartesiano), con una distribución de equilibrio lineal y **la misma para todas las direcciones**, T⁽⁰⁾ = T/(2D), se deriva por expansión multi-escala la ecuación de difusión ∂T/∂t = κ∇²T con coeficiente de difusión

κ = (1/ω − 1/2)(1/D)

Un resultado destacado: para ω=1 el esquema se reduce exactamente a un esquema de **diferencias finitas explícitas evaluado justo en su límite de estabilidad** (el nuevo valor es la media aritmética de los vecinos). Para 0<ω<1 (sub-relajación) se obtiene un coeficiente de difusión efectivo mayor que ese límite clásico, manteniendo Δt=Δx=1 y sin perder estabilidad — es decir, el LBM permite superar la restricción de estabilidad Δt ≤ (Δx)²/(2Dκ) propia del esquema explícito clásico, a costa de un mayor error numérico (verificado comparando con la solución analítica gaussiana de la ecuación de difusión). El mismo método se extiende, en el libro, a difusión no lineal (coeficiente dependiente de la concentración) y a ecuaciones de reacción-difusión.

### 5.10 Panorama de aplicaciones adicionales (sección "What else?")

El libro cierra el capítulo de LBM con un listado extenso, a modo de mapa de la literatura, de áreas donde se han aplicado LGCA/LBM más allá de lo desarrollado en detalle: coordenadas curvilíneas y mallas no estructuradas/refinamiento adaptativo; flujo alrededor de obstáculos; **flujo en medios porosos** (una de las aplicaciones más consolidadas); flujo granular; **flujos multifásicos y multicomponente** (mezclas inmiscibles, tensión superficial); magnetohidrodinámica; flujos compresibles y ecuación de Burgers; flujo alrededor de obstáculos fractales; **turbulencia y simulación de grandes escalas (LES)**; flujo en geometría dinámica, incluyendo **flujo sanguíneo**; flujo de glaciares; convección de Rayleigh-Bénard; inestabilidad de Rayleigh-Taylor; ecuación de Korteweg-de Vries; formación de gotas; crecimiento de cristales; propagación de ondas; incluso ecuaciones de Maxwell y mecánica cuántica. Esto ilustra la versatilidad del método más allá de la hidrodinámica clásica que motivó su desarrollo.

---

## 6. Cierre: perspectiva del autor

En el resumen final, el autor reflexiona sobre por qué estos métodos resultan atractivos, sobre todo para físicos: (1) están construidos desde el principio alrededor de leyes de conservación, terreno familiar para la física; (2) requieren más teoría física genuina (mecánica estadística: Chapman-Enskog, máxima entropía) que otros métodos numéricos más "mecánicos" como diferencias finitas; y (3) el rol de la simetría es central y aparece una y otra vez: pasar de simetría cuádruple (HPP) a hexagonal (FHP) para obtener el término de advección correcto, necesitar una cuarta dimensión (FCHC) para lograr simetría suficiente en 3D con una sola velocidad, usar aleatoriedad para restaurar simetría de paridad (FHP), y tener que "escalar" o eliminar sistemáticamente las rupturas de simetría residuales (invariancia galileana, invariantes espurios). El autor no predice que estos métodos vayan a desplazar a los esquemas numéricos tradicionales (diferencias finitas, volúmenes finitos, elementos finitos, espectrales), que siguen desarrollándose y conviviendo con LGCA/LBM según las ventajas relativas de cada problema concreto.

---

## 7. Glosario mínimo de notación (para referencia rápida en los TPs)

- **LGCA**: Lattice-Gas Cellular Automata (autómata celular de gas reticular).
- **LBM / LBE**: Lattice Boltzmann Model / Equation.
- **DkQb**: notación de red (Qian et al.) — k = dimensión espacial, b = número de velocidades de red (incluyendo, si existe, la de reposo c₀=0).
- **cᵢ**: velocidades de red (vectores discretos de propagación).
- **Nᵢ / Fᵢ**: número medio de ocupación (LGCA) / función de distribución discreta (LBM) asociada a la dirección i.
- **ρ, j=ρu**: densidad de masa y densidad de momento (velocidad macroscópica u).
- **ω = 1/τ**: frecuencia de colisión / inverso del tiempo de relajación BGK.
- **Fᵢ⁽⁰⁾ / Nᵢ^eq**: distribución de equilibrio local (Maxwell discreta en LBM; Fermi-Dirac en LGCA).
- **Kn = λ/L**: número de Knudsen, parámetro pequeño de la expansión de Chapman-Enskog.
- **Re = UL/ν**: número de Reynolds.
