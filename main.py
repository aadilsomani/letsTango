from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List
import cv2
import numpy as np

from app.board_parser import BoardParser 
from app.board_solver import BoardSolver  # Import your solver

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Define what the incoming request data should look like for solving
class BoardSolveRequest(BaseModel):
    board: List[Any]  # Adjust types if they are specifically List[List[int]] etc.
    signs: List[Any]

# --- Endpoint 1: Parse the Image ---
@app.post("/parse-board")
async def parse_board(file: UploadFile = File(...)) -> dict[str, Any]:
    try:
        file_bytes = await file.read()
        np_array = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file.")

        parser = BoardParser()
        parsed = parser.parse_image(image) 
        
        return {
            "board": parsed["board"],
            "signs": parsed["signs"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint 2: Solve the Board ---
@app.post("/solve-board")
async def solve_board(data: BoardSolveRequest) -> dict[str, Any]:
    try:
        solver = BoardSolver(board=data.board, signs=data.signs)
        
        # Assuming solver.solve() now returns the dict with board, solved, and steps
        result = solver.solve() 
        
        return {
            "status": "success",
            "board": result["board"],
            "solved": result["solved"],
            "steps": result["steps"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)