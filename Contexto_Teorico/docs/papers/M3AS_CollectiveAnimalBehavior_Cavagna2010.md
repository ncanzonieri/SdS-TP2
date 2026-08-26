# De datos empíricos a interacciones: las reglas del comportamiento colectivo animal (Cavagna et al. 2010)

*Fuente original: `M3AS_20SUPPL.P1491.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

## Motivación y pregunta de investigación

El artículo parte de una pregunta central de la ecología del comportamiento y de la física de sistemas complejos: ¿qué reglas dinámicas locales siguen los individuos de un grupo animal (bandada de estorninos, cardumen, enjambre) para producir orden colectivo global sin líder ni estímulo externo (auto-organización)? Los autores (grupo de Roma: Cavagna, Cimarelli, Giardina, Parisi, Santagati, Stefanini, Tavarone) sostienen que la metodología de la física estadística —pensada para sistemas de partículas o espines con interacciones de corto alcance— es un marco natural para atacar este problema, porque:

- El comportamiento colectivo solo emerge cualitativamente distinto (efectos "more is different", en referencia a P. W. Anderson) cuando el número de individuos es grande; grupos pequeños no son representativos.
- El mecanismo microscópico (ajuste de velocidad a vecinos, atracción para no perder el grupo, repulsión para evitar colisiones) es formalmente análogo al alineamiento ferromagnético y a fuerzas de atracción-repulsión de líquidos, aunque el sistema es de no equilibrio (los animales se autopropulsan).
- La resiliencia de las bandadas ante perturbaciones (ataques de predadores) requiere mecanismos de transferencia de información y robustez estructural, temas centrales en física de sistemas con interacciones locales.

Hasta este trabajo, casi todos los estudios empíricos de grupos animales en 3D estaban limitados a decenas de individuos, por lo que los modelos de "self-propelled particles" (Vicsek et al. 1995 y sucesores) no habían sido contrastados con datos reales a gran escala. El objetivo del paper es mostrar cómo un análisis estadístico apropiado de datos de gran escala permite inferir propiedades de la interacción entre individuos —un insumo básico para los modelos teóricos— retomando y extendiendo un estudio previo de los mismos autores sobre bandadas de estorninos (con un dataset más grande, nunca antes analizado).

## Metodología

**Adquisición de datos (proyecto StarFlag).** Se realizaron experimentos estereoscópicos sobre bandadas de estorninos en pleno despliegue aéreo sobre el dormidero, durante dos temporadas (2005-2006 y 2006-2007), fotografiando a 10 cuadros por segundo (hasta 40 imágenes consecutivas por limitación de memoria de las cámaras). El problema técnico central de la reconstrucción 3D es el "matching" estereoscópico: dado que las fotografías muestran nubes de puntos densas y sin rasgos distintivos (miles de pájaros), no alcanza con técnicas estándar de visión por computadora (requieren niveles de ruido inalcanzables o son computacionalmente intratables para grandes números). Los autores resolvieron esto adaptando algoritmos de asignación (assignment) propios de la física estadística: un algoritmo recursivo que mejora iterativamente una medida de coincidencia basada en reconocimiento de patrones y en la transformación estereométrica conocida, integrado con un módulo de asignación final. En datos sintéticos la eficiencia promedio de matching correcto fue del 90% sobre miles de puntos. Esto permitió reconstruir bandadas de hasta ~4000 individuos (dos órdenes de magnitud más que el estado del arte previo), obteniendo coordenadas 3D y velocidades de cada ave para 19 eventos de bandada, con tamaños de cientos a miles de individuos, distintas densidades y velocidades (ver tabla de eventos en el original).

**Tratamiento del borde.** A diferencia de los modelos teóricos (que suelen asumir fluidos infinitos o condiciones periódicas), las bandadas reales tienen un borde bien definido, y los pájaros cercanos al borde tienen sesgos estadísticos triviales (parte del espacio a su alrededor está vacío). Para delimitar el borde sin asumir convexidad se usó el algoritmo de **alpha-shapes** (excavación del conjunto de puntos con esferas de radio α; α elegido para maximizar localmente la densidad del conjunto interno). Los sesgos de borde en los indicadores estadísticos se corrigieron con el **método de Hanish** (al calcular observables relativos al n-ésimo vecino, solo se consideran aves cuyo n-ésimo vecino está a una distancia menor que la distancia al borde de la bandada).

**Indicador de anisotropía y rango de interacción.** La idea metodológica central es usar la anisotropía espacial de los vecinos como "trazador" de la interacción: en un sistema de individuos no interactuantes los vecinos se distribuirían isotrópicamente en el espacio. Se define para cada ave i el vector normalizado hacia su n-ésimo vecino más cercano, y se estudia la distribución de cos(θ) entre ese vector y la dirección media de vuelo de la bandada. Empíricamente esta distribución es marcadamente anisotrópica para los primeros vecinos (es poco probable encontrar al vecino más cercano justo delante o detrás en la dirección de movimiento) y se aplana (se vuelve isotrópica) a medida que aumenta el orden n del vecino considerado. Para cuantificar esto de forma robusta se introduce la **matriz de anisotropía** y sus autovalores/autovectores (factores gamma), que decaen desde un valor alto en n=1 hasta el valor isotrópico 1/3 (ver fórmulas). El orden de vecino nc donde el factor gamma alcanza el valor isotrópico define el **rango de interacción topológico**.

**Distinción topológico vs. métrico.** Para bandadas homogéneas existe una relación entre el orden del vecino n y su distancia media rn (Ec. 4.2-4.3), de modo que el rango topológico nc y un rango métrico rc son dos descripciones equivalentes para una bandada dada, relacionadas por una ley de homogeneidad (Ec. 4.4). La clave del método es que, al comparar bandadas de **distintas densidades**, ambas cantidades no pueden ser simultáneamente independientes de la densidad: si la interacción fuera métrica, rc debería mantenerse constante y nc debería crecer con la densidad (linealmente en r1⁻¹); si es topológica, nc debería mantenerse constante y rc crecer linealmente con la distancia al vecino más cercano r1.

## Ecuaciones y fórmulas clave (transcriptas)

- Matriz de anisotropía: 
  M_{αβ}^{(n)} = (1/N) Σ_{i=1}^{N} u_i^α u_i^β  (donde u_i es el vector normalizado hacia el n-ésimo vecino de i)

- Valor isotrópico de los factores gamma (autovalores normalizados de M): 
  Γ1^iso(n) = Γ2^iso(n) = Γ3^iso(n) = 1/3

- Relación densidad-orden de vecino para agregaciones homogéneas: 
  n ∝ (4/3)π ρ r_n³ , equivalentemente n^(1/3) ∝ ρ^(1/3) r_n = r_n / r_1

- Relación entre rango topológico y rango métrico para una bandada: 
  n_c^(1/3) ∝ r_c / r_1

- Resultado numérico principal (promedio sobre todos los eventos): 
  ⟨n_c⟩ = 7.04 ± 0.6

## Resultados principales

1. **Anisotropía como huella de la interacción.** La distribución angular de vecinos es fuertemente anisotrópica para vecinos cercanos y se vuelve isotrópica más allá de un cierto orden n, lo que se interpreta como evidencia directa de interacción (en ausencia de interacción, la distribución sería uniforme para cualquier n).

2. **Naturaleza topológica de la interacción.** Al analizar bandadas de densidades muy distintas (19 eventos, de cientos a ~4150 aves), el rango topológico nc no muestra correlación significativa con la densidad ni con la distancia al vecino más cercano r1, mientras que el rango métrico rc sí crece linealmente con r1. Esto confirma —con un dataset mayor y nunca antes analizado— el hallazgo previo de Ballerini et al. (2008, PNAS): cada estornino interactúa en promedio con un **número fijo de vecinos (~7)**, independientemente de la distancia física a ellos, y no con todos los vecinos dentro de un radio métrico fijo, como asumían la mayoría de los modelos previos (incluido el modelo de Vicsek original).

3. **Interpretación funcional/evolutiva.** Los autores argumentan que la interacción topológica confiere mayor robustez estructural: si la interacción fuera métrica, al expandirse la bandada (por ejemplo durante un ataque de predador) el número de vecinos dentro del rango fijo caería drásticamente y podrían quedar individuos aislados (presas fáciles); con interacción topológica el número de vecinos con los que cada ave coordina no depende de cuán dispersa esté la bandada, preservando la cohesión del grupo ante perturbaciones disruptivas (predadores) o pasivas (obstáculos). Se menciona también la posible conexión con límites cognitivos de "subitizing" (capacidad de las aves de discriminar hasta ~7 objetos simultáneamente), sugiriendo que el número de vecinos topológicos podría estar determinado por restricciones sensorio-cognitivas de rastreo visual.

4. **Alcance del análisis y trabajo relacionado.** El análisis se centra en grados de libertad estructurales (posiciones, fuerzas de atracción-repulsión). Los autores señalan que un trabajo relacionado propio (Cavagna et al., "Scale-free correlations in starling flocks", PNAS 2010) estudió los grados de libertad orientacionales (alineación de velocidades) sobre los mismos eventos, encontrando que las correlaciones de velocidad son de **rango libre de escala** (scale-free) y se extienden con mínima atenuación a través de toda la bandada — resultado complementario que indica coherencia colectiva maximal frente a perturbaciones, aunque no permite inferir directamente un rango de interacción de alineación de la misma manera que se hizo con la anisotropía estructural.

5. **Metodología como aporte general.** Más allá del resultado sustantivo sobre estorninos, el paper reivindica el enfoque de "problema inverso" propio de la física estadística (inferir interacciones a partir de mediciones) como herramienta general para el estudio empírico del comportamiento colectivo animal, señalando que los métodos de máxima entropía —exitosos en redes neuronales— no son directamente aplicables a bandadas porque distintas bandadas no pueden tratarse como muestras independientes del mismo sistema y la red de interacción cambia continuamente en el tiempo.

## Referencia bibliográfica completa

Cavagna, A., Cimarelli, A., Giardina, I., Parisi, G., Santagati, R., Stefanini, F., & Tavarone, R. (2010). From empirical data to inter-individual interactions: Unveiling the rules of collective animal behavior. *Mathematical Models and Methods in Applied Sciences*, 20(Suppl.), 1491–1510. https://doi.org/10.1142/S0218202510004660
