package analysis;

import models.Particle;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Union-Find (Disjoint Set, con path compression y union by rank) sobre el
 * grafo de vecindad que devuelve Grid.nearestNeighbor(): un cluster es un
 * conjunto de particulas donde todo par esta conectado por una cadena de
 * saltos entre vecino y vecino (particulas dentro del radio de interaccion rc).
 */
public final class ClusterFinder {

    private ClusterFinder() {
    }

    /** S = tamano del cluster mas grande / N (fraccion de nodos en la componente gigante). */
    public static double largestClusterFraction(Map<Particle, List<Particle>> neighbors, List<Particle> particles) {
        int n = particles.size();
        if (n == 0) {
            return 0.0;
        }

        Map<Particle, Integer> index = new HashMap<>();
        for (int i = 0; i < n; i++) {
            index.put(particles.get(i), i);
        }

        int[] parent = new int[n];
        int[] rank = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }

        for (Map.Entry<Particle, List<Particle>> entry : neighbors.entrySet()) {
            int a = index.get(entry.getKey());
            for (Particle other : entry.getValue()) {
                union(parent, rank, a, index.get(other));
            }
        }

        int[] sizes = new int[n];
        for (int i = 0; i < n; i++) {
            sizes[find(parent, i)]++;
        }
        int largest = 0;
        for (int size : sizes) {
            largest = Math.max(largest, size);
        }
        return (double) largest / n;
    }

    private static int find(int[] parent, int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]]; // path compression (halving)
            x = parent[x];
        }
        return x;
    }

    private static void union(int[] parent, int[] rank, int a, int b) {
        int ra = find(parent, a);
        int rb = find(parent, b);
        if (ra == rb) {
            return;
        }
        if (rank[ra] < rank[rb]) {
            parent[ra] = rb;
        } else if (rank[ra] > rank[rb]) {
            parent[rb] = ra;
        } else {
            parent[rb] = ra;
            rank[ra]++;
        }
    }
}
