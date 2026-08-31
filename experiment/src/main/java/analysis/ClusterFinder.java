package analysis;
import models.Particle;
import java.util.*;

public final class ClusterFinder {
    public static double largestClusterFraction(Map<Particle, List<Particle>> neighbors, List<Particle> particles) {
        if (particles.isEmpty())
            return 0;
        Set<Particle> visited = new HashSet<>();
        List<Set<Particle>> clusters = new LinkedList<>();
        for (Particle particle : particles) {
            if(visited.contains(particle))
                continue;
            visited.add(particle);
            Set<Particle> cluster = new HashSet<>();
            clusters.add(cluster);
            recursiveAdd(particle,neighbors,cluster,visited);
        }
        clusters.sort(Comparator.comparingInt(Set::size));
        return clusters.getFirst().size() / (double) particles.size();
    }

    public static void recursiveAdd(Particle particle, Map<Particle, List<Particle>> neighbors, Set<Particle> cluster, Set<Particle> visited) {
        cluster.add(particle);
        for (Particle neighbor : neighbors.getOrDefault(particle,Collections.emptyList())) {
            visited.add(neighbor);
            recursiveAdd(neighbor,neighbors,cluster,visited);
        }
    }
}