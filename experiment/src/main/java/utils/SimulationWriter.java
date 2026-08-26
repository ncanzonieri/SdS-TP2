package utils;

import models.Particle;
import models.SimulationParams;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;

/**
 * Escribe a disco los archivos de texto plano de una corrida, siguiendo el
 * formato de catedra (Contexto_Teorico/docs/teoria/Teorica_1.md). La animacion
 * y el analisis se corren despues, por separado, tomando estos archivos como
 * input.
 *
 * Genera tres archivos dentro de `outputDir`:
 *
 *   static.txt      metadatos constantes de la corrida, uno por linea:
 *                   N, L, v, rc, eta, T, modelo
 *
 *   dynamic.txt     estado del sistema en cada paso de tiempo:
 *                     t
 *                     x1 y1 vx1 vy1
 *                     ...
 *                     xN yN vxN vyN
 *                   (el nro. de fila dentro de cada bloque es la identidad de
 *                   la particula, como pide el formato de catedra)
 *                   Solo se genera si writeDynamic == true, porque pesa ~14 MB
 *                   por corrida con N=800/T=500: hace falta para las
 *                   animaciones (punto a del enunciado, "pocas situaciones
 *                   caracteristicas") pero seria un desperdicio generarlo en
 *                   las ~120 corridas del barrido de eta, que solo necesitan
 *                   observables.txt.
 *
 *   observables.txt una linea por paso de tiempo: `t va S`, con una linea de
 *                   encabezado comentada con '#' (numpy.loadtxt la ignora).
 *
 * IMPORTANTE: todos los numeros se formatean con Locale.ROOT (punto decimal).
 * Sin esto, en una maquina con locale es-AR Java escribiria "0,998" y los
 * scripts de analisis en Python no podrian parsear los archivos.
 */
public class SimulationWriter implements AutoCloseable {

    private final double v;
    private final BufferedWriter dynamicWriter;
    private final BufferedWriter observablesWriter;

    /** Corrida completa: escribe tambien dynamic.txt (para animar). */
    public SimulationWriter(Path outputDir, SimulationParams params) throws IOException {
        this(outputDir, params, true);
    }

    public SimulationWriter(Path outputDir, SimulationParams params, boolean writeDynamic) throws IOException {
        this.v = params.getV();
        Files.createDirectories(outputDir);
        writeStatic(outputDir.resolve("static.txt"), params);
        this.dynamicWriter = writeDynamic
                ? Files.newBufferedWriter(outputDir.resolve("dynamic.txt"))
                : null;
        this.observablesWriter = Files.newBufferedWriter(outputDir.resolve("observables.txt"));
        this.observablesWriter.write("# t va S\n");
    }

    private static void writeStatic(Path file, SimulationParams params) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(file)) {
            writer.write(params.getN() + "\n");
            writer.write(params.getL() + "\n");
            writer.write(format(params.getV()) + "\n");
            writer.write(format(params.getRc()) + "\n");
            writer.write(format(params.getEta()) + "\n");
            writer.write(params.getT() + "\n");
            writer.write(params.getModel() + "\n");
        }
    }

    /** Vuelca el estado de todas las particulas en el instante t (no-op si no se pidio dynamic.txt). */
    public void writeFrame(int t, List<Particle> particles) {
        if (dynamicWriter == null) {
            return;
        }
        try {
            dynamicWriter.write(t + "\n");
            for (Particle p : particles) {
                dynamicWriter.write(format(p.getX()) + " " + format(p.getY()) + " "
                        + format(p.vx(v)) + " " + format(p.vy(v)) + "\n");
            }
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    /** Agrega la linea de observables (t, va, S) del instante t. */
    public void writeObservables(int t, double va, double s) {
        try {
            observablesWriter.write(t + " " + format(va) + " " + format(s) + "\n");
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static String format(double value) {
        return String.format(Locale.ROOT, "%.6f", value);
    }

    @Override
    public void close() throws IOException {
        try (BufferedWriter d = dynamicWriter; BufferedWriter o = observablesWriter) {
            if (d != null) {
                d.flush();
            }
            o.flush();
        }
    }
}
