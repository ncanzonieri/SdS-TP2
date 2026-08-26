import models.Grid;
import utils.CsvWriter;

import java.io.IOException;
import java.util.Random;

public class Main {
    public static void main(String[] args) throws IOException {
        int N = args.length > 0 ? Integer.parseInt(args[0]) : 10;
        Grid grid = new Grid(N);
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
