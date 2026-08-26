import models.Grid;
import models.SimulationParams;
import utils.CsvWriter;

import java.io.IOException;
import java.util.Random;

public class Main {
    public static void main(String[] args) throws IOException {
        int N = args.length > 0 ? Integer.parseInt(args[0]) : 10;
        // TODO(Paso 5): reemplazar estos valores fijos por argumentos/config real
        // (rho, eta, modelo, T, semilla, carpeta de salida) y wirear el loop de
        // simulacion. Por ahora solo se ajusta la construccion de Grid al nuevo
        // constructor parametrizado del Paso 1, sin cambiar el comportamiento actual.
        SimulationParams params = new SimulationParams(
                N, 10, 1.0, 0.03, 0.0, 0, System.nanoTime(), SimulationParams.Model.VICSEK);
        Grid grid = new Grid(params);
        Random random = new Random();

        int side = grid.getL();

        while (grid.getParticles().size() < N) {
            int x = random.nextInt(side);
            int y = random.nextInt(side);
            grid.addRandomParticle(x, y);
        }

        CsvWriter.writeStatic(grid, "static.csv");
        System.out.println("Wrote static.csv");
    }
}
