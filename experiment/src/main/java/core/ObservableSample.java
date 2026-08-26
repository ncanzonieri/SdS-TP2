package core;

/**
 * Observables primarios registrados en un instante t: la polarizacion `va`
 * (analysis.OrderParameter) y la fraccion del cluster mas grande `s`
 * (analysis.ClusterFinder). Uno por paso de tiempo de la corrida.
 */
public record ObservableSample(int t, double va, double s) {
}
