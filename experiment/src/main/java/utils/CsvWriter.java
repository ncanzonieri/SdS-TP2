package utils;

import models.Grid;
import models.Particle;

import java.io.FileWriter;
import java.io.IOException;

public class CsvWriter {
    public static void writeStatic(Grid grid, String filename) throws IOException {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.write(grid.getParticles().size() + "\n");
            writer.write(grid.getL() + "\n");
            for (Particle p : grid.getParticles()) {
                writer.write(p.getId() + "," + p.getX() + "," + p.getY() + "," + p.getAngle() + "\n");
            }
        }
    }
}
