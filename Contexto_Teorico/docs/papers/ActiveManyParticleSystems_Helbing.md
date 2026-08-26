# Traffic and Related Self-Driven Many-Particle Systems (Active Many-Particle Systems)

*Fuente original: `ActiveManyParticleSystems.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

Dirk Helbing (Institute for Economics and Traffic, TU Dresden). Publicado en B. Kramer (Ed.), *Advances in Solid State Physics* **41**, 357–369 (2001), Springer.

## Idea general

El texto es un review corto que presenta el "paradigma" de los sistemas de muchas partículas **auto-impulsadas** (self-driven / activas / "motorizadas") como marco unificado de la física estadística fuera del equilibrio, aplicado principalmente a tráfico vehicular y dinámica de peatones, con extensión especulativa a sistemas socioeconómicos (donde "partículas" serían acciones, bienes o individuos). La tesis central: muchas propiedades de transporte de estos sistemas se capturan generalizando de forma mínima la ecuación de Newton, agregando un término de impulso propio (self-propulsion) y fricción disipativa, en vez de fuerzas puramente conservativas entre partículas.

## 1. Marco general: de Newton a partículas activas

Punto de partida: sistema de N cuerpos con fuerzas de interacción por pares,
$$m_i \ddot{x}_i(t) = \sum_{j(\neq i)} f_{ij}(t)$$
válido, por ejemplo, para cuerpos celestes bajo fuerzas conservativas (potencial → hamiltoniano).

Para sistemas *impulsados* (driven), como fluidos bajo gradientes de presión o medios granulares vibrados, hace falta agregar interacción con el entorno: fuerza externa $f^0(x,t)$, fricción disipativa $f^{fr}_i(t) = -\gamma_i v_i(t)$, y fluctuaciones individuales $\zeta_i(t)$ (ruido térmico o de otro origen):
$$m_i \ddot{x}_i(t) = f^0(x_i(t), t) - \gamma_i v_i(t) + \sum_{j(\neq i)} f_{ij}(t) + \zeta_i(t)$$

La competencia entre fuerza impulsora y fricción disipativa produce redistribución espacio-temporal de energía y da lugar a fenómenos de autoorganización, gracias a las no linealidades que amplifican perturbaciones pequeñas y estabilizan patrones lejos del equilibrio.

**Generalización a partículas "activas"**: a diferencia de un sistema físico convencional, en sistemas vivos/sociales las fuerzas de interacción $f_{ij}$ no tienen por qué cumplir la 3ª ley de Newton (acción-reacción, $f_{ji} = -f_{ij}$), y cada partícula puede tener su propia fuerza impulsora individual $f^0_i(t)$ en vez de una fuerza externa común. Reescribiendo en términos de aceleración (llamada "fuerza generalizada" $a_{ij}$):
$$\dot{v}_i(t) = v^0_i(t)\, e^0_i(t) + \xi_i(t) - \frac{v_i(t)}{\tau_i} + \sum_{j(\neq i)} a_{ij}(t)$$

Interpretación de cada término:
- $v^0_i e^0_i$: velocidad y dirección "deseadas" o de equilibrio de la partícula *i* cuando está suficientemente lejos de otras (sin interacción, $a_{ij}=0$).
- La adaptación hacia esa velocidad deseada es exponencial en el tiempo, con constante de relajación $\tau_i$ (término $-v_i/\tau_i$ combinado con $v^0_i e^0_i/\tau_i$ implícito).
- $\xi_i(t)$: fluctuaciones individuales (ruido).
- $\sum a_{ij}$: interacciones de corto alcance y repulsivas con otras partículas (supuesto adoptado en el resto del review).

Este es el "modelo social de fuerzas" (social force model) generalizado que se particulariza después para tráfico vehicular (1D) y peatones (2D).

## 2. Tráfico vehicular en autopistas (sistema 1D)

Se modela el tráfico en un único carril con **modelos de seguimiento de vehículo** (car-following): cada vehículo *i* reacciona principalmente al vehículo que lo precede (i−1), ignorando la reacción del que lo sigue:
$$\frac{dv_i}{dt} = \frac{v^0_i - v_i(t)}{\tau_i} + a_{i(i-1)}(t)$$

En el caso simplificado con conductores/vehículos idénticos ($v^0_i=v^0$, $\tau_i=\tau$), se define la **"velocidad óptima"** dependiente del tráfico:
$$V(s_i, v_i, \Delta v_i) = v^0 + \tau\, a(s_i, v_i, \Delta v_i) \le v^0$$
donde $s_i$ es la distancia al vehículo de adelante y $\Delta v_i$ la velocidad relativa (approaching rate). El conductor *i* intenta adaptar su velocidad real a esta velocidad óptima en un tiempo de relajación $\tau$.

### 2.1 "Atascos fantasma" (phantom traffic jams)

Si la velocidad óptima depende solo de la distancia $s_i$, se obtiene la relación fundamental flujo-densidad en tráfico homogéneo (con $\rho=1/s$ la densidad vehicular):
$$Q_f(\rho) = \rho\, V(1/\rho)$$

Puntos clave:
- Existe un régimen **linealmente inestable** en el que perturbaciones pequeñas del flujo se amplifican hasta formar un estado congestionado (zonas de alta densidad/baja velocidad) — esto ocurre incluso **sin accidente ni cuello de botella**: es un "atasco fantasma" producto de una reacción en cadena de sobre-frenados individuales. El mecanismo: el tiempo de adaptación finito $\tau$ produce una reacción retrasada; un vehículo se acerca demasiado al de adelante, tiene que frenar de más, y si el vehículo siguiente llega antes de que la perturbación se disipe, la sobre-reacción se propaga y amplifica hacia atrás hasta llegar al estándstill.
- Los regímenes linealmente estables se dividen en un régimen **absolutamente estable** (hasta perturbaciones grandes se disipan) y un régimen **metaestable** adyacente al inestable, caracterizado por una "amplitud crítica": perturbaciones menores a esa amplitud decaen, las mayores crecen (efecto de nucleación).
- El tráfico es estable cuando la función $V(s)$ varía poco con $s$ (densidad muy baja = tráfico libre, o densidad muy alta = velocidad ya de por sí baja). El problema aparece en densidades intermedias (~25 vehículos/km/carril, correspondiente a velocidades por debajo de ~85 km/h), donde $V(s)$ cae rápido con la distancia.
- Una vez formado, el atasco no se disuelve fácilmente porque los vehículos que salen del frente del atasco (downstream) pierden tiempo al acelerar, lo que reduce el flujo de salida $Q_{out}$ respecto al flujo máximo teórico $Q_{max}$ de tráfico homogéneo (la capacidad "nominal" de la vía). Este $Q_{out}$ actúa como una segunda capacidad, "dinámica", una especie de constante autoorganizada del flujo de tráfico.

### 2.2 Variedad de estados de tráfico congestionado

Cerca de cuellos de botella (rampas de acceso, etc.), según la relación entre el volumen de tráfico entrante $Q_{up}$ y el incremento de flujo en la rampa $\Delta Q$, se observa un diagrama de fases con varios estados posibles (Fig. 1 del original):
- **FT** (Free Traffic / tráfico libre): volúmenes bajos.
- **HCT** (Homogeneous Congested Traffic): congestión homogénea y estable — el clásico atasco de "temporada alta".
- **OCT** (Oscillating Congested Traffic) y **TSG** (Triggered Stop-and-Go traffic): aparecen cuando el flujo congestionado es linealmente inestable; a menudo emergen juntos en secuencia espacial (llamado "efecto pinch"). El TSG se caracteriza por una secuencia de atascos móviles separados por tramos de flujo libre, cada uno disparando al siguiente por un mecanismo de "efecto boomerang" (una perturbación pequeña viaja aguas abajo, pero si crece lo suficiente invierte su dirección de propagación).
- **MLC** (Moving Localized Cluster) y **PLC** (Pinned Localized Cluster): aparecen en el régimen metaestable (volumen de tráfico más reducido); el PLC queda anclado en la ubicación de la rampa si el tráfico aguas arriba es estable.

## 3. Dinámica colectiva de peatones (sistema 2D)

Los peatones tienen un tiempo de adaptación mucho más corto ($\tau_i \approx 0.5$ s) que los vehículos, por lo que **no aparecen los fenómenos de inestabilidad tipo atasco fantasma** vistos en tráfico vehicular. En cambio dominan otros efectos de autoorganización, modelados con el "modelo de fuerzas sociales" (social force model, Helbing & Molnár 1995).

Fuerza de interacción entre dos peatones *i, j* (tendencia psicológica a mantener distancia, más fuerzas de contacto físico si se tocan, relevantes en situaciones de pánico):
$$f_{ij} = \{A_i \exp[(r_{ij}-d_{ij})/B_i] + k\,\Theta(r_{ij}-d_{ij})\}\, n_{ij} + \kappa\,\Theta(r_{ij}-d_{ij})\, \Delta v^t_{ji}\, t_{ij}$$

donde $A_i, B_i$ son constantes de la repulsión psicológica exponencial, $d_{ij}$ la distancia entre centros de masa, $n_{ij}$ la dirección normal entre peatones, $\Theta(x)$ es cero si no hay contacto físico ($d_{ij}>r_{ij}$) y vale $x$ si lo hay; el término con $k$ es una "fuerza de cuerpo" (compresión física) y el término con $\kappa$ una fricción tangencial de deslizamiento (relevante solo en aglomeraciones/pánico). Se define de forma análoga la fuerza de interacción con paredes/obstáculos $f_{iW}$.

### 3.1 Formación de carriles ("lane formation") y "freezing by heating"

- En flujos de peatones en direcciones opuestas dentro de un corredor, las simulaciones reproducen la formación espontánea de **carriles** (lanes) de gente caminando en la misma dirección — un fenómeno observado empíricamente. El mecanismo: los peatones que se cruzan en direcciones opuestas tienen una velocidad relativa alta, por lo que interactúan (colisionan/evitan) con más frecuencia hasta segregarse en carriles separados, lo cual minimiza la frecuencia e intensidad de las maniobras de evasión — es un estado que además maximiza la eficiencia del movimiento colectivo (autoorganización que tiende a optimizar globalmente el sistema).
- El número de carriles depende del ancho de la calle, la densidad de peatones y el nivel de ruido/fluctuación.
- Efecto notable de **ordenamiento inducido por ruido**: niveles de ruido intermedios producen *más* segregación (menos carriles, más definidos) que niveles bajos; niveles de ruido muy altos producen el efecto contraintuitivo de **"freezing by heating"** ("congelamiento por calentamiento"): en vez de pasar del estado ordenado en carriles a un estado desordenado tipo "gas" (como se esperaría al aumentar el ruido/"temperatura"), el sistema pasa a un estado **sólido/cristalizado, bloqueado** — con mayor grado de orden estructural pese a tener más energía interna, aunque metaestable frente a perturbaciones (p.ej. el intercambio de peatones que se mueven en direcciones opuestas). Es la situación opuesta a la esperable en un sistema en equilibrio térmico. Requiere la combinación del término de impulso propio $v^0_i e^0_i/\tau_i$ y la fricción disipativa $-v_i/\tau_i$; no requiere el término de fricción de deslizamiento.
- Se modela el "nerviosismo" de un peatón *i* con un parámetro $n_i \in [0,1]$ que interpola el nivel de fluctuación entre un valor normal $\eta_0$ y uno máximo $\eta_{max}$: $\eta_i = (1-n_i)\eta_0 + n_i \eta_{max}$.

### 3.2 Cuellos de botella: oscilación de sentido, "faster-is-slower", y "phantom panics"

- En pasos angostos con flujo bidireccional (p. ej. una puerta), se observa **oscilación espontánea del sentido de paso dominante**: cuando un lado logra "ganar" el paso, se reduce la presión de espera de ese lado, lo cual eventualmente favorece que el otro lado recupere el paso, y así sucesivamente.
- En flujos unidireccionales por una salida angosta: con velocidades deseadas normales, el flujo de salida es regular; pero para velocidades deseadas altas (>1.5 m/s, "gente apurada") aparecen bloqueos intermitentes tipo arco (arching) en la salida, con "avalanchas" de gente saliendo de a ráfagas cuando el arco se rompe — fenómeno análogo al clogging intermitente en flujos granulares por embudos/tolvas.
- **Efecto "faster-is-slower"**: al intentar aumentar la velocidad deseada $v^0_i$ (por apuro/pánico), si el coeficiente de fricción interpersonal $\kappa$ es suficientemente alto, la velocidad *promedio* de salida termina siendo *menor* — resultado trágicamente relevante en evacuaciones de incendios, donde huir más rápido reduce las chances colectivas de supervivencia. Requiere la combinación de (1) un cuello de botella físico y (2) fricción interpersonal fuerte cuando los peatones están muy próximos entre sí.
- Consecuencia práctica de diseño: minimizar cuellos de botella en estadios/edificios públicos — pero atención, porque el atasco también puede ocurrir en **ensanchamientos** de las vías de escape (los peatones se dispersan lateralmente y luego deben "reapretarse" al final del ensanchamiento, que actúa como un cuello de botella encubierto). Colocar columnas asimétricamente frente a las salidas puede mejorar el flujo de salida y evitar picos de presión peligrosos.
- **"Phantom panics"**: pánicos que ocurren sin causa objetiva aparente (ejemplos citados: Moscú 1982, Innsbruck 1999). Se explican por el efecto faster-is-slower: pequeños contraflujos de peatones generan demoras; quienes están más atrás y no ven la causa del freno se ponen impacientes y empujan, lo cual se modela aumentando dinámicamente su velocidad deseada:
$$v^0_i(t) = [1-n_i(t)]\, v^0_i(0) + n_i(t)\, v^{max}_i, \qquad n_i(t) = 1 - \frac{v_i(t)}{v^0_i(0)}$$
El resultado puede derivar en situaciones de gente aplastada o pisoteada por exceso de presión.

## 4. Síntesis y perspectivas (cierre del review)

- La física (métodos de mecánica estadística y dinámica no lineal) contribuye de forma significativa a entender fenómenos de tráfico, biología y sistemas socioeconómicos bajo el paraguas común de sistemas de partículas activas.
- Falta desarrollar una "mecánica estadística" general para sistemas activos fuera del equilibrio, análoga a la que existe para sistemas que conservan momento y energía (¿existen principios generales tipo maximización de entropía, o análogos de la función de partición?) — a la fecha del review, esto solo estaba resuelto para casos específicos.
- Aplicaciones prácticas ya en uso (vínculo con proyectos industriales): límites de velocidad adaptativos, control inteligente de rampas de acceso, detección de incidentes, pronóstico de tráfico, sistemas de asistencia al conductor.
- El campo se presenta como un buen ejemplo de cercanía entre investigación aplicada y fundamental, con implicancias transferibles a sistemas biológicos y socioeconómicos (individuos compitiendo por recursos limitados: tiempo, dinero, energía).

## Relevancia para la materia

Este paper es una referencia directa para modelado de sistemas de partículas activas/auto-impulsadas con reglas de interacción locales (fuerzas repulsivas de corto alcance + impulso propio + fricción + ruido) — conecta con el enfoque de autómatas celulares / lattice gas de la materia en tanto ambos apuntan a fenómenos emergentes macroscópicos (flujo, congestión, formación de patrones) a partir de reglas microscópicas simples, aunque acá el modelo es continuo (ecuaciones diferenciales tipo Langevin) en vez de discreto en la grilla.
