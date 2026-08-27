package cli;

import models.SimulationParams;
import models.SimulationParams.Model;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/**
 * Parseo de los argumentos de linea de comandos y armado de la lista de
 * corridas a ejecutar. Una "corrida" es una combinacion concreta de
 * (modelo, densidad, eta, repeticion); el barrido es simplemente el producto
 * cartesiano de las listas que se pasen por parametro.
 * Los parametros fijos del TP (L=10, v=0.03, rc=1) son los valores por
 * defecto, pero se pueden pisar por CLI para el benchmark del Paso 6 (que
 * necesita comparar contra la geometria del TP1, con L=20). <- Comentario: no sé si hace falta cambiar L, quizás solo N manteniendo la densidad
 */
public class RunConfig {

    /** Una corrida concreta ya resuelta: sus parametros y donde escribir su output. */
    public record PlannedRun(SimulationParams params, Path outputDir) {
    }

    private int L = 10;
    private double v = 0.03;
    private double rc = 1.0;
    private int T = 500;
    private long seed = 1L;
    private int repeats = 1;
    private Path outDir = Path.of("out");
    private boolean writeDynamic = false;
    private List<Double> rhos = List.of(2.0, 4.0, 8.0);
    private List<Integer> explicitNs = null;
    private List<Double> etas = parseNumberList("0:6:0.5");
    private List<Model> models = List.of(Model.VICSEK);

    public static final String USAGE = """
            Motor de simulacion TP2 - bandadas de agentes autopropulsados (Vicsek / Votante).

            Uso: java -cp target/classes Main [opciones]

            Opciones (todas opcionales, entre parentesis el valor por defecto):
              --model <lista>   vicsek | votante | both                        (vicsek)
              --rho <lista>     densidades; N = rho*L^2                        (2,4,8)
              --N <lista>       cantidad de particulas (alternativa a --rho)
              --eta <lista>     amplitud del ruido                             (0:6:0.5)
              --T <int>         pasos de tiempo por corrida                    (500)
              --repeats <int>   realizaciones por combinacion (distinta semilla) (1)
              --seed <long>     semilla base                                   (1)
              --out <dir>       carpeta base de salida                         (out)
              --dynamic         escribir tambien dynamic.txt (para animar)     (desactivado)
              --L <int>         lado de la caja                                (10)
              --v <double>      modulo de la velocidad                         (0.03)
              --rc <double>     radio de interaccion                           (1.0)
              --help            muestra esta ayuda

            Las <lista> aceptan valores separados por coma (0.1,0.5,2) o un rango
            desde:hasta:paso (0:6:0.5). Se corre una simulacion por cada combinacion
            de modelo x densidad x eta x repeticion.

            dynamic.txt (el archivo que consume la animacion) pesa ~14 MB por corrida
            con N=800/T=500, asi que NO se escribe salvo que pases --dynamic. Para las
            curvas de va y S alcanza con observables.txt, que se escribe siempre.

            Ejemplos:
              # barrido completo de eta para las 3 densidades, ambos modelos (solo observables)
              java -cp target/classes Main --model both --rho 2,4,8 --eta 0:6:0.5 --T 500

              # una corrida caracteristica, con frames para animar
              java -cp target/classes Main --model vicsek --rho 4 --eta 0.5 --T 500 --dynamic

              # densidades bajas del estudio de clusters
              java -cp target/classes Main --N 11,16,32 --eta 0:6:0.5 --T 500
            """;

