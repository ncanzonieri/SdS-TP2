# SdS-TP2
## Autómatas Celulares
#### Grupo 9:
Canzonieri, Nicolás 63501

Díaz Varela, Lola  62792

Viera, Federico


Off-Lattice. 
Lado de tablero L=10. Condición de contorno periódico. Densidades d= 1/3pi, 1/2pi, 1/pi, 2, 4 y 8 (o sea, N = 11, 16, 32, 200, 400 y 800). v = 0.03. rc=1. 0<=eta<2pi (en principio, cortar cuando se estabiliza en 0).

Cada partícula es puntual y sin colisión. Se representa como un vector y se colorea según ángulo.

Xi(t+1)=Xi(t)+Vi(t) (Dt=1UT)

Ai(t+1)=<Ai(t)>r + R  (Viscek)

Ai(t+1)=randomFromNeighbours(i,r) + R  (Votante)

R es el ruido que es U[-eta/2,eta/2]

<Ai(t)>r es ángulo promedio de las partículas que rodean a i (inclusive) en un radio de r. 

El promedio de ángulos se calcula con arctg(<sen(Ai(t))>r/<cos(Ai(t))>r). Tener en cuenta los cuadrantes correctos (función atan2).

La polarización (va) se calcula con: va= ||Sum(Vi)||/Nv. (Módulo de la sumatoria de los vectores velocidad dividido por rapidez y cantidad de partículas)

Clústers son conjuntos de partículas conectadas por saltos de vecinos. S es la fracción de nodos del mayor clúster sobre el total de partículas.

Se desea evaluar va y S en función de eta para cada densidad. El va de cada experimento se considera aquel en el cual se estanca.
