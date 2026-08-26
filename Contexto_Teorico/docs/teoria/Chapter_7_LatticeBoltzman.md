# Práctica de Simulaciones de Lattice Boltzmann: Flujo Alrededor de un Cilindro

*Fuente original: `Chapter_7_LatticeBoltzman.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

## 1. Contexto general

Este capítulo (Cap. 7 de *Introduction to Practice of Molecular Simulation*, A. Satoh) es un caso de aplicación práctica del método de Lattice Boltzmann (LBM): **flujo uniforme alrededor de un cilindro circular en 2D**. A diferencia de los métodos de simulación molecular clásicos, LBM trabaja con una función de distribución de partículas (abstracción mesoscópica) en lugar de variables macroscópicas directas como velocidad y presión — esto lo hace conceptualmente algo menos intuitivo al principio, pero una vez comprendido resulta muy versátil (aplicable también a suspensiones de partículas y líquidos poliméricos, donde interesan las interacciones hidrodinámicas multicuerpo).

El objetivo del ejercicio es reproducir, para un rango moderado de número de Reynolds, la aparición de un par de vórtices estacionarios detrás del cilindro — un fenómeno muy sensible al modelo de condición de borde usado en la interfaz cilindro-fluido.

## 2. Formulación del problema: modelo D2Q9

Se trata el flujo como bidimensional, usando el modelo de red **D2Q9** (9 direcciones de velocidad discretas, incluyendo la de reposo), numeradas α = 0, 1, …, 8.

### 2.1 Ecuación de Lattice Boltzmann (BGK)

Si f_α(r,t) es la función de distribución de partículas en el sitio r, dirección α, tiempo t, la evolución (colisión + streaming) se escribe:

**f_α(r + c_α·Δt, t + Δt) = f̃_α(r,t)**

**f̃_α(r,t) = f_α(r,t) + (1/τ)·[f_α^(0)(r,t) − f_α(r,t)]**  ... (7.1)

donde τ es el tiempo de relajación (aproximación BGK de un único tiempo de relajación), f_α^(0) es la función de distribución de equilibrio termodinámico, y c_α es la velocidad de red en la dirección α.

### 2.2 Función de distribución de equilibrio

**f_α^(0) = ρ·w_α·[1 + 3(c_α·u)/c² − (3u²)/(2c²) + (9/2)·(c_α·u)²/c⁴]**  ... (7.2)

donde u es la velocidad macroscópica, ρ la densidad, y w_α una constante de peso.

### 2.3 Parámetros del modelo D2Q9

**Pesos:**

w_α = 4/9 para α = 0
w_α = 1/9 para α = 1, 2, 3, 4
w_α = 1/36 para α = 5, 6, 7, 8   ... (7.3)

**Magnitud de la velocidad de red:**

|c_α| = 0 para α = 0
|c_α| = c para α = 1, 2, 3, 4
|c_α| = √2·c para α = 5, 6, 7, 8

donde c = Δx/Δt es la velocidad asociada al desplazamiento de un sitio de red por paso de tiempo, con Δx la distancia mínima entre sitios vecinos.

**Vectores de velocidad discretos (convención del código fuente, dirección x,y):**

C₀=(0,0), C₁=(1,0), C₂=(−1,0), C₃=(0,1), C₄=(0,−1),
C₅=(1,1), C₆=(−1,−1), C₇=(1,−1), C₈=(−1,1)

### 2.4 Densidad y momento macroscópicos

**ρ(r,t) = Σ_{α=0}^{8} f_α(r,t)**

**ρ(r,t)·u(r,t) = Σ_{α=0}^{8} f_α(r,t)·c_α**   ... (7.4)

Descompuesto en componentes (usado en el código de evaluación de velocidad):

**ρ·u_x = c·(f₁ − f₂ + f₅ − f₆ + f₇ − f₈)**   ... (7.15)

**ρ·u_y = c·(f₃ − f₄ + f₅ − f₆ − f₇ + f₈)**   ... (7.16)

## 3. Condiciones de borde

La formalización de condiciones de borde es la parte más delicada del problema: hay que tratar (a) la interfaz cilindro-fluido, (b) el borde de entrada (upstream) y salida (downstream), y (c) los bordes laterales exteriores.

### 3.1 Modelo Yu-Mei-Luo-Shyy (YMLS) para la superficie del cilindro

Se define: r_w = punto sobre la superficie del cilindro, r_p = punto vecino dentro del cilindro, r_l = sitio vecino en el fluido, r_l' = siguiente sitio vecino en el fluido (más alejado del cilindro).

**Interpolación lineal para obtener f en r_l tras el streaming:**

**f₂(r_l, t+Δt) = [Δw/(1+Δw)]·f₂(r_l', t+Δt) + [1/(1+Δw)]·f₂(r_w, t+Δt)**   ... (7.5)

con **Δw = |r_l − r_w| / |r_l − r_p|**.

**Valor en la superficie:**

**f₂(r_w, t+Δt) = (1 − Δw)·f̃₁(r_l', t) + Δw·f̃₁(r_l, t)**   ... (7.6)

El método YMLS lineal usa solo dos puntos de red para la interpolación (útil cuando partículas están casi en contacto, como en suspensiones densas). También se mencionan variantes: la regla histórica de **bounce-back**, el método **YMLS cuadrático** (usa un punto adicional r_l''), y el método de **Bouzidi-Firdaouss-Lallemand (BFL)** — estos últimos con procedimientos ligeramente distintos según Δw ≤ 1/2 o Δw > 1/2 (detallados en el Cap. 8 del libro original, referenciado pero no incluido aquí).

### 3.2 Borde de salida (downstream)

**Condición de extrapolación** (relación lineal entre los últimos tres valores):

**f_α(r_N, t+Δt) = 2·f_α(r_{N−1}, t+Δt) − f_α(r_{N−2}, t+Δt)**   ... (7.7)

**Condición de gradiente cero:**

**f_α(r_N, t+Δt) = f_α(r_{N−1}, t+Δt)**   ... (7.8)

La extrapolación es más precisa pero menos estable (mayor tendencia a divergir); el gradiente cero es más robusto pero menos preciso.

### 3.3 Bordes laterales exteriores

Si la región de simulación es suficientemente grande respecto al diámetro del cilindro, se puede usar condición **periódica** (borde superior = borde inferior). También pueden aplicarse la distribución de equilibrio (flujo uniforme, Ec. 7.2) o bounce-back, aunque estas últimas pueden distorsionar significativamente el campo de flujo si la región es chica. La condición de extrapolación resulta, en general, la más efectiva para minimizar la influencia del borde exterior.

## 4. Coeficiente de arrastre (drag)

**Definición:**

**C_D = F / (ρ·U²·D/2)**   ... (7.9)

donde F es la fuerza por unidad de longitud en la dirección del flujo ejercida por el fluido sobre el cilindro, ρ la densidad, U la velocidad de flujo uniforme, D el diámetro del cilindro.

**Cálculo de la fuerza:** para el sitio de fluido más cercano a la superficie r_l^cyl, con dirección α_l^cyl apuntando hacia el interior del cilindro, el cambio de momento (impulso) por paso de tiempo da:

**F_{α_l^cyl} = { c_{α_l^cyl}·f̃_{α_l^cyl}(r_l^cyl, t)·ΔxΔy + c_{α_l^cyl}·f_{α_l^cyl}(r_l^cyl, t+Δt)·ΔxΔy } / Δt**   ... (7.10)

**Fuerza total (suma sobre todos los sitios y direcciones interactuantes con el cilindro):**

**F = Σ_l Σ_{α_l^cyl} F_{α_l^cyl}**   ... (7.11)

Se usa |F| en la Ec. (7.9).

**Número de Reynolds:**

**Re = D·U / ν**

con la viscosidad cinemática para el modelo D2Q9:

**ν = Δt·c²·(τ − 1/2) / 3**   ... (7.12)

## 5. Clasificación de sitios ("coloring")

Para organizar el código, cada sitio de red se etiqueta con una variable `color`:

- color = 0: sitio ordinario interior.
- color = 1: borde upstream (entrada).
- color = 2: borde downstream (salida).
- color = 3: borde lateral superior.
- color = 4: borde lateral inferior.
- color = 5: sitio interactuando con el cilindro.
- color = 6: sitio interior al cilindro que interactúa con vecinos exteriores.
- color = 7: sitio interior al cilindro sin interacción con el exterior.

Como el cilindro es fijo, esta clasificación se calcula una única vez antes del bucle principal. En problemas con partículas móviles habría que recalcularla en cada paso.

## 6. Geometría de la interpolación en la superficie del cilindro

Dado que r_w está en la superficie del cilindro (radio R_cyl = D/2, centro r_cyl):

**|(1 − Δw)·(r_l − r_p) + r_p − r_cyl| = R_cyl**   ... (7.13)

Esto se reduce a una ecuación cuadrática resuelta explícitamente para Δw:

**Δw = [ (r̂_l² − r̂_p·r̂_l) − √( (r̂_l² − r̂_p·r̂_l)² − (r̂_l − r̂_p)²·(r̂_l² − R_cyl²) ) ] / (r̂_l − r̂_p)²**   ... (7.14)

con r̂_l = r_l − r_cyl y r̂_p = r_p − r_cyl. Este valor de Δw se calcula y guarda para cada par de puntos interactuantes en la superficie.

## 7. Adimensionalización

Tomando Δt, c = Δx/Δt y ρ₀ como escalas de referencia, la ecuación básica queda en forma adimensional (variables con asterisco):

**f*_α(r* + c*_α, t* + 1) = f̃*_α(r*, t*)**

**f̃*_α(r*, t*) = f*_α(r*, t*) + (1/τ)·[f*_α^(0)(r*, t*) − f*_α(r*, t*)]**   ... (7.17)

**f*_α^(0) = w_α·ρ*·[1 + 3·c*_α·u* + (9/2)·(c*_α·u*)² − (3/2)·u*²]**   ... (7.18)

**|c*_α| = 0 (α=0), 1 (α=1,2,3,4), √2 (α=5,6,7,8)**   ... (7.19)

**ρ*(r*,t*) = Σ_α f*_α(r*,t*)  ;  ρ*(r*,t*)·u*(r*,t*) = Σ_α f*_α(r*,t*)·c*_α**   ... (7.20)

La velocidad del sonido adimensional resulta **c*_s = 1/√3**, por lo que las simulaciones deben mantener u* ≪ 1 salvo cuando se admite variación significativa de densidad. La viscosidad cinemática adimensional es:

**ν* = (2τ − 1)/6**

## 8. Condiciones y parámetros típicos de simulación

- Distribución inicial: equilibrio con velocidad uniforme U y densidad ρ₀ (una distribución inicial en reposo puede inducir divergencia).
- Rango de trabajo del capítulo: 1 ≤ Re ≤ 20 (par de vórtices estable aproximadamente entre Re ≈ 7 y Re ≈ 40).
- Re = U*·D* / [(2τ−1)/6]; para Re grande conviene τ cercano a 1/2.
- Valores típicos usados: U* = 0.005–0.01, τ = 0.515–0.8, D* = 3–20.
- Tamaño de la región de simulación: 2h₀* = 4D*–14D*, 2l₀* = 3D*–11D*. A menor tamaño de región, mayor distorsión del campo por el borde exterior.

## 9. Resultados cualitativos reportados

- Con región de simulación pequeña, la condición de flujo uniforme en los bordes exteriores distorsiona y acorta el par de vórtices; la condición de gradiente cero da mejor acuerdo con la solución de Navier-Stokes de referencia (obtenida por diferencias finitas), aunque también muestra distorsión si la región es chica.
- La condición de extrapolación en los bordes exteriores tendió a diverger en las pruebas reportadas.
- Al aumentar el tamaño de la región de simulación, los resultados de LBM convergen hacia la solución de Navier-Stokes de referencia.
- Comparando modelos de borde en la superficie del cilindro (bounce-back, YMLS lineal, BFL lineal) con región suficientemente grande y condición de gradiente cero en los bordes exteriores: los tres dan resultados muy similares y consistentes con la solución exacta, tanto en la formación del par de vórtices como en coeficiente de arrastre y perfil de velocidades. Las variantes cuadráticas de YMLS y BFL, en cambio, mostraron divergencia. El método YMLS lineal se destaca como especialmente conveniente para problemas de suspensiones de partículas, por usar el menor número de puntos de red en la interpolación.

## 10. Estructura del programa de ejemplo (FORTRAN)

El capítulo incluye un programa FORTRAN completo (`LBcyl5.f`) implementando el caso. Estructura funcional (subrutinas principales, ejecutadas en el bucle temporal principal):

1. **VELCAL** — calcula velocidad y densidad macroscópica en cada sitio a partir de f_α (Ecs. 7.4/7.15/7.16), y aplica condiciones de borde en upstream/downstream/laterales.
2. **COLLPROC** — aplica el paso de colisión BGK (Ec. 7.1/7.17), diferenciando el tratamiento según el `color` del sitio (usual, upstream, borde lateral, etc.).
3. **MOVEPROC** — realiza la propagación (streaming) de f_α entre sitios vecinos, incluyendo el tratamiento especial en sitios que interactúan con el cilindro (bounce-back / YMLS / BFL, según el parámetro `ITREECYL`), y acumula la fuerza sobre el cilindro (`CDFORCE`) para el cálculo posterior de C_D.
4. **BCPROC** — aplica las condiciones de borde explícitas post-streaming en upstream, downstream y laterales, según los parámetros `ITREESID` (bordes laterales) e `ITREEDWN` (borde de salida): extrapolación, gradiente cero, o flujo uniforme.
5. **FEQ** (función) — evalúa la distribución de equilibrio f_α^(0) según la Ec. (7.18)/(7.2):

   ```
   FEQ = W(α)·ρ·(1 + 3·(c_α·u) + (9/2)·(c_α·u)² − (3/2)·|u|²)
   ```

6. Subrutinas de inicialización: `INICVEL` (define c_α, w_α, tabla de direcciones opuestas ANTIALPH), `INILAT` (posiciones de red), `INIDIST` (distribución inicial), `INICOLOR`/`MAKETBLE`/`INTERACT` (clasificación de sitios y cálculo de Δw para la interfaz del cilindro, Ec. 7.14).

Los parámetros de control de condición de borde en el código son:
- `ITREECYL`: 1=bounce-back, 2=YMLS cuadrático, 3=YMLS lineal, 4=BFL cuadrático, 5=BFL lineal.
- `ITREESID`: 1=extrapolación, 2=gradiente cero (DEF=0), 3–5=flujo uniforme (variantes).
- `ITREEDWN`: mismas opciones que ITREESID pero para el borde downstream.

Ejemplo de correspondencia τ–Re usada en el código (U*=0.005, D*=20): τ=0.80→Re=1; τ=0.60→Re=3; τ=0.55→Re=6; τ=0.53→Re=10; τ=0.52→Re=15; τ=0.515→Re=20; τ=0.51→Re=30.

## 11. Conceptos clave para retener

- El modelo D2Q9 y la ecuación de colisión BGK (Ec. 7.1) son la base de cualquier implementación práctica de LBM en 2D.
- El tratamiento de la condición de borde en superficies curvas (no alineadas con la red) requiere interpolación (YMLS, BFL) — el bounce-back simple es la opción más económica pero menos precisa geométricamente.
- El tamaño finito del dominio de simulación tiene un impacto significativo sobre la validez del resultado cuando se compara con soluciones de referencia (Navier-Stokes); esto es un punto crítico a validar en cualquier TP que reproduzca este tipo de simulación.
- La relación entre τ, Re, y la viscosidad cinemática (Ec. 7.12) es la que permite mapear parámetros de simulación (adimensionales, en unidades de red) a un número de Reynolds físico objetivo.
