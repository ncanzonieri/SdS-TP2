import cli.RunConfig;
import cli.RunConfig.PlannedRun;
import core.SimulationEngine;
import models.Grid;
import models.SimulationParams;
import utils.SimulationWriter;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

/**
 * Punto de entrada del motor de simulacion. Arma la lista de corridas a partir
 * de los argumentos de linea de comandos (ver RunConfig.USAGE) y ejecuta cada
 * una, dejando sus archivos de salida en su propia carpeta.
 *
 * La simulacion es offline: aca solo se generan los archivos de texto. La
 * animacion y el analisis se corren despues, por separado, tomandolos como
 * input.
 */
public class Main {

    public static void main(String[] args) throws IOException {
        RunConfig config;
        try {
            config = RunConfig.parse(args);
        } catch (IllegalArgumentException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
            return;
        }
        if (config == null) { // --help
            System.out.println(RunConfig.USAGE);
            return;
        }

        List<PlannedRun> runs = config.buildRuns();
        System.out.printf(Locale.ROOT, "Corridas a ejecutar: %d (output en %s/)%n",
                runs.size(), config.getOutDir());
        if (!config.isWriteDynamic()) {
            System.out.println("Sin dynamic.txt (pasa --dynamic si necesitas los frames para animar).");
        }

        long start = System.nanoTime();
        for (int i = 0; i < runs.size(); i++) {
            PlannedRun run = runs.get(i);
            System.out.printf(Locale.ROOT, "[%d/%d] %s ... ", i + 1, runs.size(),
                    run.outputDir().getFileName());
            System.out.flush();

            double va = execute(run, config.isWriteDynamic());
            System.out.printf(Locale.ROOT, "va_final=%.4f%n", va);
        }
        System.out.printf(Locale.ROOT, "Listo en %.1f s.%n", (System.nanoTime() - start) / 1e9);
    }

    /** Ejecuta una corrida completa y devuelve la polarizacion del estado final. */
    private static double execute(PlannedRun run, boolean writeDynamic) throws IOException {
        SimulationParams params = run.params();
        Grid grid = new Grid(params);
        grid.initializeRandom();

        try (SimulationWriter writer = new SimulationWriter(run.outputDir(), params, writeDynamic)) {
            SimulationEngine engine = new SimulationEngine(grid, params, writer);
            engine.run(params.getT());
            List<core.ObservableSample> observables = engine.getObservables();
            return observables.get(observables.size() - 1).va();
        }
    }
}
