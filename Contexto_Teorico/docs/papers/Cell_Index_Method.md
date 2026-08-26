# Cell Index Method

*Fuente original: `Cell_Index_Method.pdf`, documento del Proyecto claude.ai "Sistemas de Simulacion".*

## Nota sobre la extracción

La extracción automática de texto de este documento (`project_read`) devolvió contenido vacío, tanto en intentos previos como en un nuevo intento realizado ahora. Esto sugiere que se trata de un PDF escaneado (imagen) sin capa de texto reconocible (OCR), por lo que no es posible generar aquí un resumen fiel de su contenido sin inventar información.

El documento original completo está disponible para consulta manual en el Proyecto de claude.ai **"Sistemas de Simulacion"** (archivo `Cell_Index_Method.pdf` en la lista de documentos del proyecto).

## Contexto de la materia

El **Cell Index Method** (también conocido como método de celdas o de *bins*, o *linked-cell method*) es una técnica clásica de simulación para la detección eficiente de vecinos: en lugar de comparar cada partícula/agente contra todos los demás (complejidad O(N²)), el espacio de simulación se divide en una grilla de celdas de tamaño comparable al radio de interacción, y cada partícula solo necesita examinar las partículas ubicadas en su celda y en las celdas vecinas inmediatas, reduciendo la complejidad típica a O(N).

En el contexto de la materia Sistemas de Simulación, este método fue el eje del **TP1**, y reaparece como herramienta en el **TP2** para el cálculo eficiente de interacciones dentro de un radio de interacción `rc` (por ejemplo, en modelos de partículas activas / flocking donde cada agente interactúa solo con vecinos dentro de esa distancia).
