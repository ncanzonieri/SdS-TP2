# Sistemas de Simulación — Contexto para Claude Code (réplica del Proyecto claude.ai)

Este archivo es el punto de entrada de contexto para Claude Code en este repositorio. Es una réplica local del Proyecto de claude.ai **"Sistemas de Simulación"** (materia Simulación de Sistemas, ITBA), armada porque hoy no existe una forma de sincronizar directamente un Proyecto de claude.ai con Claude Code. Contiene el texto de todos los documentos que estaban cargados en ese Proyecto, organizado en `docs/`, más el trabajo del grupo para el TP2.

## Sobre este Proyecto

- **Descripción original del Proyecto:** "Ayudanyte para la elaboración de los trabajos prácticos de la materia Simulación de Sistemas."
- **Instrucciones originales del Proyecto:** "A partir de la teoría cargada en contenido del proyecto, desarrollar los trabajos prácticos del mismo."
- **Grupo:** Grupo 9 — Canzonieri, Nicolás (63501); Díaz Varela, Lola; Viera, Federico.
- **TP activo:** TP2 — Autómatas Celulares (bandadas de agentes autopropulsados, off-lattice: modelo de Vicsek y modelo de votante). Entrega **04/09/2026 13hs**.

Cuando trabajes conmigo (Claude Code) en este repo para el TP2, priorizá siempre lo que dice `docs/tp/TP2_Enunciado.md` (enunciado + parámetros del grupo) y las ecuaciones exactas en `docs/teoria/Teorica_2.md`, `docs/papers/NovelTypePhaseTransition2_Vicsek1995.md` y `docs/papers/PhysRevE104_034111_Loscar2021_VoterModel.md`.

## Estructura del repositorio

```
SdS-TP2/
├── CLAUDE.md                    ← este archivo
├── README.md                    ← notas originales del grupo (parámetros del TP2)
├── docs/                        ← réplica del contenido del Proyecto claude.ai
│   ├── tp/                      ← enunciados de los TPs
│   ├── catedra/                 ← cronograma, reglamento, guías de formato
│   ├── teoria/                  ← clases teóricas y apuntes de la materia
│   └── papers/                  ← papers de referencia citados en los TPs
└── experiment/                  ← código fuente (Java/Maven) del motor de simulación
    ├── pom.xml
    └── src/main/java/
        ├── Main.java
        ├── models/Grid.java
        ├── models/Particle.java
        └── utils/CsvWriter.java
```

**Importante:** `experiment/` ya es un proyecto Maven/Java existente y con historial de git — no hay que reescribirlo desde cero, sino extender lo que ya está armado (`Grid`, `Particle`, `CsvWriter`, `Main`).

## Índice de `docs/`

### `docs/tp/` — Enunciados de los trabajos prácticos
- `TP2_Enunciado.md` — **el enunciado activo.** Incluye el enunciado oficial completo (entregables a-d, fecha de entrega, ejercicio off-lattice con los puntos a-g, modelo de votante, referencias) fusionado con los parámetros exactos que el grupo ya definió en su `README.md` (L=10, densidades ρ=2/4/8 → N=200/400/800, v=0.03, rc=1, ecuaciones de actualización, fórmula de va, definición de cluster/S).
- `TP1_Enunciado.md` — enunciado del TP1 (Cell Index Method), relevante para el punto (g) del TP2 que pide comparar tiempos de ejecución del CIM entre ambos TPs.

### `docs/catedra/` — Documentos administrativos y guías de formato
- `Cronograma.md` — cronograma completo de clases 2026 Q2. Fechas clave del TP2: clases 21/ago, 24/ago, 28/ago, 31/ago, y **presentación + entrega de informe el 04/09/2026**.
- `Reglamento.md` — reglamento de cursada: condiciones de aprobación, composición de la nota (Simulaciones 30% / Resultados 30% / Estructura presentación 30% / Formato 10%), reglas de entrega, política de plagio.
- `GuiaInformes.md` — formato exigido para el informe escrito (secciones, numeración de figuras/ecuaciones, convenciones de notación: escalares en itálica, vectores en negrita, formato de referencias).
- `GuiaPresentaciones.md` — formato exigido para la presentación oral (estructura de secciones 2.1–2.6, reglas de tiempo, formato de gráficos y notación científica, animaciones al inicio de cada estudio).

