# Reglamento SdS 2026 C2

*Fuente original: `Reglamento_SdS_2026_Q2.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion".*

ITBA – Dto. Sistemas Digitales y Datos. Carrera Ing. Informática
Simulación de Sistemas (72.25). Año: 2026 – Segundo Cuatrimestre

- Dr. Daniel R. Parisi (dparisi@itba.edu.ar)
- Dr. Ariel Salgado
- Dr. Lucas E. Wiebke
- Dr. Rafael F. Martín
- Lic. Franco Eskinazi

## 1. Normas Generales

- Las clases se alternarán entre presenciales y virtuales según se establece en el cronograma (en CAMPUS/Contenido del curso/Bienvenida/SdS_Cronograma_2026C2.pdf).
- Resumen de la propuesta del Curso: el curso será teórico-práctico, durante el cual se brindarán herramientas para implementar simulaciones de sistemas en general y físicos en particular. Estas simulaciones permiten estudiar sistemas complejos formados por muchas partículas inertes o autopropulsadas, brindando posibilidades para entender, modelar y optimizar el funcionamiento de dichos sistemas. Por otro lado, las técnicas presentadas permiten generar animaciones con potenciales aplicaciones a las industrias del cine y en el desarrollo de videojuegos.
- Las comunicaciones oficiales de la cátedra serán a través del sitio en Internet CAMPUS - ITBA. Su lectura se considera obligatoria, no pudiéndose aducir su desconocimiento. Opcionalmente, en caso de urgencia, y a criterio de los docentes, se enviará un correo electrónico a la dirección oficial de cada alumno/a: nombre@alu.itba.edu.ar.
- Las comunicaciones o consultas vía mail que envíen las/los alumnas/os a la Cátedra deben tener en copia a todos los miembros del grupo, y en el tema del mail debe figurar el código de identificación del grupo `2026Q2GXX`, donde XX es el número de grupo.
- La resolución de cualquier situación no contemplada en el presente reglamento quedará a criterio del responsable de la Cátedra.

## 2. Modalidad de las Clases

- Se dictarán 2 clases semanales, distribuidas entre teóricas y trabajos prácticos (T.P.) según se establece en el cronograma (en CAMPUS/Contenido del curso/00_Cronograma_y_Reglamento).
- En las clases teóricas se explicarán los conceptos básicos, los cuales deberán ser complementados y profundizados con la bibliografía.
- Las clases prácticas se realizarán en el aula/laboratorio o virtualmente, y el objetivo será implementar computacionalmente los sistemas y modelos introducidos en las teóricas. Para ello se deberá escribir nuevo código. El lenguaje de programación será elección de los/as alumnos/as. La modalidad de los trabajos prácticos será individual o grupal. Los T.P. finalizados deberán ser expuestos frente a la clase mediante una presentación oral asistida por Keynote, Powerpoint o similar en las fechas estipuladas en el cronograma como "Presentación de T.P.". El formato de esta presentación debe seguir los lineamientos detallados en el documento `GuiaPresentaciones.pdf` (en …/Contenido del curso/Bienvenida/Guías de Formato).
- Los T.P. se aprueban con nota mayor o igual a **4 (cuatro)**. Las presentaciones de T.P. serán de asistencia obligatoria. La falta de puntualidad (o retirarse anticipadamente) tendrá penalizaciones en reducción de puntaje de la calificación del T.P. correspondiente, a razón de **0.5 puntos por cada miembro del grupo y por cada media hora**, más allá de **10 minutos de tolerancia** al inicio. La ausencia sin justificación de alguno de los miembros del grupo a las presentaciones de los T.P. producirá que el mismo sea desaprobado. Las causas válidas para justificar una inasistencia son: salud, viajes de estudio, feriados religiosos que figuren en el calendario oficial y mudanza. La validez de otras causas para justificar una inasistencia, no contempladas en el presente reglamento, quedarán a criterio de la Cátedra.

## 3. Condiciones de Aprobación de la Materia

- Para aprobar la materia será necesario aprobar todos los T.P. Si la nota de la cursada es mayor o igual a **7 (siete)**, la materia se podrá promocionar con la misma nota. Además, es condición necesaria para promocionar no desaprobar ningún T.P. En caso de nota de cursada menor a 7 (siete) o que se haya recuperado algún T.P. se deberá rendir una Evaluación Final. Grupos con notas entre 7 (siete) y 9 (nueve), ambos inclusive, podrán optar por rendir Evaluación Final si desean subir la nota.
- Se podrá recuperar un único T.P. En caso de no aprobar dos T.P. (o uno y su recuperatorio) se perderá la condición de alumno regular.
  - El T.P. a recuperar se presentará en la fecha indicada en el cronograma de la materia. En caso de aprobarse el recuperatorio, la nota correspondiente será el promedio entre la nota del T.P. desaprobado y la de su recuperatorio. En caso de que este promedio sea menor a cuatro, la nota pasará a ser cuatro.
  - En el caso de que se recupere un T.P. por no haberse presentado en la fecha original, la máxima nota de ese T.P. será **8 (ocho)**.
- Cada T.P. consiste en:
  1. Implementar código propio correspondiente al sistema que se simule.
  2. Realizar simulaciones y analizar los resultados.
  3. Realizar la correspondiente presentación oral (tipo Keynote, Powerpoint o similar); estas presentaciones deberán contener animaciones del sistema simulado embebidas, solamente, en la presentación en vivo.

### Entregables de los T.P. (como respuesta a las actividades en CAMPUS)

a) Última versión del código de simulación implementado en un archivo `*.zip` (<< 1 MB). NO incluir con el código: NI resultados o outputs de las simulaciones, NI otros documentos como enunciados de problemas, etc., NI repositorios enteros con todas las versiones, NI animaciones, NI scripts para analizar los datos, NI nada que no sean solo las líneas de código creadas para realizar las simulaciones.

b) Presentación exportada en formato `*.pdf` (de forma tal que se puedan realizar búsquedas dentro del texto que contienen, es decir, formato texto y no formato imagen u otro). La presentación en formato pdf deberá tener, en las diapositivas donde se muestran las animaciones, solo una imagen de un fotograma representativo, y en ningún caso se deben incluir animaciones embebidas en el archivo `*.pdf` que se entrega.

c) Informe, en caso de ser requerido.

- Las entregas de actividades a través de campus cuentan con un sistema automático para identificar plagio entre documentos de la institución y de internet en general. En caso de detectarse plagio, tanto en el código como en las figuras, presentaciones y/o informes, el T.P. (o T.P. Final) correspondiente será desaprobado con calificación **"0" (cero)**.
- En caso de rendir una Evaluación Final, el formato de la misma será, por defecto, la entrega y presentación de un T.P. Final. Alternativamente, y a criterio de la Cátedra, la Evaluación Final podrá ser un examen (oral o escrito).

### T.P. Final

- El T.P. Final consistirá en la entrega de un informe que debe seguir el formato indicado en `GuiaInformes.pdf`, el código fuente implementado, una presentación oral asistida por diapositivas (estilo Keynote, Powerpoint o similar), y el archivo de la presentación oral en formato `*.pdf`. Tanto este archivo como el informe deben contener links explícitos de animaciones del sistema simulado. La duración de la presentación oral debe ser de **20 minutos**, a lo que se adicionará el tiempo de las preguntas.
- El tema de este trabajo final podrá ser la profundización y/o extensión de alguno de los temas vistos durante la cursada, u otro propuesto por las/los alumnas/os.
- El tema y los alcances del T.P. final deben ser:
  1. Primero presentados por los alumnos al Profesor;
  2. quien hará correcciones y sugerencias;
  3. para, finalmente, enviar por mail la propuesta final a dparisi@itba.edu.ar;
  4. la cual debe ser aprobada.
- El plazo para la definición del tema del T.P. final y las consultas sobre el mismo se limitan a lo establecido en el cronograma de la materia. En todos los casos, el tema y los alcances del T.P. deben estar definidos y aprobados por la Cátedra **al menos dos semanas antes** de la fecha de final.
- Una vez acordado y definido un tema para T.P. final, el mismo no podrá ser cambiado.
- Dado que los T.P. finales se presentan oralmente por grupos o individualmente, cada uno deberá fijar previamente un horario para realizar la presentación dentro de la fecha de final correspondiente. Es decir, que no deben presentarse todos los alumnos que rindan final en el horario publicado de comienzo del mismo.
- Todos los integrantes del grupo deben estar en condiciones de rendir el T.P. final, en lo concerniente a materias correlativas. Si alguno de los alumnos perteneciente a un grupo rinde en una fecha distinta a la del resto del grupo, queda a criterio de la Cátedra la forma de evaluación, pudiendo ser la misma la realización de otro T.P. final (con igual o diferente tema) o un examen final escrito.
- El T.P. final podrá ser hecho y presentado en forma grupal (con el mismo grupo de la cursada) o en forma individual.
- El objetivo del T.P. final es integrar los conocimientos y herramientas brindadas durante toda la cursada. Por ello, las preguntas que se realicen durante la presentación de dicho T.P. podrán ser sobre el tema elegido y también sobre cualquier otro tema visto en clase.

### Composición de la nota de cada T.P.

| Componente | Porcentaje |
|---|---|
| Simulaciones | 30 % |
| Resultados de los puntos pedidos en el enunciado | 30 % |
| Correcta estructura de la presentación (identificar adecuadamente qué conceptos corresponden a cada sección, según la guía de presentaciones) | 30 % |
| Formato de la presentación | 10 % |

### Nota de la cursada y de la materia

- La nota de la cursada (**NC**) será el promedio entre: todos los T.P. de la cursada y una nota de concepto de cada alumno.
- En caso de rendir T.P. final, su nota será **NTPF**.
- En el caso en que se promocione la materia, la nota del final será igual a la de la cursada: **NTPF = NC**.
- Finalmente, la calificación de la materia (**Nm**) será el promedio entre NC y la del T.P. final: **Nm = (NC + NTF) / 2**.

## 4. Contenidos

1. **Sistemas y Modelos**: Teoría General de Sistemas. Sistemas en tiempo continuo. Sistemas en tiempo discreto. Sistemas de eventos discretos. Estado de un sistema. Modelos discretos y continuos. Modelos determinísticos y probabilísticos. Propósito de la simulación.
2. **Sistemas Físicos**: Introducción a los sistemas de muchas partículas. Definición de materia activa. Ejemplos. Métodos y Enfoques de Simulación.
3. **Autómatas Celulares**. Sobre grilla fija: Fluidos - Lattice Boltzmann. Sin grilla espacial: Bandadas de Vicsek.
4. **Simulaciones de partículas dirigidas por eventos (Event Driven)**. Gas ideal. Tablero de Galton.
5. **Simulaciones de partículas dirigidas por el paso temporal (Time-Step Driven)**. Dinámica Molecular. Métodos Numéricos de Integración: Euler, Verlet, Corrector Predictor. Gas de Lennard-Jones. Sistemas gravitatorios.
6. **Medios Granulares Densos Gravitatorios 2D**. Partículas cilíndricas. Partículas de formas arbitrarias: Esferopolígonos.
7. **Simulación de Multitudes**. Social Force Model. Contractile Particle Model. Modelado del comportamiento de humanos y animales. Egreso de agentes biológicos a través de una puerta angosta. Navegación de peatones virtuales.

## 5. Bibliografía

- Cassandras, C., Lafortune, S., "Introduction to Discrete Event Systems", Springer, 1999.
- Allen, Mike P., and Dominic J. Tildesley, eds. "Computer simulation of liquids". Oxford university press, 1989.
- Sukop, Michael C., and Daniel T. Thorne. "Lattice Boltzmann modeling: an introduction for geoscientists and engineers". Springer, 2007.
- Dietrich E. Wolf, "Modeling and Computer Simulation of Granular Media". In: *Computational Physics: Selected Methods - Simple Exercises - Serious Applications*, Karl H. Hoffmann (Editor), Michael Schreiber (Editor). Springer (1996).
- Vicsek, Tamás, et al. "Novel type of phase transition in a system of self-driven particles." *Physical Review Letters* 75.6 (1995): 1226.
- Helbing, Dirk, Illés Farkas, and Tamas Vicsek. "Simulating dynamical features of escape panic." *Nature* 407.6803 (2000): 487-490.
- J. Banks, J. S. Carson, B. Nelson & D. Nicol. *Discrete-Event System Simulation*, 3rd ed. Prentice-Hall, 2000.
</content>
