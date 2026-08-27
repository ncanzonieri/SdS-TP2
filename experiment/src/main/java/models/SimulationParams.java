package models;

public class SimulationParams {

    public enum Model { VICSEK, VOTANTE }

    private final int N;
    private final int L;
    private final double R;
    private final double v;
    private final double noise;
    private final int T;
    private final long seed;
    private final Model model;

    public SimulationParams(int N, int L, double R, double v, double noise, int T, long seed, Model model) {
        this.N = N;
        this.L = L;
        this.R = R;
        this.v = v;
        this.noise = noise;
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

    public double getR() {
        return R;
    }

    public double getV() {
        return v;
    }

    public double getNoise() {
        return noise;
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
