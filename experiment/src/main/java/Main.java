import models.Grid;
import utils.CsvWriter;

import java.io.IOException;
import java.util.Random;

public class Main {
    public static void main(String[] args) throws IOException {
        int N = args.length > 0 ? Integer.parseInt(args[0]) : 10;
        int width = 20;
        int height = 20;
        Grid grid = new Grid(N, width, height);
        Random random = new Random();

        while (grid.getParticles().size() < N) {
            int x = random.nextInt(width);
            int y = random.nextInt(height);
            grid.addRandomParticle(x, y);
        }

        CsvWriter.writeStatic(grid, "static.csv");
        System.out.println("Wrote static.csv");
    }
}
