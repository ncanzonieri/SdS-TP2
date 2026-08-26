# Cellular Automata as Models of Complexity

*Fuente original: `CellularAutomataModelsComplexityStephenWolframArticle.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion". Nota: resumen/apuntes parafraseados, no transcripción literal completa (por derechos de autor); para el texto íntegro consultar el original en el Proyecto.*

Stephen Wolfram, *Nature* Vol. 311, 4 de octubre de 1984, pp. 419–424 (sección "Articles").

## Advertencia sobre la extracción

**El contenido disponible es muy limitado.** La extracción vía `project_read` sobre este PDF solo devolvió el tramo final del artículo (aprox. la última columna de la página 424): el cierre de la discusión sobre indecidibilidad/intratabilidad computacional, los agradecimientos del autor y la lista de 24 referencias bibliográficas. **No se recuperó el cuerpo principal** del artículo (introducción, la clasificación de Wolfram de los autómatas celulares en cuatro clases de comportamiento —homogéneo, periódico, caótico y complejo—, las figuras, ni las ecuaciones de entropía/dimensión que se discuten en el resto del texto). Lo que sigue son apuntes parafraseados de ese fragmento final únicamente; no se debe asumir que cubre el artículo completo, y no se inventó contenido adicional para compensar el faltante.

## Apuntes del fragmento recuperado

El pasaje retomado corresponde a la discusión final del artículo sobre los límites de predictibilidad de los autómatas celulares de clase 3 (caóticos) y clase 4 (complejos), en el marco de la clasificación de comportamientos que Wolfram desarrolla en trabajos previos (citados como refs. 1–4).

- **Indecidibilidad del comportamiento a tiempo infinito.** Para los autómatas de clase 4, y en gran medida también para los de clase 3, no habría un procedimiento general para predecir si una secuencia de valores de sitio dada va a aparecer alguna vez en la evolución del sistema, salvo simulando explícitamente. Es decir, la pregunta "¿aparece este patrón en el límite de tiempo infinito?" sería en general indecidible.
- **No computabilidad del límite de entropía.** Como consecuencia de lo anterior, el valor límite (a tiempo infinito) de la entropía en autómatas de clase 3 y 4 no podría calcularse en general con un procedimiento finito a precisión arbitraria — sólo se podrían dar cotas. Esto se cumpliría si los "conjuntos límite" de estos autómatas forman lenguajes al menos sensibles al contexto (context-sensitive), en la jerarquía de Chomsky.
- **Intratabilidad computacional a tiempo finito.** A diferencia del caso de tiempo infinito, para un tiempo finito *t* sí es posible en principio decidir si una secuencia de longitud *n* puede aparecer, considerando todas las secuencias iniciales de longitud n₀ = n + 2rt que podrían evolucionar hacia ella (donde *r* es el radio de vecindad de la regla). Pero el costo computacional de ese procedimiento crece exponencialmente con *n* o *t*, por lo que se vuelve rápidamente intratable en la práctica.
- **Conjetura de NP-completitud.** Wolfram conjetura que identificar las secuencias posibles generadas por autómatas de clase 3 y 4 es, en general, un problema NP-completo (remite a Hopcroft & Ullman sobre teoría de la computación). Si eso es así, no existiría un algoritmo que resuelva el problema en tiempo polinomial en *n* o *t*: en la práctica, la única vía es la simulación explícita de todas las posibilidades.
- **Lectura más amplia (especulación del autor).** Wolfram extiende la observación a sistemas naturales en general: la indecidibilidad y la intratabilidad, comunes en matemática y computación, podrían afectar a "casi todos" los autómatas celulares no triviales, y quizás sean generalizadas en sistemas naturales cada vez que hay no linealidad presente. La consecuencia es fuerte: para muchos sistemas naturales no habría fórmulas cerradas que describan su comportamiento — sólo se podrían conocer sus consecuencias mediante simulación directa u observación. Esta idea es, en cierto sentido, el argumento central que conecta el artículo con la motivación general de usar autómatas celulares (y por extensión, la simulación) como herramienta de modelado de sistemas complejos.

## Contexto (agradecimientos)

El autor agradece discusiones con O. Martin, J. Milnor, N. Packard y otros, y menciona el uso del sistema de cómputo simbólico SMP. El trabajo fue financiado en parte por la US Office of Naval Research (contrato N00014-80-C-0657).

## Referencias citadas en el fragmento

Lista bibliográfica completa tal como aparece en el artículo (es información de cita, no texto protegido por derecho de autor en su expresión):

1. Wolfram, S. *Rev. Mod. Phys.* **55**, 601–644 (1983).
2. Wolfram, S. *Physica* **100**, 1–35 (1984).
3. Wolfram, S. *Commun. Math. Phys.* (in the press).
4. Wolfram, S. *Cellular Automata* (Los Alamos Science, Autumn, 1983).
5. Mandelbrot, B. *The Fractal Geometry of Nature* (Freeman, San Francisco, 1982).
6. Packard, N. Preprint, *Cellular Automaton Models for Dendritic Growth* (Institute for Advanced Study, 1984).
7. Madore, B. & Freedman, W. *Science* **222**, 615–616 (1983).
8. Greenberg, J. M., Hassard, B. D. & Hastings, S. P. *Bull. Amer. Math. Soc.* **84**, 1296–1327 (1978).
9. Vichniac, G. *Physica* **100**, 96–116 (1984).
10. Domany, E. & Kinzel, W. *Phys. Rev. Lett.* **53**, 311–314 (1984).
11. Waddington, C. H. & Cowe, R. J. *J. theor. Biol.* **25**, 219–225 (1969).
12. Lindsay, D. T. *Veliger* **24**, 297–299 (1977).
13. Young, D. A. *A Local Activator-Inhibitor Model of Vertebrate Skin Patterns* (Lawrence Livermore National Laboratory Rep., 1983).
14. Guckenheimer, J. & Holmes, P. *Nonlinear Oscillations, Dynamical Systems, and Bifurcations of Vector Fields* (Springer, Berlin, 1983).
15. Hopcroft, J. E. & Ullman, J. D. *Introduction to Automata Theory, Languages, and Computation* (Addison-Wesley, New York, 1979).
16. Packard, N. Preprint, *Complexity of Growing Patterns in Cellular Automata* (Institute for Advanced Study, 1983).
17. Martin, O., Odlyzko, A. & Wolfram, S. *Commun. Math. Phys.* **93**, 219–258 (1984).
18. Grassberger, P. *Physica* **100**, 52–58 (1984).
19. Lind, D. *Physica* **100**, 36–44 (1984).
20. Margolus, N. *Physica* **100**, 81–95 (1984).
21. Smith, A. R. *Journal of the Association for Computing Machinery* **18**, 339–353 (1971).
22. Berlekamp, E. R., Conway, J. H. & Guy, R. K. *Winning Ways for your Mathematical Plays* Vol. 2, Ch. 25 (Academic, New York, 1982).
23. Gardner, M. *Wheels, Life and other Mathematical Amusements* (Freeman, San Francisco, 1983).
24. Wolfram, S. *SMP Reference Manual* (Computer Mathematics Group, Inference Corporation, Los Angeles, 1983).

## Recomendación

Para el TP que use este artículo como referencia sobre clasificación de autómatas celulares (clases 1–4 de Wolfram), conviene consultar directamente el PDF original en el Proyecto (o los trabajos previos de Wolfram citados como refs. 1–4, en particular *Rev. Mod. Phys.* 55, 601 (1983), que es donde se presenta la clasificación completa), ya que este apunte solo cubre la sección final sobre indecidibilidad/intratabilidad.
