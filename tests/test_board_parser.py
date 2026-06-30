import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from app.board_parser import BoardParser


class BoardParserTests(unittest.TestCase):
    def test_detects_sun_moon_and_blank_cells(self):
        image = Image.new("RGB", (400, 400), "white")
        draw = ImageDraw.Draw(image)

        cell = 120
        for row in range(3):
            for col in range(3):
                x1 = 20 + col * cell
                y1 = 20 + row * cell
                x2 = x1 + cell - 30
                y2 = y1 + cell - 30
                draw.rectangle([x1, y1, x2, y2], outline="black", width=2)

        draw.ellipse([50, 50, 90, 90], fill=(255, 0, 0))
        draw.ellipse([170, 170, 210, 210], fill=(0, 0, 255))

        # Draw an 'x' sign centered on the horizontal boundary between (0, 0) and (0, 1)
        # Boundary gap is x=110 to 140. Center gap x=125. Row 0 center y=65.
        draw.rectangle([120, 60, 130, 70], fill="black")

        # Draw an '=' sign centered on the vertical boundary between (1, 1) and (1, 2)
        # Boundary gap is x=230 to 260. Center gap x=245. Row 1 center y=185.
        draw.rectangle([237, 179, 253, 181], fill="black")
        draw.rectangle([237, 188, 253, 190], fill="black")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            image.save(temp_file.name)
            temp_path = Path(temp_file.name)

        try:
            parser = BoardParser(
                grid_size=3,
                moon_color=(255, 0, 0),
                sun_color=(0, 0, 255),
                tolerance=10
            )
            result = parser.parse_image(temp_path)

            self.assertEqual(result["board"][0][0], "moon")
            self.assertEqual(result["board"][1][1], "sun")
            self.assertEqual(result["board"][2][2], "blank")

            signs = result["signs"]
            self.assertEqual(len(signs), 2)
            
            x_sign = [s for s in signs if s["type"] == "x"][0]
            eq_sign = [s for s in signs if s["type"] == "="][0]
            
            self.assertEqual(x_sign["cells"], [(0, 0), (0, 1)])
            self.assertEqual(eq_sign["cells"], [(1, 1), (1, 2)])
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