    /** Devuelve null si se pidio --help (el caller debe imprimir USAGE y salir). */
    public static RunConfig parse(String[] args) {
        RunConfig config = new RunConfig();
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            switch (arg) {
                case "--help", "-h" -> {
                    return null;
                }
                case "--dynamic" -> config.writeDynamic = true;
                case "--model" -> config.models = parseModels(next(args, ++i, arg));
                case "--rho" -> config.rhos = parseNumberList(next(args, ++i, arg));
                case "--N" -> config.explicitNs = parseNumberList(next(args, ++i, arg))
                        .stream().map(Double::intValue).toList();
                case "--eta" -> config.etas = parseNumberList(next(args, ++i, arg));
                case "--T" -> config.T = Integer.parseInt(next(args, ++i, arg));
                case "--repeats" -> config.repeats = Integer.parseInt(next(args, ++i, arg));
                case "--seed" -> config.seed = Long.parseLong(next(args, ++i, arg));
                case "--out" -> config.outDir = Path.of(next(args, ++i, arg));
                case "--L" -> config.L = Integer.parseInt(next(args, ++i, arg));
                case "--v" -> config.v = Double.parseDouble(next(args, ++i, arg));
                case "--rc" -> config.rc = Double.parseDouble(next(args, ++i, arg));
                default -> throw new IllegalArgumentException(
                        "Argumento desconocido: " + arg + " (usa --help para ver las opciones)");
            }
        }
        config.validate();
        return config;
    }

    private static String next(String[] args, int i, String flag) {
        if (i >= args.length) {
            throw new IllegalArgumentException("Falta el valor de " + flag);
        }
        return args[i];
    }

    private void validate() {
        if (T <= 0) {
            throw new IllegalArgumentException("--T debe ser > 0");
        }
        if (repeats <= 0) {
            throw new IllegalArgumentException("--repeats debe ser > 0");
        }
        if (rc <= 0 || rc > L) {
            throw new IllegalArgumentException("--rc debe estar en (0, L]");
        }
        for (double eta : etas) {
            if (eta < 0) {
                throw new IllegalArgumentException("--eta no puede ser negativo (fue " + eta + ")");
            }
        }
        for (int n : particleCounts()) {
            if (n <= 0) {
                throw new IllegalArgumentException(
                        "La cantidad de particulas debe ser > 0 (quedo " + n + "; revisa --rho o --N)");
            }
        }
    }

    /** Cantidades de particulas a simular: las de --N si se pasaron, si no N = rho*L^2. */
    private List<Integer> particleCounts() {
        if (explicitNs != null) {
            return explicitNs;
        }
        return rhos.stream().map(rho -> SimulationParams.nFromDensity(rho, L)).toList();
    }

    /** Producto cartesiano modelo x densidad x eta x repeticion. */
    public List<PlannedRun> buildRuns() {
        List<Integer> counts = particleCounts();
        List<PlannedRun> runs = new ArrayList<>();
        for (Model model : models) {
            for (int n : counts) {
                for (double eta : etas) {
                    for (int r = 0; r < repeats; r++) {
                        // Semilla distinta por repeticion, pero determinista: dos
                        // ejecuciones con la misma --seed dan exactamente lo mismo.
                        long runSeed = seed + 31L * r;
                        SimulationParams params =
                                new SimulationParams(n, L, rc, v, eta, T, runSeed, model);
                        runs.add(new PlannedRun(params, outDir.resolve(dirName(model, n, eta, r))));
                    }
                }
            }
        }
        return runs;
    }

    /**
     * Nombre de carpeta derivado de los parametros, para que dos corridas
     * distintas nunca se pisen. La densidad va en el nombre (no N) porque es lo
     * que se grafica; con --N se recalcula rho = N/L^2 para mantenerlo legible.
     */
    private String dirName(Model model, int n, double eta, int repeat) {
        double rho = (double) n / (L * L);
        String name = String.format(Locale.ROOT, "%s_rho%s_eta%s",
                model.name().toLowerCase(Locale.ROOT), fmt(rho), fmt(eta));
        return repeats > 1 ? name + "_r" + repeat : name;
    }

    /** Formatea un numero para nombres de carpeta: sin comas decimales ni ceros de mas. */
    private static String fmt(double value) {
        String s = String.format(Locale.ROOT, "%.4f", value);
        s = s.replaceAll("0+$", "");
        s = s.endsWith(".") ? s.substring(0, s.length() - 1) : s;
        return s;
    }

    private static List<Model> parseModels(String raw) {
        if (raw.equalsIgnoreCase("both")) {
            return List.of(Model.VICSEK, Model.VOTANTE);
        }
        return Arrays.stream(raw.split(","))
                .map(String::trim)
                .map(s -> Model.valueOf(s.toUpperCase(Locale.ROOT)))
                .toList();
    }

    /**
     * Acepta "0.1,0.5,2" (lista explicita) o "desde:hasta:paso" (rango inclusivo).
     * El rango se genera como desde + i*paso (no acumulando) para que el error de
     * punto flotante no se arrastre a lo largo de la lista.
     */
    private static List<Double> parseNumberList(String raw) {
        if (!raw.contains(":")) {
            return Arrays.stream(raw.split(","))
                    .map(String::trim)
                    .map(Double::parseDouble)
                    .toList();
        }
        String[] parts = raw.split(":");
        if (parts.length != 3) {
            throw new IllegalArgumentException(
                    "Rango invalido: '" + raw + "' (se espera desde:hasta:paso)");
        }
        double from = Double.parseDouble(parts[0]);
        double to = Double.parseDouble(parts[1]);
        double step = Double.parseDouble(parts[2]);
        if (step <= 0) {
            throw new IllegalArgumentException("El paso del rango debe ser > 0 (fue " + step + ")");
        }
        List<Double> values = new ArrayList<>();
        int count = (int) Math.floor((to - from) / step + 1e-9) + 1;
        for (int i = 0; i < count; i++) {
            values.add(from + i * step);
        }
        return values;
    }

    public boolean isWriteDynamic() {
        return writeDynamic;
    }

    public Path getOutDir() {
        return outDir;
    }
}
