package analysis;

import models.Particle;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ClusterFinderTest {

    @Test
    void emptySystemIsZero() {
        assertEquals(0.0, ClusterFinder.largestClusterFraction(Map.of(), List.of()));
    }

    @Test
    void chainOfThreePlusIsolateIsGiantThreeQuarters() {
        Particle a = new Particle(0, 0, 0, 0);
        Particle b = new Particle(1, 0, 0, 0);
        Particle c = new Particle(2, 0, 0, 0);
        Particle isolated = new Particle(3, 0, 0, 0);
        Map<Particle, List<Particle>> neighbors = new HashMap<>();
        neighbors.put(a, List.of(b));
        neighbors.put(b, List.of(a, c));
        neighbors.put(c, List.of(b));
        double s = ClusterFinder.largestClusterFraction(neighbors, List.of(a, b, c, isolated));
        assertEquals(0.75, s, 1e-12);
    }

    @Test
    void allIsolatedIsOneOverN() {
        Particle a = new Particle(0, 0, 0, 0);
        Particle b = new Particle(1, 0, 0, 0);
        double s = ClusterFinder.largestClusterFraction(Map.of(), List.of(a, b));
        assertEquals(0.5, s, 1e-12);
    }
}
