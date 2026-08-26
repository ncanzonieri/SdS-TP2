package models;

/**
 * Parametros de una corrida de simulacion (Vicsek u Votante). Agrupa todo lo que
 * hoy estaba hardcodeado (L, R, velocidad, semilla) para que Grid y el resto del
 * motor no dependan de constantes sueltas.
 */
public class SimulationParams {

    public enum Model { VICSEK, VOTANTE }

    private final int N;
    private final int L;
    private final double rc;
    private final double v;
    private final double eta;
    private final int T;
    private final long seed;
    private final Model model;

    public SimulationParams(int N, int L, double rc, double v, double eta, int T, long seed, Model model) {
        this.N = N;
        this.L = L;
        this.rc = rc;
        this.v = v;
        this.eta = eta;
        this.T = T;
        this.seed = seed;
        this.model = model;
    }

    /**
     * N = rho * L^2, redondeado al entero mas cercano. Sirve tanto para las
     * densidades generales (rho=2,4,8) como para las densidades bajas usadas
     * solo en el estudio de clusters (rho=1/pi, 1/(2pi), 1/(3pi)).
     */
    public static int nFromDensity(double rho, int L) {
        return (int) Math.round(rho * L * L);
    }

    public int getN() {
        return N;
    }

    public int getL() {
        return L;
    }

    public double getRc() {
        return rc;
    }

    public double getV() {
        return v;
    }

    public double getEta() {
        return eta;
    }

    public int getT() {
        return T;
    }

    public long getSeed() {
        return seed;
    }

    public Model getModel() {
        return model;
    }
}
