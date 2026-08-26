package core;

import analysis.ClusterFinder;
import analysis.OrderParameter;
import models.Grid;
import models.Particle;
import models.SimulationParams;
import models.SimulationParams.Model;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * Loop temporal de la simulacion de bandadas (Vicsek/Votante). Cada llamada a
 * step() hace evolucionar sincronicamente todas las particulas un paso de
 * tiempo (dt=1, ver SimulationParams):
 *
 *   1. Busca vecinos dentro de rc via el CIM de Grid.
 *   2. Registra los observables primarios del estado actual (t): polarizacion
 *      `va` (analysis.OrderParameter) y fraccion del cluster mas grande `S`
 *      (analysis.ClusterFinder), reusando los mismos vecinos del CIM.
 *   3. Calcula el nuevo angulo de cada particula segun el modelo elegido
 *      (Vicsek: promedio circular de si misma + vecinos; Votante: copia el
 *      angulo de un vecino al azar, incluyendose a si misma), sumando ruido
 *      R ~ U(-eta/2, eta/2).
 *   4. Actualiza la posicion con modulo v constante y wrap-around periodico.
 *
 * El paso 3 se calcula en un buffer (todas las particulas leen el angulo
 * "congelado" del tick anterior antes de que nadie se mueva) para que la
 * actualizacion sea realmente sincronica y no dependa del orden de iteracion.
 */
public class SimulationEngine {

    private final Grid grid;
    private final SimulationParams params;
    private final Random random;
    private final List<ObservableSample> observables = new ArrayList<>();
    private int t = 0;

    public SimulationEngine(Grid grid, SimulationParams params) {
        this.grid = grid;
        this.params = params;
        this.random = grid.getRandom();
    }

    public Grid getGrid() {
        return grid;
    }

    /**
     * Serie temporal (t, va, S) acumulada hasta ahora - un elemento por cada
     * estado registrado (uno por step(), mas el estado final de run()). La
     * persistencia a disco (Paso 4) va a leer esta lista.
     */
    public List<ObservableSample> getObservables() {
        return observables;
    }

    /**
     * Corre `steps` pasos de tiempo y ademas registra el estado final (t ==
     * steps), que step() por si solo no llega a capturar (siempre registra el
     * estado ANTES de moverse - ver step()).
     */
    public void run(int steps) {
        for (int i = 0; i < steps; i++) {
            step();
        }
        sampleObservables();
    }

    /** Ejecuta un unico paso de tiempo (dt=1) sobre todas las particulas. */
    public void step() {
        List<Particle> particles = grid.getParticles();
        Map<Particle, List<Particle>> neighbors = grid.nearestNeighbor();

        // Los observables del instante t se calculan ANTES de mover a nadie,
        // reusando estos mismos vecinos (evita buscar vecinos dos veces por tick).
        recordObservables(particles, neighbors);

        // Buffer: theta_i(t+1) de cada particula, calculado a partir del estado
        // congelado del tick anterior (nadie lee un angulo ya actualizado).
        double[] newAngles = new double[particles.size()];
        for (int idx = 0; idx < particles.size(); idx++) {
            Particle particle = particles.get(idx);
            List<Particle> ns = neighbors.getOrDefault(particle, List.of());
            double theta = params.getModel() == Model.VICSEK
                    ? vicsekAngle(particle, ns)
                    : voterAngle(particle, ns);
            newAngles[idx] = theta + noise();
        }

        // Recien aca se mutan las particulas: nueva posicion (con wrap-around
        // periodico) y nuevo angulo, todo a partir del buffer ya calculado.
        double v = params.getV();
        int L = params.getL();
        for (int idx = 0; idx < particles.size(); idx++) {
            Particle particle = particles.get(idx);
            double theta = newAngles[idx];
            particle.setX(wrap(particle.getX() + v * Math.cos(theta), L));
            particle.setY(wrap(particle.getY() + v * Math.sin(theta), L));
            particle.setAngle(theta);
        }

        t++;
    }

    /**
     * Registra (t, va, S) del estado actual sin avanzar el tiempo ni mover a
     * nadie. Util para capturar el estado final tras run() (que step() no
     * llega a registrar, ya que siempre registra el estado ANTES de moverse).
     */
    public void sampleObservables() {
        recordObservables(grid.getParticles(), grid.nearestNeighbor());
    }

    private void recordObservables(List<Particle> particles, Map<Particle, List<Particle>> neighbors) {
        double va = OrderParameter.polarization(particles);
        double s = ClusterFinder.largestClusterFraction(neighbors, particles);
        observables.add(new ObservableSample(t, va, s));
    }

    /**
     * Modelo estandar de Vicsek: arctan2 del promedio de senos/cosenos de la
     * propia particula y sus vecinos dentro de rc (Ecuacion 2 del enunciado).
     */
    private double vicsekAngle(Particle particle, List<Particle> neighbors) {
        double sumSin = Math.sin(particle.getAngle());
        double sumCos = Math.cos(particle.getAngle());
        for (Particle p : neighbors) {
            sumSin += Math.sin(p.getAngle());
            sumCos += Math.cos(p.getAngle());
        }
        return Math.atan2(sumSin, sumCos);
    }

    /**
     * Modelo de votante: en vez de promediar, copia el angulo de una unica
     * particula elegida al azar entre {si misma} U vecinos.
     */
    private double voterAngle(Particle particle, List<Particle> neighbors) {
        int pick = random.nextInt(neighbors.size() + 1);
        return pick == neighbors.size() ? particle.getAngle() : neighbors.get(pick).getAngle();
    }

    /** Ruido uniforme R ~ U(-eta/2, eta/2), comun a ambos modelos. */
    private double noise() {
        double eta = params.getNoise();
        return random.nextDouble() * eta - eta / 2;
    }

    /** Lleva x a [0, L) - wrap-around para el contorno periodico. */
    private static double wrap(double x, int L) {
        double wrapped = x % L;
        return wrapped < 0 ? wrapped + L : wrapped;
    }
}
