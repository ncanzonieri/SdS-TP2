# Hidrodinámica de la materia blanda activa (Marchetti et al., Rev. Mod. Phys. 2013)

*Fuente original: `marchetti_hydrodynamics_soft_active_matter.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes sustanciales y parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

Referencia completa: M. C. Marchetti, J. F. Joanny, S. Ramaswamy, T. B. Liverpool, J. Prost, M. Rao, R. Aditi Simha, "Hydrodynamics of soft active matter", *Reviews of Modern Physics* **85**, 1143 (2013).

---

## 1. Motivación y qué se entiende por "materia activa"

El artículo es una revisión (review) de gran alcance que busca dar un marco teórico unificado para sistemas de "materia viva" y sus imitaciones no vivas: filamentos citoesqueléticos y motores moleculares (in vitro o dentro de la célula), microorganismos móviles (bacterias), cardúmenes y bandadas de animales, y sistemas artificiales (materia granular vibrada, coloides autopropulsados por reacciones catalíticas, robots).

La característica que define a la **materia activa** es que está compuesta por unidades autopropulsadas ("partículas activas"), cada una de las cuales convierte energía almacenada o del ambiente en movimiento sistemático (locomoción). A diferencia de un sistema fuera de equilibrio "clásico" (por ejemplo, un fluido con un gradiente de temperatura impuesto en el borde), en materia activa la inyección de energía es **local**: ocurre en cada partícula individualmente, no en el contorno del sistema. Esto es lo que distingue verdaderamente a estos sistemas de otros problemas de no equilibrio ya conocidos en física de la materia condensada.

Las partículas activas suelen ser alargadas (anisótropas) y su dirección de autopropulsión está fijada por su propia anisotropía (no por un campo externo), por lo que el **orden orientacional** es un tema recurrente en toda la fenomenología: enjambres de bacterias, bandadas de aves, cardúmenes de peces, capas de células, filamentos del citoesqueleto activados por motores, todos exhiben distintas formas de orden orientacional colectivo.

Los autores remarcan que una teoría exhaustiva de la "materia viva" en general es inabordable por su complejidad (un organismo tiene, a lo sumo, unos 300 tipos celulares, pero cada célula responde a una enorme cantidad de señales). La estrategia, entonces, es apostar a que **principios generales** —leyes de conservación y simetrías— restringen el comportamiento dinámico posible, permitiendo una descripción hidrodinámica de grano grueso (coarse-grained) independiente de buena parte del detalle microscópico. Esta filosofía es la misma que subyace a la hidrodinámica de cristales líquidos de Martin-Parodi-Pershan, extendida aquí con nuevos términos "no de equilibrio" que provienen de la actividad.

### Clasificación general: polar vs. nemático, "seco" vs. "húmedo"

El review propone organizar la materia activa en clases de universalidad según dos ejes:

1. **Simetría del orden roto.** Los objetos autopropulsados alargados suelen ser polares (tienen cabeza y cola distinguibles, como bacterias o peces) y pueden ordenar de forma:
   - **Polar (ferromagnética)**: todos los objetos apuntan en promedio en la misma dirección. Se describe con un parámetro de orden vectorial, la polarización **p**.
   - **Nemática**: hay un eje privilegiado pero sin distinción de sentido (cabeza-cola). Ocurre tanto cuando partículas polares se alinean "en paralelo" pero con orientaciones cabeza-cola aleatorias, como cuando las partículas mismas son apolares (p. ej. melanocitos). Se describe con un tensor de alineamiento **Q** (simétrico y de traza nula).

2. **Conservación o no del momento (seco vs. húmedo).** Si las partículas activas se mueven sobre un sustrato friccional (o entre paredes muy cercanas, o a través de un medio poroso), el momento del conjunto de partículas activas **no se conserva** (se disipa por fricción con el sustrato): estos son sistemas **"secos"**. Si en cambio las partículas están suspendidas en un fluido y las interacciones hidrodinámicas mediadas por el solvente son relevantes, hay que incluir la dinámica del fluido y el momento total (partículas + fluido) se conserva: estos son sistemas **"húmedos"**. Es importante notar que esta distinción se refiere al *modelo* usado (y a la escala de longitud de interés), no a una propiedad intrínseca del sistema: un mismo sistema físico puede comportarse como "seco" a ciertas escalas y "húmedo" a otras.

El artículo arma una tabla con ejemplos: manadas migrando en tierra, capas de células migrando, melanocitos y varillas granulares vibradas (secos, nemáticos o polares); citoesqueleto y extractos celulares en volumen, suspensiones de coloides catalíticos, bacterias nadando en volumen (húmedos).

---

## 2. Las dos grandes estrategias para construir la hidrodinámica activa

El review distingue (y luego busca reconciliar) tres caminos para llegar a las ecuaciones hidrodinámicas de un sistema activo:

- **(a) Derivación microscópica**: partir de un modelo de partículas concreto (p. ej. el modelo de Vicsek, o filamentos con motores) y usar herramientas de mecánica estadística (ecuación de Smoluchowski, cierre de momentos) para obtener por *coarse-graining* las ecuaciones de campo de largo alcance. Es más laborioso y requiere aproximaciones (baja densidad, interacción débil), pero permite relacionar los parámetros macroscópicos con cantidades microscópicas.
- **(b) Enfoque fenomenológico "por simetría"**: escribir directamente las ecuaciones hidrodinámicas para los campos macroscópicos, incluyendo todos los términos permitidos por la simetría del problema (como hicieron pioneramente Toner y Tu para bandadas "secas", y luego Simha y Ramaswamy para suspensiones activas). Aparecen naturalmente términos "nuevos" que están prohibidos en un sistema en equilibrio térmico.
- **(c) Termodinámica generalizada cerca del equilibrio (tipo Onsager)**: tratar el estado estacionario activo como una perturbación pequeña y sostenida sobre un estado de equilibrio térmico bien definido (por ejemplo, para el citoesqueleto, la fuerza motriz es la diferencia de energía libre química Δμ de la hidrólisis de ATP). Se identifican flujos y fuerzas termodinámicas y se escribe la relación lineal más general entre ellos respetando las simetrías del problema (procedimiento de Onsager). Los términos "nuevos" resultan ser, en este marco, coeficientes de Onsager no diagonales multiplicados por el Δμ impuesto.

Un resultado central del review es mostrar que estos tres caminos, aplicados a sistemas con la misma simetría, llevan a ecuaciones con la **misma estructura**, difiriendo solo en los valores concretos de los parámetros de transporte.

Para construir cualquier teoría hidrodinámica hay que identificar las variables lentas: las densidades locales de cantidades conservadas, los campos de "simetría rota" (que no tienen fuerza restitutiva a número de onda cero) y, cerca de una transición de fase continua, el parámetro de orden. En sistemas húmedos, la densidad de momento es una variable lenta conservada; en sistemas secos, el momento es una variable rápida y solo la densidad de partículas es conservada.

---

## 3. Materia activa "seca": el modelo de Toner-Tu y su conexión con Vicsek (clave para TP2 - flocking)

Esta es la sección más directamente relevante para el estudio de modelos tipo Vicsek / flocking.

### 3.1 El modelo de Vicsek y su versión continua

El modelo de Vicsek (1995) describe partículas puntuales autopropulsadas con **rapidez fija**, cuya dirección de movimiento cambia según una regla local ruidosa que tiende a alinearlas con sus vecinas en cada paso temporal. Exhibe una transición de fase de no equilibrio, de un estado desordenado (a baja densidad o ruido alto) a un estado ordenado de movimiento colectivo coherente (a alta densidad o ruido bajo).

Toner y Tu (1995, 1998) propusieron, por argumentos de simetría, una **teoría de campo continua** ("hidrodinámica de bandadas") para describir el comportamiento de grano grueso de este tipo de modelos. Más tarde, Bertin, Droz y Grégoire (2006, 2009) e Ihle (2011) lograron *derivar* estas mismas ecuaciones a partir del modelo de Vicsek microscópico (vía una ecuación de Boltzmann de grano grueso), lo cual dio valores explícitos para casi todos los parámetros fenomenológicos del modelo de Toner-Tu (excepto la magnitud del ruido).

### 3.2 Variables y ecuaciones fundamentales

Como las partículas se mueven sobre un sustrato friccional, el único campo conservado es la densidad numérica ρ(**r**,t) de partículas activas. Para describir el posible orden polar se introduce además el campo de polarización **p**(**r**,t). Ambos se definen microscópicamente a partir de las posiciones **r**ₙ(t) y las orientaciones instantáneas de velocidad **ν̂**ₙ(t) de cada partícula (ecuaciones (1a)-(1b) del original).

Las ecuaciones dinámicas acopladas (forma simplificada, ignorando ruido y difusión de densidad por simplicidad) son:

$$\partial_t \rho + v_0 \nabla\cdot(\rho\,\mathbf{p}) = 0$$

$$\partial_t \mathbf{p} + \lambda_1(\mathbf{p}\cdot\nabla)\mathbf{p} = -\frac{1}{\gamma}\frac{\delta F_p}{\delta \mathbf{p}} + \mathbf{f}$$

donde **v₀** es la rapidez de autopropulsión de cada partícula individual, γ y λ₁ son coeficientes cinéticos, y **f** es un ruido blanco gaussiano de media nula. El punto clave es que **p** cumple un **doble rol**: es simultáneamente el parámetro de orden orientacional del sistema *y* (multiplicado por v₀) el campo de velocidad de las partículas. Esta dualidad es la que genera el comportamiento de largo alcance característico del sistema fuera de equilibrio.

A diferencia de la ecuación de Navier-Stokes, aquí **no hay invariancia galileana** (las partículas se mueven relativo a un sustrato fijo), de modo que el coeficiente λ₁ del término advectivo (**p**·∇)**p** es en general **distinto** de v₀ — no está fijado por ningún principio de conservación, sino que es un parámetro fenomenológico no universal determinado por la física microscópica.

La energía libre efectiva que genera los términos "tipo equilibrio" de la ecuación de **p** tiene la forma tipo Landau-de Gennes:

$$F_p = \int_{\mathbf r}\left[\frac{\alpha(\rho)}{2}|\mathbf p|^2 + \frac{\beta}{4}|\mathbf p|^4 + \frac{K}{2}(\partial\mathbf p)^2 + \dots\right]$$

con α(ρ) el coeficiente que controla la transición orden-desorden de campo medio: se toma típicamente α(ρ) = α₀(1 − ρ/ρc), que cambia de signo en una densidad crítica ρc. β > 0 por estabilidad, y K es la constante de Frank (rigidez elástica frente a deformaciones espaciales del parámetro de orden).

### 3.3 La transición orden-desorden

- Para α > 0 (ρ₀ < ρc): estado homogéneo **desordenado/isótropo**, con **p** = 0 y velocidad media nula.
- Para α < 0 (ρ₀ > ρc): estado **ordenado**, con |**p₀**| = √(−α/β) ≠ 0. Este es también un estado en movimiento (velocidad media **v** = v₀**p₀**), donde se rompe espontáneamente la simetría rotacional continua.

Un resultado notable —y contraintuitivo desde la física de equilibrio— es que este orden orientacional continuo **sobrevive en 2D** incluso considerando fluctuaciones, "evadiendo" el teorema de Mermin-Wagner (que en equilibrio prohíbe la ruptura espontánea de una simetría continua en 2D). La razón es que las no linealidades advectivas de las ecuaciones generan efectivamente interacciones de largo alcance en el sistema (esto no aplica porque el sistema no está en equilibrio térmico, así que el teorema simplemente no rige).

### 3.4 Fase isótropa: ondas de sonido activas

Linealizando alrededor del estado isótropo se obtienen relaciones de dispersión acopladas entre fluctuaciones de densidad y de polarización longitudinal. Para valores razonables de los parámetros (v₀v₁ > 0, con v₁ un coeficiente tipo "módulo de compresión efectivo") el estado isótropo es linealmente estable, aunque presenta la propiedad inusual de que, cerca de la transición, las fluctuaciones de densidad pueden propagarse como **ondas** en vez de difundir puramente — recordando ondas de sonido — en un rango finito de números de onda. Esto es una consecuencia genuina de la actividad, sin análogo simple en un fluido pasivo.

### 3.5 Fase ordenada: inestabilidad cerca de la transición y bandas

Analizando la estabilidad lineal del estado ordenado (con **p₀** apuntando en una dirección fija), se encuentra que, **cerca de la transición de campo medio**, el estado uniformemente polarizado es en realidad **linealmente inestable** frente a fluctuaciones de número de onda pequeño (existe un rango 0 < q < qc de modos inestables). Simulaciones numéricas del modelo continuo (con y sin ruido) muestran que en esa región el estado homogéneo se reemplaza por **estructuras espaciotemporales complejas**: ondas solitarias que toman la forma de **bandas ordenadas** (regiones de alta densidad y alto orden polar) que se propagan en un fondo desordenado de baja densidad. Estas bandas ya habían sido observadas en simulaciones del modelo de Vicsek microscópico (Grégoire y Chaté, 2004; Chaté et al., 2008) y son uno de los fenómenos más característicos y reproducibles del flocking cerca de la transición.

**Consenso numérico actual sobre el tipo de transición** (resaltado explícitamente en el review): a pesar de estudios tempranos que sugerían una transición continua tipo campo medio, la evidencia numérica más sólida (para sistemas donde el número de partículas se conserva) indica que la transición orden-desorden en modelos secos tipo Vicsek es en realidad **discontinua** (de primer orden), con un régimen extendido de coexistencia dominado por estas bandas viajeras. Este fenómeno se vincula a lo que los autores llaman "autorregulación dinámica": a diferencia de una transición de fase de equilibrio típica, el parámetro de control (la densidad local de partículas activas) no se fija externamente, sino que es advectado/difundido por las mismas corrientes activas que dependen del parámetro de orden.

### 3.6 Fluctuaciones gigantes de densidad ("giant density fluctuations")

Uno de los resultados más citados del formalismo. En el estado ordenado, se calcula el factor de estructura estático S(**q**) a partir de las ecuaciones linealizadas, encontrando una divergencia tipo 1/q² para q → 0 (a diferencia de un fluido en equilibrio, donde S(q→0) es finito y proporcional a la compresibilidad isotérmica). Esto implica que las fluctuaciones del número de partículas ΔN en una subregión de tamaño V, en vez de escalar como ΔN ~ √⟨N⟩ (ley estándar de equilibrio, teorema central del límite), escalan como:

$$\Delta N \sim \langle N\rangle^{a}, \qquad a = \frac{1}{2} + \frac{1}{d}$$

con d la dimensión espacial (en d=2, a=1, es decir ΔN ~ ⟨N⟩, fluctuaciones "gigantes" comparadas con el caso térmico). Esto se ha confirmado experimentalmente tanto en materia granular vibrada (polar y apolar) como en suspensiones bacterianas, aunque los exponentes medidos difieren algo del valor lineal simple predicho (por ejemplo, a ≈ 0.75 en bacterias, Zhang et al. 2010), reflejando la importancia de efectos no lineales no capturados por la teoría linealizada. Los autores aclaran que estas fluctuaciones gigantes **no** corresponden a una compresibilidad efectiva divergente (la respuesta a una perturbación externa sigue siendo finita); son más bien "ruido en exceso" que proviene de que el modo de Goldstone (blando) del orden orientacional invade la dinámica de la densidad — algo que solo ocurre porque el sistema es activo (la curvatura orientacional genera una corriente de partículas real).

### 3.7 Orden nemático en sistemas secos (materia activa apolar)

Cuando las partículas activas son apolares (o cuando el mecanismo de interacción alinea sin distinguir cabeza-cola), el estado ordenado tiene simetría **nemática** en vez de polar, descrito por el tensor **Q**. Aunque a primera vista un "flock que no va a ningún lado" (sin velocidad media) parece menos interesante, el review muestra que estos sistemas también exhiben fluctuaciones gigantes de densidad, e incluso pueden mostrar **auto-propulsión local emergente**: una configuración curva (splay/bend) del director nemático genera una polaridad local transitoria, y en un sistema activo esa polaridad transitoria se traduce en una corriente neta de partículas:

$$J_{\text{activo}} = \lambda_Q\, \nabla\cdot Q$$

Este mecanismo (curvatura → polaridad local → corriente) es una de las "firmas" distintivas de la actividad y ha sido confirmado experimentalmente (defectos de carga +1/2 que se mueven en capas vibradas de varillas, Narayan-Ramaswamy-Menon 2007) y en simulaciones.

Además el review discute un caso "de simetría mixta": varillas rígidas autopropulsadas (self-propelled hard rods, Baskaran y Marchetti 2008), donde cada partícula individual es polar (tiene una dirección de autopropulsión definida) pero las colisiones esféricas rígidas entre pares generan una alineación **apolar** (nemática). El resultado sorprendente de la teoría cinética es que estas varillas, pese a ser polarmente autopropulsadas, **no ordenan macroscópicamente en un estado polar en volumen**: la simetría de largo alcance sigue siendo nemática, aunque la autopropulsión sí favorece (adelanta a menor densidad) la transición isótropo-nemático respecto del caso puramente térmico (tipo Onsager). Las simulaciones muestran formación de clusters polares viajeros y bandas nemáticas cerca de la transición, cualitativamente distintas del comportamiento tipo Vicsek puro.

---

## 4. Geles activos: materia activa "húmeda" (suspensiones)

Cuando el momento se conserva (sistema húmedo), el enfoque adoptado es la termodinámica generalizada tipo Onsager, siguiendo de cerca la hidrodinámica de cristales líquidos de Martin-Parodi-Pershan, extendida con actividad. El sistema modelo es el "gel activo": un fluido o suspensión de objetos orientables con **esfuerzos activos** (active stresses), con disipación de momento dominada por la viscosidad del medio (no por fricción de sustrato).

### 4.1 Producción de entropía y variables lentas

Se identifican como variables lentas: la densidad ρ, la polarización **p**, y la densidad de momento **g** = m**v**. La tasa de producción de entropía en un gel activo a temperatura constante se escribe combinando la variación de energía libre con el término de inyección de energía química (por ejemplo, la hidrólisis de ATP con energía Δμ por molécula, a una tasa de reacción r):

$$T\dot S = \int d\mathbf r\left[-\dot\rho\,\mu - \dot\rho\,\left(\tfrac12 m v^2\right) + \mathbf h\cdot\dot{\mathbf p} - \sigma_{\alpha\beta}v_{\alpha\beta} + r\,\Delta\mu\right]$$

(forma esquemática, ver ecuación (30) del original). De aquí, tras usar las leyes de conservación (masa y momento) e integrar por partes, se identifican pares flujo-fuerza: el tensor de esfuerzos σ conjugado con la tasa de deformación (strain rate) v_{αβ}, el campo molecular **h** conjugado con la derivada corrotacional de **p**, y la tasa de reacción r conjugada con Δμ.

### 4.2 Relaciones constitutivas y el esfuerzo activo

Aplicando el procedimiento de Onsager (relación lineal más general entre flujos y fuerzas compatible con las simetrías, separando componentes reactivas y disipativas según su signo de reversión temporal), se llega —para el caso incompresible— a las ecuaciones hidrodinámicas del gel activo polar/nemático de una componente:

$$m(\partial_t + \mathbf v\cdot\nabla)\mathbf v = -\nabla P + \nabla\cdot\sigma$$

$$(\partial_t + \mathbf v\cdot\nabla)\mathbf p + \omega\times\mathbf p = \nu\, v\cdot\mathbf p + \frac{1}{\gamma_1}\mathbf h + \lambda_1\,\zeta\,\Delta\mu\,\mathbf p$$

con la condición de incompresibilidad ∇·**v** = 0. El tensor de esfuerzos se separa en una parte pasiva (viscosa + elástica, como en un cristal líquido pasivo) y una parte puramente **activa**:

$$\sigma^{\text{activo}}_{\alpha\beta} = -\zeta\,\Delta\mu\; Q_{\alpha\beta}$$

Este es, junto con las ecuaciones de Toner-Tu, el **resultado central del formalismo de geles activos**: un esfuerzo mecánico anisótropo generado internamente, proporcional al parámetro de orden nemático **Q** (o, equivalentemente, a **pp**), con un coeficiente de actividad ζΔμ cuyo **signo** determina el carácter del sistema:

- **ζ < 0** (o convención de signo equivalente): esfuerzo **contráctil**, como el generado por motores de miosina en el citoesqueleto de actina (los motores tienden a contraer el gel).
- **ζ > 0**: esfuerzo **extensil** (extensile), como el observado en ciertas suspensiones bacterianas nadando (bacterias tipo "pusher").

Esta distinción contráctil/extensil (o, en el lenguaje de nadadores individuales, "pullers" vs. "pushers") es la que gobierna gran parte de la fenomenología del capítulo de inestabilidades y reología del review: el signo del esfuerzo activo determina si el estado uniformemente ordenado de un sistema con momento conservado es estable o genéricamente **inestable** frente a fluctuaciones de longitud de onda larga.

### 4.3 Un resultado global destacado: inestabilidad genérica del estado ordenado húmedo

Un hallazgo transversal del review (repetido en las conclusiones) es que, a diferencia de los sistemas secos —donde el estado ordenado uniforme puede ser estable lejos de la transición—, el estado ordenado uniforme de un sistema **húmedo** (con momento conservado), tanto polar como nemático, es **genéricamente inestable** en el régimen de Stokes (bajo número de Reynolds), como consecuencia directa del acoplamiento entre el esfuerzo activo y el flujo. El resultado final de esta inestabilidad, en muchos casos, es un régimen de "turbulencia de bajo número de Reynolds" (observado en suspensiones bacterianas densas), producto de la competencia entre el forzado por el esfuerzo activo y la relajación por difusión orientacional.

### 4.4 Defectos activos

En fases ordenadas de materia activa aparecen configuraciones de defectos topológicos análogas a las de cristales líquidos en equilibrio (asters, vórtices, espirales de carga +1 en sistemas polares; defectos de carga ±1/2 en sistemas nemáticos), pero con una propiedad extra genuinamente activa: los flujos generados por el esfuerzo activo hacen que estos defectos roten o se **trasladen espontáneamente**, con sentido determinado por la quiralidad o polaridad del defecto — algo sin análogo en cristales líquidos pasivos, y observado experimentalmente en mezclas de microtúbulos y kinesina.

---

## 5. Derivación microscópica de la hidrodinámica: el ejemplo de Vicsek

El review dedica una sección completa a mostrar, paso a paso, cómo se puede *derivar* rigurosamente (bajo aproximaciones de baja densidad e interacción débil, tipo "caos molecular") las ecuaciones continuas a partir de un modelo microscópico concreto de partículas tipo Vicsek con interacción angular de alineación polar.

El procedimiento general es:

1. Se parte de ecuaciones de Langevin acopladas para posición **r**ₙ(t) y ángulo θₙ(t) de cada partícula, con autopropulsión a rapidez fija v₀, fuerzas/torques derivados de un potencial de interacción par a par (que tiende a alinear partículas dentro de un rango R), y ruido gaussiano blanco.
2. Se transforman estas ecuaciones de Langevin en una **ecuación de Smoluchowski** para la densidad de probabilidad de una partícula c(**r**,θ,t).
3. Se expande c en momentos angulares (transformada de Fourier angular), obteniendo una jerarquía de ecuaciones para los coeficientes f_k(**r**,t): f₀ = ρ (densidad), f₁ relacionado con la polarización **p**, f₂ con el tensor **Q**, etc.
4. Se trunca la jerarquía asumiendo que los modos de orden angular alto (k ≥ 2 o 3) son "rápidos" (relajan instantáneamente, ∂ₜf₂ ≈ 0) y se eliminan en favor de ρ y **p**, quedando así un cierre cerrado para las ecuaciones hidrodinámicas de ρ y **p**.

El resultado (ecuaciones (84)-(85) del original) reproduce exactamente la **misma estructura funcional** que las ecuaciones fenomenológicas de Toner-Tu de la Sec. 3, pero ahora con **todos los coeficientes expresados explícitamente en términos de parámetros microscópicos** (v₀, el rango de interacción R, la intensidad de interacción ζ, etc.):

$$\alpha(\rho) = \zeta\rho - \frac{1}{2}, \qquad \beta = \frac{\zeta^2\rho}{8R}, \qquad \lambda_1 = \frac{3v_0}{16R},\ \dots$$

Este ejercicio es importante conceptualmente porque confirma la tesis central del review: modelos microscópicos distintos (partículas tipo Vicsek, filamentos con motores, varillas autopropulsadas) que comparten la misma simetría del estado ordenado dan lugar a ecuaciones hidrodinámicas con la **misma forma general**, difiriendo solo en los valores (y en algunas dependencias funcionales, p. ej. lineal vs. cuadrática en v₀) de los coeficientes de transporte.

También se discute cómo incorporar interacciones hidrodinámicas (acoplamiento con un campo de velocidad de fluido **v**(**r**,t)) cuando el sistema es húmedo: se agrega una ecuación de tipo Navier-Stokes o Stokes para **v**, acoplada a la concentración y orientación de las partículas activas, con las fuerzas activas de los nadadores entrando como una contribución activa adicional al tensor de esfuerzos — cerrando así el círculo con el formalismo de geles activos de la Sec. 4.

---

## 6. Conclusiones generales del review

Los autores resumen los resultados más robustos y transversales de todo el programa de "hidrodinámica activa":

- Las bandadas polares sobre un sustrato (manadas, queratocitos sobre un vidrio, modelos tipo Vicsek/Toner-Tu) exhiben **orden de largo alcance en 2D**, algo imposible en equilibrio térmico (donde rige el teorema de Mermin-Wagner). Esta es una de las diferencias cualitativas más fuertes entre materia activa y materia pasiva.
- Tanto las fases ordenadas nemáticas como las polares (en sistemas sobre sustrato) exhiben **fluctuaciones de densidad gigantes**, rompiendo la escala ⟨N⟩^(1/2) esperada en equilibrio.
- El estado ordenado uniforme de sistemas húmedos (con momento conservado), de simetría polar o nemática, es **genéricamente inestable** en el régimen de Stokes; el resultado típico de esta inestabilidad es un régimen de turbulencia de bajo número de Reynolds, producto de la competencia entre el forzado por esfuerzo activo y la relajación orientacional difusiva.
- Todos estos sistemas pueden sostener un nuevo tipo de **ondas sonoras propagantes**, con velocidades de propagación distintas en direcciones opuestas debido a la polaridad (ausencia de invariancia galileana).

El review también insiste en que estas propiedades no son solo predicciones teóricas: se han confirmado tanto en simulaciones a gran escala (modelos tipo Vicsek, geles activos numéricos) como en experimentos (materia granular vibrada, suspensiones bacterianas, extractos citoesqueléticos, mezclas de microtúbulos-kinesina).

Como líneas de trabajo futuro se identifican: la incorporación de señalización bioquímica explícita (más allá de simetría y conservación) para entender fenómenos como cicatrización de heridas, división celular; el acoplamiento de la física de geles activos con reacciones químicas (p. ej. estructuras de Turing en rangos de existencia ampliados); la investigación del rol de "líderes" en bandadas (rompiendo la simetría "democrática" asumida hasta entonces); y el desarrollo de sistemas artificiales tridimensionales controlados (coloides accionados por luz o reacciones químicas) que permitan variar los parámetros de activación de forma controlada, algo difícil de lograr con sistemas puramente vivos.

---

## 7. Relevancia para los TPs de la materia (nota de contexto, no parte del original)

Para el TP2, centrado en modelos tipo Vicsek/flocking, las secciones más directamente aplicables de este review son:

- La Sec. 3 completa (equivalente a la Sec. II.A del original): el modelo continuo de Toner-Tu, sus dos fases (isótropa/ordenada), la transición orden-desorden, la naturaleza (discontinua, con bandas viajeras) de esa transición, y las fluctuaciones gigantes de densidad — todos fenómenos que también deberían observarse al simular directamente el modelo de Vicsek discreto.
- La Sec. 5 (derivación microscópica), que muestra explícitamente **cómo pasar** de las reglas de actualización de un modelo de partículas tipo Vicsek a una ecuación de campo continua, algo útil como referencia conceptual si el TP pide conectar la simulación de agentes con una descripción de campo medio/hidrodinámica.
- La discusión de bandas de densidad-orden cerca de la transición (Sec. 3.5) es directamente comparable con lo que se observa al barrer el parámetro de ruido η (o la densidad) en una implementación numérica del modelo de Vicsek: la aparición de bandas viajeras en vez de una transición continua suave es el fenómeno esperado según el consenso numérico actual citado en el review.
