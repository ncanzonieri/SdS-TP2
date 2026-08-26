package analysis;

import models.Particle;

import java.util.List;

/**
 * Polarizacion (parametro de orden) del sistema: va = |Sum_i (cos th_i, sin th_i)| / N.
 *
 * El modulo de velocidad v de la formula del enunciado (va = ||Sum Vi|| / (N*v))
 * se cancela por ser constante e igual para todas las particulas, asi que
 * calcularlo con los vectores unitarios (cos th, sin th) da exactamente el
 * mismo resultado sin tener que pasarle v.
 */
public final class OrderParameter {

    private OrderParameter() {
    }

    public static double polarization(List<Particle> particles) {
        if (particles.isEmpty()) {
            return 0.0;
        }
        double sumCos = 0;
        double sumSin = 0;
        for (Particle p : particles) {
            sumCos += Math.cos(p.getAngle());
            sumSin += Math.sin(p.getAngle());
        }
        return Math.hypot(sumCos, sumSin) / particles.size();
    }
}
