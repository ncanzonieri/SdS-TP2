# Modelos de Lattice Gas (Autómatas Celulares de Gas Reticular)

*Fuente original: `02_Lattice Gas Models.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

## 1. Contexto y motivación

Los modelos de gas reticular (lattice gas cellular automata, LGCA) son los precursores históricos del método de Lattice Boltzmann (LBM). El capítulo los presenta con doble propósito: valor histórico y valor pedagógico, ya que ofrecen un marco intuitivo (aunque menos común, basado en aritmética booleana sobre una red triangular) para entender la idea de "gas sobre una red". No son estrictamente necesarios para aplicar LBM, pero ayudan a comprenderlo en profundidad.

## 2. Autómatas celulares (CA): fundamentos

Un autómata celular es una entidad algorítmica ubicada en un punto de una grilla/red que interactúa con sus vecinos idénticos. En cada paso de tiempo examina su propio estado y el de un cierto número de vecinos, y actualiza su estado según reglas simples. La evolución completa queda determinada únicamente por: (a) las reglas de actualización, y (b) las condiciones iniciales y de borde.

Los componentes básicos de un CA son: una teselación (tiling) del espacio, un reloj que marca el tiempo, y una regla de transición/actualización.

### 2.1 CA unidimensionales de 2 estados y 2 vecinos

El caso más simple: automátas en una línea 1D, considerando solo el propio estado y el de los dos vecinos adyacentes. Con 2 estados posibles (0 y 1), existen 256 reglas posibles de actualización. La regla se escribe simbólicamente como:

**aᵢ' = I(aᵢ₋₁, aᵢ, aᵢ₊₁)**

donde aᵢ' es el estado actualizado, I es una de las 256 funciones posibles, y aᵢ₋₁, aᵢ, aᵢ₊₁ son los estados iniciales del autómata y sus vecinos izquierdo y derecho.

Wolfram (1986, 2002) clasificó y analizó completamente estas 256 reglas. Cada regla corresponde a un número binario de 8 dígitos (de 00000000 a 11111111, es decir 0 a 255 en decimal). Procediendo de derecha a izquierda, cada dígito binario representa 2⁰, 2¹, 2², …, 2⁷. Para un valor n dado, se resuelve n = 4n₂ + 2n₁ + n₀ (con n₂, n₁, n₀ ∈ {0,1}) y el valor de I(n₂, n₁, n₀) es 0 o 1 según el dígito binario correspondiente.

**Ejemplo (Regla 18, binario 00010010):**

I(0,0,0) = 0
I(0,0,1) = 1
I(0,1,0) = 0
I(0,1,1) = 0
I(1,0,0) = 1
I(1,0,1) = 0
I(1,1,0) = 0
I(1,1,1) = 0

En general, para nₛ estados posibles y una vecindad de nₙ autómatas (incluyendo el propio), la tabla de actualización requiere **nₛ^(nₙ)** entradas.

A pesar de su simplicidad, este tipo de CA puede mostrar comportamiento caótico y aperiódico (clasificación de Wolfram). Se puede visualizar partiendo de una condición inicial aleatoria (p. ej. 50% de probabilidad de estado 1) y graficando generaciones sucesivas como líneas — esto es fácilmente implementable en una hoja de cálculo.

## 3. Modelo de gas reticular bidimensional (FHP)

Los modelos de gas reticular fueron propuestos como un método viable para resolver las ecuaciones de Navier-Stokes en un trabajo fundacional de **Frisch, Hasslacher y Pomeau (1986)** — de ahí el nombre **modelo FHP**. Este modelo usa una **red triangular equilátera** (hexagonal desde el punto de vista de vecindad), que garantiza isotropía en la solución.

Características del modelo:
- Los puntos de red están separados por 1 unidad de red (lu, *lattice unit*).
- Todas las partículas tienen una única velocidad: 1 lu por paso de tiempo (lu·ts⁻¹).
- En cada punto x puede haber hasta 6 partículas, una por cada una de las 6 direcciones posibles, definidas por:

  **eₐ = (cos(πa/3), sin(πa/3))**, con a = 1, 2, …, 6

  donde eₐ es el vector velocidad que apunta desde el origen (0,0) hacia la dirección discreta a.

- El estado de un sitio se representa con una cadena de variables booleanas **n = (n₁, n₂, …, n₆)**, donde nₐ = 0 o 1 indica ausencia o presencia de una partícula moviéndose desde x hacia el sitio vecino x + eₐ.

### 3.1 Evolución: streaming y colisión

Cada paso de tiempo consta de dos etapas:
1. **Propagación / streaming ("hopping")**: las partículas se mueven a nuevos sitios según su posición previa y su velocidad.
2. **Colisión**: las partículas que coinciden en un sitio colisionan y se dispersan según reglas de colisión predefinidas.

### 3.2 Reglas de colisión

Se consideran dos tipos de colisiones en el modelo FHP más simple:
- **Colisiones de 2 cuerpos** (dos partículas).
- **Colisiones de 3 cuerpos** (tres partículas).

Dos principios son esenciales para que el modelo reproduzca correctamente Navier-Stokes:
- **Conservación de masa.**
- **Conservación de momento** — dado que todas las partículas tienen igual masa y velocidad, esto se reduce a conservar la suma vectorial de las velocidades.

Las colisiones frontales (2 partículas opuestas, o 3 partículas separadas por 120°) tienen momento neto cero, por lo que el resultado post-colisión también debe tener momento neto cero. Existen múltiples configuraciones de salida posibles que conservan momento cero; el modelo elige aleatoriamente entre ellas (esto introduce ruido esencial para la hidrodinámica emergente). Para colisiones no frontales (p. ej. dos partículas separadas 60°) no existe ninguna configuración alternativa que conserve momento — por lo tanto el estado no cambia. Lo mismo aplica a colisiones de 5 y 6 partículas.

Modelos más complejos pueden incluir colisiones de 4 partículas y partículas en reposo (velocidad cero) (Rothman y Zaleski, 1997).

### 3.3 Implementación con variables de bits

Las 6 direcciones se codifican con letras A a F. Se usa un byte (8 bits) por sitio:
- Bits 1–6 (valores 1,2,4,8,16,32): presencia/ausencia de partícula en cada una de las 6 direcciones (A,B,C,D,E,F).
- Bit 7 (valor 64, variable **S**): indica presencia de un sólido en ese sitio.
- Bit 8 (valor 128, variable **R**): bit aleatorio (0 o 1) usado para elegir entre las configuraciones post-colisión equivalentes.

**Condición de borde "bounce-back":** en sitios con sólido, la partícula rebota directamente hacia atrás — A se convierte en D, B en E, C en F, y viceversa.

**Tabla de consulta (look-up table):** Se construye una tabla de 256 entradas (una por cada configuración posible de 8 bits) que mapea "configuración de entrada" → "configuración de salida". Inicialmente se llena de forma trivial (salida = entrada) y luego se modifican las entradas correspondientes a: (a) presencia de sólido (bounce-back), (b) colisiones frontales de 2 partículas (AD, BE, CF, con las dos alternativas según el bit aleatorio), y (c) colisiones frontales de 3 partículas (ACE, BDF, con sus alternativas).

Ejemplo de código (fragmento adaptado del paquete Lgapack, Rothman y Zaleski 1997):

```
table[A + D] = B + E;
table[B + E] = C + F;
table[C + F] = A + D;
table[A + D + EPS] = C + F;
table[B + E + EPS] = A + D;
table[C + F + EPS] = B + E;
table[A + C + E] = B + D + F;
table[B + D + F] = A + C + E;
table[A + C + E + EPS] = B + D + F + EPS;
table[B + D + F + EPS] = A + C + E + EPS;
```

(EPS representa el bit aleatorio R.)

### 3.4 Detalles prácticos adicionales

- **Ruido y promediado:** la aleatoriedad introducida en las colisiones frontales es esencial para simular hidrodinámica, pero genera mucho "ruido" en los campos instantáneos. Para obtener campos de flujo suaves comparables a la macroescala, se requiere promediado temporal y/o espacial significativo.
- **Remapeo de la red triangular:** la red triangular equilátera no es directamente cómoda para el cómputo (6 vecinos en vez de 4 u 8 como en una grilla cartesiana), por lo que se usa un esquema de remapeo donde las filas alternas se desplazan a izquierda o derecha. La separación vertical entre filas de nodos es **√3/2**.
- **Forzante (driving force):** el método más simple para inducir flujo es "voltear" el momento de una fracción seleccionada aleatoriamente de partículas — por ejemplo, convertir una fracción de partículas con dirección D en partículas con dirección A, lo que equivale a agregar momento neto en la dirección A.

### 3.5 Ejemplo de simulación

Con estos ingredientes se puede calcular hidrodinámica razonable a partir de solo 6 momentos de partícula por sitio y un puñado de reglas de colisión — lo cual resulta notable por la simplicidad subyacente que produce comportamiento tipo Navier-Stokes.

## 4. Ejercicios del capítulo (resumen)

1. Implementar la Regla 18 de Wolfram en una hoja de cálculo (fórmula tipo Excel dada en el original), variando la condición inicial.
2. Descargar y compilar LGAPACK (código fhp6_simp.c), correr con distintos parámetros (FORCING_RATE, TPRINT, TMAX, TAVG) y visualizar el perfil de velocidad resultante (tipo Poiseuille) con MATLAB.
3. Estimar la viscosidad cinemática de la simulación a partir de la velocidad máxima en x, la tasa de forzado (g) y el ancho del canal, y comparar contra el valor teórico de la viscosidad cinemática densidad-dependiente del gas reticular dado por Rothman y Zaleski (1997):

   **ν = (1/12)·[7/(1−f) − 3] − 1/8**

   donde **f** es la "densidad reducida" (número promedio de partículas por enlace de red).

   (Nota: la expresión original en el PDF aparece con una disposición tipográfica ambigua producto de la extracción OCR — la fórmula corresponde a la Ec. (8) del capítulo original; se recomienda cotejar el signo/orden exacto de los términos contra el PDF fuente antes de usarla en un informe formal.)

## 5. Conceptos clave para retener

- Un CA queda definido por: geometría de la red, regla de vecindad, y regla de actualización local.
- El modelo FHP es el primer gas reticular capaz de reproducir Navier-Stokes 2D; usa red triangular, 6 direcciones de velocidad unitaria, y dos pasos por iteración (streaming + colisión).
- La conservación de masa y momento en las colisiones microscópicas es la condición necesaria para emergencia hidrodinámica macroscópica.
- La aleatoriedad en la elección de colisiones equivalentes es funcionalmente necesaria (no un defecto).
- La implementación práctica se reduce a una tabla de consulta de 256 entradas indexada por byte de estado.
