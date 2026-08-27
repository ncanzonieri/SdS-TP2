package models;

import java.util.*;

public class Grid {
    private final int N;
    private final int L;
    private final double R;
    private final int M;
    private final double cellSize;
    private final List<Particle> particles;
    private final Random random;

    public Grid(SimulationParams params) {
        this.N = params.getN();
        this.L = params.getL();
        this.R = params.getR();
        this.M = Math.max(1, (int) Math.floor(L / R));
        this.cellSize = (double) L / M;
        this.particles = new ArrayList<>();
        this.random = new Random(params.getSeed());
    }

    public int getN() {
        return N;
    }

    public int getL() {
        return L;
    }

    public List<Particle> getParticles() {
        return particles;
    }

    /**
     * Random con semilla de esta corrida (params.getSeed()). Se expone para que
     * SimulationEngine lo reuse para el ruido y el sorteo del modelo de votante,
     * en vez de crear un segundo Random desincronizado.
     */
    public Random getRandom() {
        return random;
    }

    /**
     * Posiciona las N partículas en el plano
     */
    public void initializeRandom() {
        particles.clear();
        for (int i = 0; i < N; i++) {
            particles.add(new Particle(
                    i,
                    random.nextDouble() * L,
                    random.nextDouble() * L,
                    random.nextDouble() * 2 * Math.PI));
        }
    }

    public Map<Particle,List<Particle>> nearestNeighbor() {
        Map<Cell,List<Particle>> grid = new HashMap<>();
        for (Particle particle : particles) {
            int i = cellIndex(particle.getX());
            int j = cellIndex(particle.getY());
            grid.computeIfAbsent(new Cell(i, j), _ -> new ArrayList<>()).add(particle);
        }

        Map<Particle,List<Particle>> neighbours = new HashMap<>();
        for(Map.Entry<Cell,List<Particle>> entry : grid.entrySet()) {
            int ci = entry.getKey().getI();
            int cj = entry.getKey().getJ();
            Set<Particle> possible = new HashSet<>();
            possible.addAll(grid.getOrDefault(new Cell(wrapCell(ci + 1), cj), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell(wrapCell(ci + 1), wrapCell(cj + 1)), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell(ci, wrapCell(cj + 1)), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell(wrapCell(ci - 1), wrapCell(cj + 1)), new ArrayList<>()));
            entry.getValue().forEach(possible::remove);
            cellIndexMethod(neighbours, entry, possible);
        }
        return neighbours;
    }

    /** Indice de celda en [0, M). cellSize = L/M; M = floor(L/rc). */
    private int cellIndex(double coord) {
        int i = (int) (coord / cellSize);
        if (i < 0) {
            return 0;
        }
        if (i >= M) {
            return M - 1;
        }
        return i;
    }

    private int wrapCell(int i) {
        int wrapped = i % M;
        return wrapped < 0 ? wrapped + M : wrapped;
    }

    private void cellIndexMethod(Map<Particle, List<Particle>> neighbours, Map.Entry<Cell, List<Particle>> entry, Set<Particle> possible) {
        for(Particle particle : entry.getValue()) {
            for(Particle other : entry.getValue()) {
                if(!particle.equals(other) && areNeighbours(particle, other)) {
                    addUnique(neighbours, particle, other);
                }
            }
            for(Particle other : possible) {
                if(!particle.equals(other) && areNeighbours(particle, other)) {
                    addUnique(neighbours, particle, other);
                    addUnique(neighbours, other, particle);
                }
            }
        }
    }

    private boolean areNeighbours(Particle particle, Particle other) {
        double dx = Math.abs(particle.getX() - other.getX());
        double dy = Math.abs(particle.getY() - other.getY());
        dx = Math.min(dx, L - dx);
        dy = Math.min(dy, L - dy);
        return Math.hypot(dx, dy) < R;
    }

    private static void addUnique(Map<Particle, List<Particle>> neighbours, Particle particle, Particle other) {
        List<Particle> values = neighbours.computeIfAbsent(particle, _ -> new ArrayList<>());
        if(!values.contains(other)) {
            values.add(other);
        }
    }

    private static class Cell {
        int i;
        int j;
        Cell(int i, int j) {
            this.i = i;
            this.j = j;
        }
        public int getI() {
            return i;
        }
        public int getJ() {
            return j;
        }
        @Override
        public boolean equals(Object o) {
            return o instanceof Cell c && c.i == i && c.j == j;
        }
        @Override
        public int hashCode() {
            return Objects.hash(i, j);
        }
    }
}
