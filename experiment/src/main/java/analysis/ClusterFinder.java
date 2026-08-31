package analysis;
import models.Particle;
import java.util.*;

public final class ClusterFinder {
    public static double largestClusterFraction(Map<Particle, List<Particle>> neighbors, List<Particle> particles) {
        List<Set<Particle>> clusters = new ArrayList<>();
        for (Particle particle : particles) {
            boolean clusterFound = mergeClusters(particle, neighbors.getOrDefault(particle,Collections.emptyList()), clusters);
            if(!clusterFound) {
                Set<Particle> cluster = new HashSet<>(neighbors.getOrDefault(particle, Collections.emptyList()));
                clusters.add(cluster);
            }
        }
        clusters.sort(Comparator.comparingInt(Set::size));
        return (double) clusters.getFirst().size() / particles.size();
    }

    private static boolean mergeClusters(Particle particle, List<Particle> neighbors, List<Set<Particle>> clusters) {
        for(Set<Particle> cluster : clusters) {
            if(cluster.contains(particle)) {
                cluster.addAll(neighbors);
                return true;
            }
        }
        return false;
    }
}