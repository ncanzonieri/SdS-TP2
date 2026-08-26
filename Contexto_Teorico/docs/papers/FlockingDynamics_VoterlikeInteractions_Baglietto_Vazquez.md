# Dinámica de flocking con interacciones tipo votante (Baglietto & Vazquez, 2019)

*Fuente original: `Flocking dynamics with voterlike interactions.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

## Motivación y pregunta de investigación

Gabriel Baglietto y Federico Vázquez (IFLYSIB, UNLP-CONICET, La Plata) proponen y estudian un modelo de partículas autopropulsadas (flocking) en el que, a diferencia del Modelo Estándar de Vicsek (SVM) —donde cada partícula adopta el promedio de las direcciones de todos sus vecinos dentro de un radio de interacción—, la regla de actualización de dirección es de tipo **modelo de votante (voter model)**: cada partícula copia la dirección de **un único vecino elegido al azar** dentro de su radio de interacción, en lugar de promediar sobre todos ellos.

La motivación proviene de dos tradiciones que hasta entonces se habían desarrollado en paralelo:
- La física estadística de la **formación de opiniones/consenso** (modelo de votante clásico de Clifford-Sudbury y Holley-Liggett), ampliamente estudiada en redes/retículos estáticos, donde la imitación local produce dominios del mismo "spin" que crecen hasta que uno invade todo el sistema (consenso), con tiempos de consenso que escalan como N² (1D), N ln N (2D) y N (3D, campo medio).
- La física del **flocking** (Vicsek et al. 1995 y sucesores), donde el estado de cada partícula (su dirección de movimiento) determina también su posición futura, acoplando dinámica de opinión y dinámica espacial —algo ausente en los modelos de votante clásicos, donde los agentes son fijos.

Trabajos previos habían introducido movilidad en modelos de opinión (Sznajd con movilidad, Naming Game con difusión) pero sin acoplar la opinión a la dirección de desplazamiento. Otros trabajos (Couzin et al. 2011 con peces; Huepe et al. 2011 con langostas, inspirado en experimentos de Buhl et al. 2006) sí acoplan opinión y dirección de movimiento, pero con espacio de opiniones binario (dos direcciones posibles) y, en el caso de Huepe et al., con topología de red no espacial (mean-field). La novedad del modelo propuesto (**Flocking Voter Model, FVM**) es combinar: (a) un continuo de direcciones posibles en (−π, π], como en el SVM, (b) interacción de tipo votante (copiar a un solo vecino, no promediar), y (c) interacciones métricas genuinamente espaciales en 2D continuo (no mean-field). El objetivo es caracterizar cómo esta regla de imitación "de a uno" —más simple y más "ruidosa" intrínsecamente que el promedio del SVM— afecta la dinámica de ordenamiento y el tiempo hasta alcanzar consenso polar completo, sin necesidad de agregar ruido explícito (a diferencia del SVM, que típicamente requiere ruido para exhibir una transición de fase orden-desorden no trivial).

## Metodología: el modelo (FVM)

Se consideran N partículas moviéndose en un espacio 2D continuo [0,L]² con condiciones de contorno periódicas y densidad conservada ρ = N/L². Cada partícula i tiene posición r_i^t y velocidad de módulo constante v y dirección θ_i^t. En cada paso de tiempo (Δt=1), la partícula i elige al azar un vecino j dentro de un radio de interacción R=1 y:

- se desplaza según su dirección actual (regla de "backward update", igual que en la formulación original de Vicsek): r_i^{t+1} = r_i^t + v_i^t Δt
- adopta como nueva dirección la dirección actual de j: θ_i^{t+1} = θ_j^t

Si la partícula no tiene vecinos dentro del radio R, su dirección no cambia. Las posiciones iniciales se distribuyen uniformemente al azar en la caja, y las direcciones iniciales se sortean uniformemente en (−π, π]. Los autores discuten la ambigüedad "backward vs forward update" (relevante en el SVM) y argumentan que a bajas velocidades el comportamiento cualitativo del FVM debería ser el mismo bajo ambas convenciones, aunque podrían aparecer diferencias a altas velocidades.

El orden global se mide con el parámetro de orden polar:

  ϕ ≡ (1/(vN)) |Σ_{i=1}^{N} v_i|

que va de 0 (desorden total) a 1 (orden total, todas las partículas moviéndose en la misma dirección — estado de "consenso" análogo al del modelo de votante clásico, aunque aquí no es un estado congelado porque las partículas siguen moviéndose).

**Enfoque analítico auxiliar.** Para entender la dinámica de ϕ se recurre al número medio de direcciones distintas presentes en el sistema, S(t). En el límite de campo medio (todas las partículas interactuando entre sí, equivalente a alta densidad) existe una expresión analítica previa (Starnini, Baronchelli & Pastor-Satorras 2012; Pickering & Lim 2016) para el modelo de votante multi-estado bajo grafo completo. Combinando esa expresión con una aproximación de distribución uniforme de direcciones (válida en el límite S≫1, usando el teorema central del límite sobre las componentes x,y del vector resultante y la distribución de Rayleigh del módulo) se deriva una fórmula aproximada para ⟨ϕ(t)⟩ en campo medio, que se contrasta con simulaciones 2D a distintas densidades y velocidades.

**Estudio del tiempo de consenso.** Se mide el tiempo medio de consenso τ (tiempo hasta ϕ=1) en función de la densidad ρ, la velocidad v y el tamaño del sistema N, promediando sobre miles de realizaciones independientes, y se comparan los regímenes estático (v=0, análogo al modelo de votante en retículo/red aleatoria geométrica) y dinámico (v>0).

**Análisis de mecanismo (clustering y drift).** Para explicar el comportamiento no monótono de τ(ρ) se introducen indicadores adicionales: el grado medio de vecinos ⟨k⟩(t), y una medida de "drift" o flujo neto de partículas entre direcciones D(t), definida a partir de las probabilidades de transición entre direcciones ponderadas por el tamaño relativo de los clusters de cada dirección, así como la covarianza entre el tamaño de un cluster (masa m) y el grado medio ⟨k⟩ de sus miembros.

## Ecuaciones y fórmulas clave (transcriptas)

- Actualización de posición y dirección:
  r_i^{t+1} = r_i^t + v_i^t Δt   (1a)
  θ_i^{t+1} = θ_j^t        (1b)

- Parámetro de orden polar:
  ϕ ≡ (1/(vN)) | Σ_{i=1}^{N} v_i |

- Decaimiento del número de direcciones distintas en campo medio (multi-state voter model, grafo completo, actualización sincrónica reescalada por 1/2):
  S(t) ≃ N / (1 + t/2)

- Aproximación de campo medio para el parámetro de orden en función de S(t):
  ⟨ϕ⟩ ≃ (√π / 2) · S^(−1/2)

- Combinando ambas, aproximación temporal de ⟨ϕ(t)⟩:
  ⟨ϕ(t)⟩ ≃ (√π / 2) · ((1 + t/2)/N)^(1/2)

- Régimen de baja densidad / alta velocidad para el tiempo de consenso (derivado de rescalar el tiempo de consenso de campo medio τ_MF ≈ 2N por la probabilidad p ≈ πρ de que una partícula tenga al menos un vecino):
  τ ≈ 2N / (πρ)   para ρ ≤ 1/π

- Tiempo de consenso de campo medio (referencia, alta densidad): τ_MF ≈ 2N

- Escalamiento del tiempo mínimo de consenso con el tamaño del sistema (ajuste numérico, régimen 2400 ≤ N ≤ 76800):
  τ_min ~ N^0.765  (γ = 0.765 ± 0.018), con τ_min = 2.378 · N^0.765

- Densidad óptima (donde τ es mínimo) en función de N:
  ρ_min ≈ 0.16 · N^0.42  (β = 0.42 ± 0.09)

- Drift neto entre direcciones (definición):
  D(β→α, t) ≡ Σ_{i: θ_i=β} p(θ_i→α, t)
  D(t) = Σ_α Σ_β sign(m_α − m_β) · D(β→α, t)

## Resultados principales

1. **Ordenamiento más lento que en el SVM sin ruido, pero con la misma ley de potencia inicial.** El FVM alcanza el consenso completo (ϕ=1) en todos los casos estudiados, pero mucho más lentamente que el SVM sin ruido. Sin embargo, ambos modelos comparten un crecimiento inicial de ϕ como ley de potencia con exponente cercano a **1/2**, seguido de una aproximación exponencial final al orden total. Los autores especulan que este exponente 1/2 podría estar relacionado con exponentes de coarsening reportados en la fase ordenada del SVM con ruido.

2. **Relación entre orden y diversidad de direcciones.** La disminución de S(t) sigue inicialmente la predicción de campo medio del modelo de votante multi-estado (decaimiento tipo N/t), pero para densidades intermedias/altas y con movimiento (v>0) el decaimiento se acelera y pasa a ser exponencial —señal de un mecanismo adicional no presente en campo medio ni en el modelo de votante estático clásico.

3. **Tiempo de consenso no monótono en la densidad.** τ(ρ) decrece con la densidad en el caso estático (v=0), acercándose al valor de campo medio (τ_MF ≈ 2N) para N grande, con correcciones logarítmicas a baja densidad consistentes con el comportamiento 2D conocido del modelo de votante (τ ~ N ln N). En el caso dinámico (v>0) aparece un comportamiento cualitativamente distinto: τ es mucho mayor que τ_MF a bajas densidades (por la escasez de encuentros entre partículas, que introduce un retardo en la interacción), decae hasta un valor mínimo τ_min en una densidad óptima ρ_min, y luego vuelve a crecer y saturar al valor de campo medio a densidades altas. Es decir, existe una **densidad óptima para la cual el consenso se alcanza más rápido que en cualquier otro régimen, incluido el de campo medio** (interacciones de todos con todos).

4. **Escalamiento sublineal del tiempo mínimo de consenso.** En la densidad óptima, el tiempo mínimo de consenso escala como τ_min ~ N^0.765, más lento que el crecimiento lineal τ_MF ~ N de campo medio — confirmando que el consenso a densidad óptima es genuinamente más rápido que en el límite de todos-con-todos, y no solo un artefacto de tamaño finito.

5. **Mecanismo: segregación espacial en clusters y ruptura de simetría entre direcciones.** El fenómeno se explica por la formación dinámica de clusters espaciales de partículas con la misma dirección (visible en snapshots del sistema: al alinearse, partículas cercanas "se pegan" y se mueven juntas hasta que una de ellas cambia de dirección al interactuar con una tercera partícula). A diferencia del modelo de votante clásico en topologías regulares —donde todas las direcciones/opiniones son equivalentes y el flujo neto entre estados es cero, de modo que el coarsening depende solo de fluctuaciones—, en el FVM los clusters más grandes tienden en promedio a tener mayor número de vecinos (covarianza positiva entre masa del cluster y grado medio ⟨k⟩ de sus miembros), lo que genera un **drift neto positivo de partículas desde clusters chicos hacia clusters grandes** (D(t) > 0), rompiendo la simetría entre estados direccionales y acelerando la aproximación al consenso respecto del campo medio. Este mecanismo es análogo a fenómenos conocidos de modelos de votante en redes complejas, donde se conserva la "magnetización pesada" (ponderada por grado) en lugar de la magnetización simple.

6. **Régimen de baja densidad / alta velocidad.** Se deriva una aproximación analítica τ ≈ 2N/(πρ) para bajas densidades y altas velocidades, bajo el supuesto de que a alta velocidad la distribución espacial de partículas se mantiene aproximadamente uniforme (sistema "bien mezclado") y el retardo respecto de campo medio se debe simplemente a la baja probabilidad de que una partícula tenga al menos un vecino dentro del radio de interacción en cada paso. Esta aproximación ajusta razonablemente bien a altas velocidades y bajas densidades, pero subestima τ a densidades intermedias, donde domina el efecto de clustering.

7. **Conclusión y líneas futuras explícitas.** El FVM ilustra que un mecanismo de imitación mucho más simple que el promedio del SVM (copiar a un solo vecino al azar) igualmente conduce a consenso polar completo sin necesidad de ruido, pero con una dinámica de ordenamiento cualitativamente distinta, dominada por la interacción no trivial entre movimiento y topología de interacciones cambiante en el tiempo. Los autores señalan explícitamente como trabajo futuro: (a) estudiar el caso de interacciones no métricas (vecinos topológicos fijos, à la Ballerini/Cavagna, en lugar de radio de interacción fijo), anticipando que la dependencia con la densidad podría desaparecer, como ocurre en el SVM con interacciones topológicas; y (b) introducir ruido en la dirección de movimiento, como en el SVM, para estudiar una versión extendida del FVM.

## Referencia bibliográfica completa

Baglietto, G., & Vazquez, F. (2019). Flocking dynamics with voter-like interactions. *arXiv preprint* arXiv:1608.08231v3 [physics.soc-ph]. IFLYSIB, Instituto de Física de Líquidos y Sistemas Biológicos (UNLP-CONICET), La Plata, Argentina.
