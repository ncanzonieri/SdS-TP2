package models;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Grid {
    private final int N;
    private final int width;
    private final int height;
    private final List<Particle> particles;
    private final List<Particle>[][] matrix;
    private final Random random = new Random();

    @SuppressWarnings("unchecked")
    public Grid(int N, int width, int height) {
        this.N = N;
        this.width = width;
        this.height = height;
        this.particles = new ArrayList<>();
        this.matrix = new List[width][height];

        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                matrix[i][j] = new ArrayList<>();
            }
        }
    }

    public int getN() {
        return N;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public List<Particle> getParticles() {
        return particles;
    }

    public List<Particle>[][] getMatrix() {
        return matrix;
    }

    /** Adds a random particle into cell (x, y). Several particles can share a cell. */
    public boolean addRandomParticle(int x, int y) {
        if (particles.size() >= N) {
            return false;
        }
        if (x < 0 || x >= width || y < 0 || y >= height) {
            return false;
        }

        double angle = random.nextDouble() * 2*Math.PI;
        Particle particle = new Particle(particles.size() + 1, x, y, angle);

        particles.add(particle);
        matrix[x][y].add(particle);
        return true;
    }
}
