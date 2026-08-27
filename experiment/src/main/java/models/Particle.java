package models;

import java.util.Objects;

public class Particle {
    private final int id;
    private double x;
    private double y;
    private double angle;

    public Particle(int id, double x, double y, double angle) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.angle = angle;
    }

    public double getX() {
        return x;
    }

    public void setX(double x) {
        this.x = x;
    }

    public double getY() {
        return y;
    }

    public void setY(double y) {
        this.y = y;
    }

    public double getAngle() {
        return angle;
    }

    public void setAngle(double angle) {
        this.angle = angle;
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof Particle && this.id == ((Particle)o).id;
    }

    @Override
    public int hashCode() {
        // Consistente con equals (que solo compara id) - necesario porque Particle
        // se usa como key de HashMap/HashSet en Grid.nearestNeighbor().
        return Objects.hash(id);
    }

    /** Componente x de la velocidad, dado el modulo v (constante, vive en SimulationParams). */
    public double vx(double v) {
        return v * Math.cos(angle);
    }

    /** Componente y de la velocidad, dado el modulo v (constante, vive en SimulationParams). */
    public double vy(double v) {
        return v * Math.sin(angle);
    }
}
