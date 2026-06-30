from __future__ import annotations

import cv2
import numpy as np
from pathlib import Path
from app.board_parser import BoardParser


def debug_visualize(parser: BoardParser, image_path: str, output_path: str = "debug_output.png") -> None:
    """Visualize all detected regions on the image for debugging."""
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    
    # Pre-crop the image to isolate the board exactly like the parser does
    img_cropped = parser._crop_image(img)
    img_rgb = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB)
    img_display = img_rgb.copy()
    
    # Step 1: Draw detected contours on the cropped canvas
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"[DEBUG] Found {len(contours)} contours")
    
    # Draw all contours in green
    cv2.drawContours(img_display, contours, -1, (0, 255, 0), 2)
    
    # Step 2: Draw the detected board box in blue
    board_box = parser._find_board_region(img_rgb)
    x, y, w, h = board_box
    cv2.rectangle(img_display, (x, y), (x + w, y + h), (255, 0, 0), 3)
    cv2.putText(img_display, f"Board: ({x},{y}) {w}x{h}", (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    print(f"[DEBUG] Board box: ({x}, {y}, {w}, {h})")
    
    # Step 3: Draw cell boundaries and sample points
    for row in range(parser.grid_size):
        for col in range(parser.grid_size):
            x0, y0, x1, y1 = parser._cell_bounds(board_box, row, col)
            
            # Draw cell boundary in red
            cv2.rectangle(img_display, (x0, y0), (x1, y1), (0, 0, 255), 1)
            
            # Draw sample points in yellow (center and offsets)
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            samples = [
                (cx, cy),
                (x0 + (x1 - x0) // 2 + 15, cy),
                (x1 - (x1 - x0) // 2 + 15, cy),
                (cx + 15, y0 + (y1 - y0) // 2 - 15),
                (cx + 15, y1 - (y1 - y0) // 2 + 15),
            ]
            
            for sx, sy in samples:
                cv2.circle(img_display, (sx, sy), 3, (0, 255, 255), -1)
            
            # Label the cell with its detected value
            cell_value = parser._sample_cell(img_rgb, x0, y0, x1, y1)
            color_text = (0, 255, 0) if cell_value == "moon" else (0, 165, 255) if cell_value == "sun" else (200, 200, 200)
            cv2.putText(img_display, cell_value, (x0 + 5, y0 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_text, 1)

    # Step 4: Draw detected signs
    parsed_res = parser.parse_image(image_path)
    for sign in parsed_res["signs"]:
        type_ = sign["type"]
        sx, sy = sign["center"]
        # Draw sign center
        cv2.circle(img_display, (sx, sy), 5, (255, 0, 255), -1)
        # Draw text label showing sign type and adjacent cells index
        cv2.putText(img_display, f"'{type_}' {sign['cells']}", (sx - 30, sy - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
    
    # Convert back to BGR for saving
    img_display_bgr = cv2.cvtColor(img_display, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, img_display_bgr)
    print(f"[DEBUG] Visualization saved to {output_path}")


if __name__ == "__main__":
    parser = BoardParser()
    result = parser.parse_image("board.png")
    print("Parsed board:")
    for row in result["board"]:
        print(row)
    print("\nParsed signs:")
    for sign in result["signs"]:
        print(sign)
    
    # Visual debugging
    debug_visualize(parser, "board.png", "board_debug.png")