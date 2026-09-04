package benchmark;

import cli.RunConfig;
import models.Grid;
import models.SimulationParams;
import models.SimulationParams.Model;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.function.IntUnaryOperator;

/**
 * Tiempos de nearestNeighbor() aislados de I/O (punto g del TP2 / analogo
 * al punto 4 del TP1). No corre el loop de Vicsek/Votante ni escribe frames.
 */
public final class CimBenchmark {

    public static final int DEFAULT_L = 10;
    public static final double DEFAULT_RC = 1.0;
    public static final int DEFAULT_REPS = 200;
    public static final int WARMUP = 20;
    public static final Path DEFAULT_OUT = Path.of("out/cim");
    public static final List<Integer> DEFAULT_NS = List.of(
            5, 10, 20, 30, 50, 75, 100, 150, 200, 250);

    private CimBenchmark() {
    }

    public static void runFrom(RunConfig config) throws IOException {
        int L = config.isLExplicit() ? config.getL() : DEFAULT_L;
        double rc = config.isRcExplicit() ? config.getRc() : DEFAULT_RC;
        int reps = config.isRepeatsExplicit() ? config.getRepeats() : DEFAULT_REPS;
        Path outDir = config.isOutExplicit() ? config.getOutDir() : DEFAULT_OUT;
        List<Integer> ns = config.getExplicitNs() != null ? config.getExplicitNs() : DEFAULT_NS;

        Double fixedRhoArg = config.isRhoExplicit() ? config.getRhos().get(0) : null;
        if (rc <= 0 || rc > L) {
            throw new IllegalArgumentException("--rc debe estar en (0, L] (L=" + L + ", rc=" + rc + ")");
        }
        run(L, rc, ns, reps, outDir, fixedRhoArg);
    }

    public static void run(int L, double rc, List<Integer> ns, int reps, Path outDir) throws IOException {
        run(L, rc, ns, reps, outDir, null);
    }

    public static void run(int L, double rc, List<Integer> ns, int reps, Path outDir, Double rhoOverride)
            throws IOException {
        Files.createDirectories(outDir);
        Path fixedL = outDir.resolve("cim_times_L" + L + ".txt");
        writeSeries(fixedL, ns, n -> L, rc, reps,
                String.format(Locale.ROOT, "# CIM nearestNeighbor only; fixed L=%d rc=%s warmup=%d reps=%d",
                        L, format(rc), WARMUP, reps));

        int nRef = ns.contains(200) ? 200 : ns.get(ns.size() / 2);
        double rho = rhoOverride != null ? rhoOverride : (double) nRef / ((double) L * L);
        int minL = Math.max(1, (int) Math.ceil(rc));
        Path fixedRho = outDir.resolve("cim_times_rho_fixed.txt");
        writeSeries(fixedRho, ns, n -> Math.max(minL, (int) Math.round(Math.sqrt(n / rho))), rc, reps,
                String.format(Locale.ROOT, "# CIM nearestNeighbor only; fixed rho=%s (L crece con N) rc=%s warmup=%d reps=%d",
                        format(rho), format(rc), WARMUP, reps));

        System.out.printf(Locale.ROOT, "CIM benchmark listo: %s%n", outDir);
    }

    private static void writeSeries(Path file, List<Integer> ns, IntUnaryOperator lForN,
                                    double rc, int reps, String header) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(file)) {
            writer.write(header + "\n");
            writer.write("# N L mean_ns stdev_ns mean_ms\n");
            for (int n : ns) {
                int L = lForN.applyAsInt(n);
                Stats stats = timeCim(n, L, rc, WARMUP, reps);
                writer.write(String.format(Locale.ROOT, "%d %d %.1f %.1f %.6f%n",
                        n, L, stats.meanNs, stats.stdevNs, stats.meanNs / 1e6));
                System.out.printf(Locale.ROOT, "  N=%d L=%d  mean=%.3f ms%n",
                        n, L, stats.meanNs / 1e6);
            }
        }
    }

    private static Stats timeCim(int n, int L, double rc, int warmup, int reps) {
        SimulationParams params = new SimulationParams(n, L, rc, 0.03, 0.0, 1, 1L, Model.VICSEK);
        Grid grid = new Grid(params);
        grid.initializeRandom();
        for (int i = 0; i < warmup; i++) {
            grid.nearestNeighbor();
        }
        long[] samples = new long[reps];
        for (int i = 0; i < reps; i++) {
            long t0 = System.nanoTime();
            grid.nearestNeighbor();
            samples[i] = System.nanoTime() - t0;
        }
        return Stats.of(samples);
    }

    private static String format(double value) {
        return String.format(Locale.ROOT, "%.6f", value);
    }

    private record Stats(double meanNs, double stdevNs) {
        static Stats of(long[] samples) {
            int n = samples.length;
            double mean = 0;
            for (long s : samples) {
                mean += s;
            }
            mean /= n;
            double var = 0;
            for (long s : samples) {
                double d = s - mean;
                var += d * d;
            }
            double stdev = n > 1 ? Math.sqrt(var / (n - 1)) : 0;
            return new Stats(mean, stdev);
        }
    }
}
