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
 * Escribe a disco los archivos de texto plano de una corrida. La animacion
 * y el analisis se corren despues, por separado, tomando estos archivos como
 * input.
 * Genera hasta tres archivos dentro de `outputDir` (una carpeta por corrida
 * para que no se pisen):
 *   static.txt      exactamente dos lineas: N, luego L. Nada mas: no radio
 *                   ni color por particula, ni v/rc/eta/T/modelo (un parser de
 *                   catedra los leeria como propiedades de particula).
 *   dynamic.txt     un bloque por tick:
 *                     t
 *                     x1 y1 vx1 vy1
 *                     ...
 *                     xN yN vxN vyN
 *                   El orden de filas es el de la lista (identidad estable).
 *                   vx = v*cos(theta), vy = v*sin(theta).
 *                   Solo se genera si writeDynamic == true.
 *   observables.txt una linea por tick: `t va S`, con encabezado `# t va S`.
 * Todos los doubles se formatean con Locale.ROOT (punto decimal, no coma).
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

    /** Escribe static.txt una vez: solo N y L, en ese orden. */
    public static void writeStatic(Path file, SimulationParams params) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(file)) {
            writer.write(params.getN() + "\n");
            writer.write(params.getL() + "\n");
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
