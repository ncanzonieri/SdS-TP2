package models;

import java.util.*;

public class Grid {
    private final int N;
    private final int L;
    private final double rc;
    // Cantidad de celdas por lado del CIM y su tamano real: M = floor(L/rc),
    // cellSize = L/M (siempre >= rc). Antes el codigo asumia M == L (valido
    // solo cuando rc == 1); con L y rc ahora parametrizables, hay que
    // calcularlo en serio para no romper el CIM si rc != 1.
    private final int M;
    private final double cellSize;
    private final List<Particle> particles;
    private final Random random;

    public Grid(SimulationParams params) {
        this.N = params.getN();
        this.L = params.getL();
        this.rc = params.getRc();
        this.M = Math.max(1, (int) Math.floor((double) this.L / this.rc));
        this.cellSize = (double) this.L / this.M;
        this.particles = new ArrayList<>();
        this.random = new Random(params.getSeed());
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

    /** Adds a random particle into cell (x, y). Several particles can share a cell. */
    public boolean addRandomParticle(int x, int y) {
        if (particles.size() >= N) {
            return false;
        }
        if (x < 0 || x >= L || y < 0 || y >= L) {
            return false;
        }

        double angle = random.nextDouble() * 2*Math.PI;
        Particle particle = new Particle(particles.size() + 1, x, y, angle);

        particles.add(particle);
        return true;
    }

    // La regla de actualizacion (Vicsek/Votante), el ruido y el loop temporal
    // viven ahora en core.SimulationEngine (Paso 2) - Grid solo se ocupa del
    // modelo de datos y del CIM.

    public Map<Particle,List<Particle>> nearestNeighbor() {
        Map<Cell,List<Particle>> grid = new HashMap<>();
        for (Particle particle : particles) {
            int i = (int) (particle.getX() / cellSize);
            int j = (int) (particle.getY() / cellSize);
            grid.computeIfAbsent(new Cell(i, j), k -> new ArrayList<>()).add(particle);
        }

        Map<Particle,List<Particle>> neighbours = new HashMap<>();
        for(Map.Entry<Cell,List<Particle>> entry : grid.entrySet()) {
            Set<Particle> possible = new HashSet<>();
            possible.addAll(grid.getOrDefault(new Cell((entry.getKey().getI() + 1) % M , entry.getKey().getJ()), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell((entry.getKey().getI() + 1) % M , (entry.getKey().getJ() + 1) % M), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell(entry.getKey().getI() , (entry.getKey().getJ() + 1) % M), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell((entry.getKey().getI() + M - 1) % M , (entry.getKey().getJ() + 1) % M), new ArrayList<>()));
            entry.getValue().forEach(possible::remove);
            cellIndexMethod(neighbours, entry, possible);
        }
        return neighbours;
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
        return Math.hypot(dx, dy) < rc;
    }

    private static void addUnique(Map<Particle, List<Particle>> neighbours, Particle particle, Particle other) {
        List<Particle> values = neighbours.computeIfAbsent(particle, k -> new ArrayList<>());
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
