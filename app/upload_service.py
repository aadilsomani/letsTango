from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from app.board_parser import BoardParser


class UploadService:
    def __init__(self, parser: BoardParser | None = None) -> None:
        self.parser = parser or BoardParser()

    def parse_uploaded_file(self, file_bytes: bytes, file_name: str) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile(suffix=Path(file_name).suffix or ".png", delete=False) as tmp:
            tmp.write(file_bytes)
            temp_path = Path(tmp.name)

        try:
            parsed = self.parser.parse_image(temp_path)
            return {
                "board": parsed["board"],
                "signs": parsed["signs"],
                "grid_size": len(parsed["board"])
            }
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    service = UploadService()
    example = service.parse_uploaded_file(b"", "example.png")
    print(json.dumps(example, indent=2))
