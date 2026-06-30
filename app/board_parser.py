from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np


class BoardParser:
    def __init__(
        self,
        grid_size: int = 6,
        cell_padding: int = 6,
        moon_color: Tuple[int, int, int] = (103, 138, 218),
        sun_color: Tuple[int, int, int] = (233, 179, 73),
        tolerance: int = 100,
    ) -> None:
        self.grid_size = grid_size
        self.cell_padding = cell_padding
        self.moon_color = moon_color
        self.sun_color = sun_color
        self.tolerance = tolerance

    def parse_image(self, image_input: str | Path | np.ndarray) -> dict:
        # 1. Stronger check: see if it's a numpy array, OR if it has a shape attribute
        if isinstance(image_input, np.ndarray) or hasattr(image_input, 'shape'):
            img = image_input
        else:
            # 2. Treat it as a path ONLY if it's a string or Path object
            img = cv2.imread(str(image_input))
            if img is None:
                raise FileNotFoundError(f"Could not read image from path: {image_input}")

        # 3. Your existing processing logic continues below...
        img_cropped = self._crop_image(img)
        # img_cropped = img

        img_rgb = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB)
        board_box = self._find_board_region(img_rgb)
        board = []
        for row in range(self.grid_size):
            row_values = []
            for col in range(self.grid_size):
                x0, y0, x1, y1 = self._cell_bounds(board_box, row, col)
                cell_value = self._sample_cell(img_rgb, x0, y0, x1, y1)
                row_values.append(cell_value)
            board.append(row_values)

        signs = self._detect_signs(img_rgb, board_box)
        return {
            "board": board,
            "signs": signs
        }

    def _crop_image(self, img: np.ndarray) -> np.ndarray:
        """Crops the image to isolate the grid using precise pixel boundaries."""
        height, width = img.shape[:2]
        
        # 50px from left/right, 420px from top, 1040px from bottom
        y0 = 420
        y1 = height - 1040
        x0 = 50
        x1 = width - 50

        # Safety boundaries check
        y0 = max(0, min(y0, height))
        y1 = max(0, min(y1, height))
        x0 = max(0, min(x0, width))
        x1 = max(0, min(x1, width))

        if y1 <= y0 or x1 <= x0:
            return img  # fallback if bounds are invalid for this image size

        return img[y0:y1, x0:x1]

    def _find_board_region(self, img: np.ndarray) -> Tuple[int, int, int, int]:
        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        expected_cell_size = width / self.grid_size
        min_cell_size = expected_cell_size * 0.6
        max_cell_size = expected_cell_size * 1.4

        valid_boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < (min_cell_size ** 2) * 0.5:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            
            # Enforce that cells are roughly square
            aspect_ratio = w / h
            if not (0.75 <= aspect_ratio <= 1.3):
                continue
                
            # Enforce that cells match the expected grid cell sizing,
            # which filters out small non-cell symbols (like x, = or other noise)
            if not (min_cell_size <= w <= max_cell_size) or not (min_cell_size <= h <= max_cell_size):
                continue

            valid_boxes.append((x, y, w, h))

        if not valid_boxes:
            # Fallback to full cropped image if no square cells are detected
            return 0, 0, width, height

        # Find the bounding box that encompasses all valid cell contours
        min_x = min(box[0] for box in valid_boxes)
        min_y = min(box[1] for box in valid_boxes)
        max_x = max(box[0] + box[2] for box in valid_boxes)
        max_y = max(box[1] + box[3] for box in valid_boxes)

        best_box = (min_x, min_y, max_x - min_x, max_y - min_y)
        return best_box

    def _cell_bounds(self, board_box: Tuple[int, int, int, int], row: int, col: int) -> Tuple[int, int, int, int]:
        x, y, w, h = board_box
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size

        x0 = int(x + col * cell_w)
        y0 = int(y + row * cell_h)
        x1 = int(x + (col + 1) * cell_w)
        y1 = int(y + (row + 1) * cell_h)

        pad = self.cell_padding
        x0 += pad
        y0 += pad
        x1 -= pad
        y1 -= pad

        return max(x0, x), max(y0, y), min(x1, x + w), min(y1, y + h)

    def _sample_cell(self, img: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> str:
        if x1 <= x0 or y1 <= y0:
            return "blank"

        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        samples = [
            (cx, cy),
            (x0 + (x1 - x0) // 2 + 15, cy),
            (x1 - (x1 - x0) // 2 + 15, cy),
            (cx + 15, y0 + (y1 - y0) // 2 - 15),
            (cx + 15, y1 - (y1 - y0) // 2 + 15),
        ]
        counts = {"moon": 0, "sun": 0}
        for sx, sy in samples:
            label = self._classify_color(img[sy, sx])
            if label != "blank":
                counts[label] += 1

        if counts["moon"] > counts["sun"]:
            return "moon"
        if counts["sun"] > counts["moon"]:
            return "sun"
        return "blank"

    def _classify_color(self, pixel: np.ndarray) -> str:
        r, g, b = map(int, pixel)
        if (r, g, b) == (255, 255, 255):
            return "blank"
        if self._color_matches((r, g, b), self.moon_color):
            return "moon"
        if self._color_matches((r, g, b), self.sun_color):
            return "sun"
        return "blank"

    def _color_matches(self, pixel_rgb: Tuple[int, int, int], target_rgb: Tuple[int, int, int]) -> bool:
        r, g, b = pixel_rgb
        tr, tg, tb = target_rgb
        return (
            abs(r - tr) <= self.tolerance
            and abs(g - tg) <= self.tolerance
            and abs(b - tb) <= self.tolerance
        )

    def _detect_signs(self, img_rgb: np.ndarray, board_box: Tuple[int, int, int, int]) -> List[dict]:
        x_board, y_board, w_board, h_board = board_box
        cell_size = w_board / self.grid_size

        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 1. Gather candidates: 'x' contours and '=' dash contours
        x_min_sz = 0.08 * cell_size
        x_max_sz = 0.18 * cell_size
        x_min_area = 0.003 * (cell_size ** 2)
        x_max_area = 0.025 * (cell_size ** 2)

        dash_min_w = 0.11 * cell_size
        dash_max_w = 0.23 * cell_size
        dash_min_h = 0.015 * cell_size
        dash_max_h = 0.070 * cell_size
        dash_min_area = 0.0015 * (cell_size ** 2)
        dash_max_area = 0.015 * (cell_size ** 2)

        x_candidates = []
        dash_candidates = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            # Ensure it is reasonably inside or near the board box
            if x < x_board - 5 or y < y_board - 5 or (x + w) > x_board + w_board + 5 or (y + h) > y_board + h_board + 5:
                continue

            cx = x + w / 2.0
            cy = y + h / 2.0
            aspect = w / h if h > 0 else 0

            # Classification based on relative proportions
            if (x_min_sz <= w <= x_max_sz) and (x_min_sz <= h <= x_max_sz) and (0.75 <= aspect <= 1.35) and (x_min_area <= area <= x_max_area):
                x_candidates.append({"center": (cx, cy), "rect": (x, y, w, h)})
            elif (dash_min_w <= w <= dash_max_w) and (dash_min_h <= h <= dash_max_h) and (aspect >= 2.5) and (dash_min_area <= area <= dash_max_area):
                dash_candidates.append({"center": (cx, cy), "rect": (x, y, w, h)})

        # 2. Pair '=' dashes
        equals_centers = []
        used_dashes = set()
        n_dashes = len(dash_candidates)
        dy_min = 0.04 * cell_size
        dy_max = 0.16 * cell_size
        dx_max = 0.06 * cell_size

        for i in range(n_dashes):
            if i in used_dashes:
                continue
            d1 = dash_candidates[i]
            for j in range(i + 1, n_dashes):
                if j in used_dashes:
                    continue
                d2 = dash_candidates[j]
                
                dx = abs(d1["center"][0] - d2["center"][0])
                dy = abs(d1["center"][1] - d2["center"][1])
                
                if dx <= dx_max and dy_min <= dy <= dy_max:
                    used_dashes.add(i)
                    used_dashes.add(j)
                    eq_x = (d1["center"][0] + d2["center"][0]) / 2.0
                    eq_y = (d1["center"][1] + d2["center"][1]) / 2.0
                    equals_centers.append((eq_x, eq_y))
                    break

        # 3. Associate each sign with its nearest cell pair
        cell_centers = []
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                ccx = x_board + (c + 0.5) * cell_size
                ccy = y_board + (r + 0.5) * cell_size
                cell_centers.append((r, c, ccx, ccy))

        def find_associated_cells(sx: float, sy: float) -> List[Tuple[int, int]]:
            dists = []
            for r, c, ccx, ccy in cell_centers:
                dist = np.hypot(sx - ccx, sy - ccy)
                dists.append((dist, (r, c)))
            dists.sort(key=lambda item: item[0])
            cell1 = dists[0][1]
            cell2 = dists[1][1]
            if cell1 > cell2:
                cell1, cell2 = cell2, cell1
            return [cell1, cell2]

        signs = []
        for xc in x_candidates:
            sx, sy = xc["center"]
            cells = find_associated_cells(sx, sy)
            signs.append({
                "type": "x",
                "cells": cells,
                "center": (int(sx), int(sy))
            })

        for ec in equals_centers:
            sx, sy = ec
            cells = find_associated_cells(sx, sy)
            signs.append({
                "type": "=",
                "cells": cells,
                "center": (int(sx), int(sy))
            })

        return signs


if __name__ == "__main__":
    parser = BoardParser()
    result = parser.parse_image("board.png")
    print(result)