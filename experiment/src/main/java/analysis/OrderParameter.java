package analysis;

import models.Particle;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Polarizacion (parametro de orden) del sistema: va = |Sum_i (cos th_i, sin th_i)| / N.
 */
public final class OrderParameter {

    private OrderParameter() {
    }

    public static double polarization(List<Particle> particles) {
        if (particles.isEmpty()) {
            return 0.0;
        }
        return particles.stream().collect(Collectors.teeing(
                Collectors.summingDouble(p->Math.cos(p.getAngle())),
                Collectors.summingDouble(p->Math.sin(p.getAngle())),
                Math::hypot
        ))/particles.size();
    }
}