### `docs/teoria/` — Clases teóricas y apuntes
- `Teorica_2.md` — **la más relevante para el TP2.** Autómatas celulares 1D/2D, Juego de la Vida, modelo FHP de gas reticular, y la sección de bandadas off-lattice de Vicsek con las ecuaciones exactas de actualización de posición, ángulo (con `atan2`) y polarización `va`.
- `Teorica_1.md` — sistemas de muchas partículas, materia activa, y el Cell Index Method (CIM) usado en TP1 y TP2.
- `Teorica_0.md` — sistemas y modelos, espacio de estados, Monte Carlo, estadística de simulación.
- `SdS_Apuntes_parte1.md` — apuntes Unidades 1-4 (sistemas y modelos, muchas partículas, autómatas celulares, simulación por eventos).
- `SdS_Apuntes_parte2.md` — apuntes Unidades 5-7 (integradores, medios granulares, simulación de multitudes).
- `02_Lattice_Gas_Models.md`, `Chapter_7_LatticeBoltzman.md`, `00_Book_LatticeBoltzmannModeling.md`, `lattice_gas_cellular_automata_and_lattice_boltzmann_models.md` — material de gas reticular / Lattice Boltzmann (menos relevante para TP2, más para lattice gas en general; queda como contexto adicional de la cursada).

### `docs/papers/` — Papers de referencia
- `NovelTypePhaseTransition2_Vicsek1995.md` — **[1] Vicsek et al. 1995**, el paper que define el modelo estándar del TP2. Ecuaciones del modelo y transición de fase.
- `PhysRevE104_034111_Loscar2021_VoterModel.md` — **[2] Loscar, Baglietto & Vázquez 2021**, el paper que define el modelo de votante del TP2. Ecuaciones y leyes de escala.
- `FlockingDynamics_VoterlikeInteractions_Baglietto_Vazquez.md` — paper previo de Baglietto & Vázquez sobre el modelo FVM (consenso tipo votante sin ruido).
- `Flocks_Herds_Reynolds1987.md` — Reynolds 1987, modelo clásico de "boids" (separación/alineación/cohesión).
- `M3AS_CollectiveAnimalBehavior_Cavagna2010.md` — Cavagna et al., análisis empírico de bandadas de estorninos (interacción topológica vs. métrica).
- `PhysicsToday_StarlingFlocks_2007.md` — nota de divulgación sobre el proyecto StarFlag.
- `marchetti_hydrodynamics_soft_active_matter.md` — review de materia activa (Toner-Tu, conexión con Vicsek).
- `ActiveManyParticleSystems_Helbing.md` — review de Helbing sobre sistemas activos (tráfico/peatones).
- `CellularAutomataModels_Wolfram1984.md` — Wolfram sobre autómatas celulares (extracción parcial, ver nota en el archivo).
- `AdviceToBeginningPhysicsSpeakers.md` — consejos de Garland para presentaciones orales de física.
- `Cell_Index_Method.md` — **nota:** el PDF original no pudo extraerse (probablemente escaneado); el original está en el Proyecto de claude.ai.
- `download_doc_note.md` — **nota:** documento del Proyecto que no pudo extraerse (contenido corrupto/ilegible); el original está en el Proyecto de claude.ai.

**Nota sobre derechos de autor:** los papers y capítulos de libro en `docs/papers/` y varios de `docs/teoria/` son **apuntes y resúmenes parafraseados**, no transcripciones literales completas — cada archivo lo aclara en su encabezado. Las ecuaciones y fórmulas centrales sí se transcriben tal cual, porque son las que hacen falta para programar los modelos. Para el texto íntegro de cualquier paper, el PDF original sigue disponible en el Proyecto "Sistemas de Simulacion" de claude.ai.

## Cómo ayudarme con el TP2

1. Los parámetros del grupo (`README.md` y `docs/tp/TP2_Enunciado.md`) ya están fijados — no los reinventes: L=10, ρ=2/4/8, v=0.03, rc=1, η∈[0,2π).
2. El motor de simulación va en `experiment/` (Java/Maven). El output de la simulación debe ser un archivo de texto plano, separado del módulo de animación (que se corre después, independiente).
3. Hay que implementar y comparar **dos modelos de actualización de ángulo**: Vicsek (promedio de vecinos, `docs/teoria/Teorica_2.md` / `docs/papers/NovelTypePhaseTransition2_Vicsek1995.md`) y Votante (copia aleatoria de un vecino, `docs/papers/PhysRevE104_034111_Loscar2021_VoterModel.md`).
4. Los entregables finales son: presentación oral 13 min + PDF de la presentación + código fuente en zip + informe escrito — formato exacto en `docs/catedra/GuiaPresentaciones.md` y `docs/catedra/GuiaInformes.md`.
5. Reusar el Cell Index Method del TP1 (`docs/tp/TP1_Enunciado.md`, `docs/teoria/Teorica_1.md`) para la detección de vecinos dentro de rc — el punto (g) del TP2 pide comparar tiempos de ejecución con el TP1.
