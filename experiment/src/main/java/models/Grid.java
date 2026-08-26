package models;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Grid {
    private final int N;
    private final double noise;
    private final static int L=10;
    private final static double R=1.0;
    private final boolean isViscek;
    private final List<Particle> particles;
    private final Random random;

    @SuppressWarnings("unchecked")
    public Grid(SimulationParams params) {
        this.N = params.getN();
        this.noise = params.getNoise();
        this.particles = new ArrayList<>();
        this.random = new Random(params.getSeed());
        this.isViscek = params.getModel().equals(SimulationParams.Model.VICSEK);
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

    /** Adds a random particle into cell (x, y). Several particles can share a cell. */
    public void addRandomParticle(int x, int y) {
        if (particles.size() >= N) {
            return;
        }
        if (x < 0 || x >= L || y < 0 || y >= L) {
            return;
        }

        double angle = random.nextDouble() * 2*Math.PI;
        Particle particle = new Particle(particles.size() + 1, x, y, angle);

        particles.add(particle);
    }

    public double viscek(Particle particle, List<Particle> neighbors) {
        return Stream.concat(Stream.of(particle),neighbors.stream())
                .collect(Collectors.teeing(
                        Collectors.summingDouble(p->Math.sin(p.getAngle())),
                        Collectors.summingDouble(p->Math.cos(p.getAngle())),
                        Math::atan2
                ));
    }

    public double voting(Particle particle, List<Particle> neighbors) {
        return neighbors.get(random.nextInt(neighbors.size())).getAngle();
    }

    /**
     * Simula un tick de simulación, actualizando ángulos y posiciones de partículas y devolviendo el parámetro de orden en el nuevo instante
     * @return
     */
    public double simulateTick() {
        Map<Particle,List<Particle>> neighbors = nearestNeighbor();
        for (Particle particle : particles) {
            double theta = isViscek ?
                    viscek(particle,neighbors.get(particle)) :
                    voting(particle,neighbors.get(particle)) +
                    random.nextDouble(-noise/2, noise/2);
            double x = particle.getX()+10*Math.cos(theta);
            double y = particle.getY() +10*Math.sin(theta);
            particle.setAngle(theta);
            particle.setX(x);
            particle.setY(y);
        }
        return particles.stream().collect(Collectors.teeing(
                Collectors.summingDouble(p->Math.cos(p.getAngle())),
                Collectors.summingDouble(p->Math.sin(p.getAngle())),
                Math::hypot
        ))/N;
    }

    public Map<Particle,List<Particle>> nearestNeighbor() {
        Map<Cell,List<Particle>> grid = new HashMap<>();
        for (Particle particle : particles) {
            int i = (int) (particle.getX() / R);
            int j = (int) (particle.getY() / R);
            grid.computeIfAbsent(new Cell(i, j), k -> new ArrayList<>()).add(particle);
        }

        Map<Particle,List<Particle>> neighbours = new HashMap<>();
        for(Map.Entry<Cell,List<Particle>> entry : grid.entrySet()) {
            Set<Particle> possible = new HashSet<>();
            possible.addAll(grid.getOrDefault(new Cell((entry.getKey().getI() + 1) % L , entry.getKey().getJ()), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell((entry.getKey().getI() + 1) % L , (entry.getKey().getJ() + 1) % L), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell(entry.getKey().getI() , (entry.getKey().getJ() + 1) % L), new ArrayList<>()));
            possible.addAll(grid.getOrDefault(new Cell((entry.getKey().getI() + L - 1) % L , (entry.getKey().getJ() + 1) % L), new ArrayList<>()));
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
        return Math.hypot(dx, dy) < R;
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
