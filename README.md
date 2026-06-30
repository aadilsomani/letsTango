# Tango board parser prototype

This workspace contains a small Python prototype for turning a screenshot of a Tango board into a 2D grid of labels.

## Current capabilities
- Upload a screenshot and parse it into a grid of `moon`, `sun`, or `blank` values.
- Use simple color matching for the two token types.
- Keep the parser isolated so it can later be exposed through a Cloudflare Worker or a small web app.

## Files
- [app/board_parser.py](app/board_parser.py): image-to-grid parser.
- [app/upload_service.py](app/upload_service.py): helper that accepts uploaded bytes and returns parsed board data.
- [tests/test_board_parser.py](tests/test_board_parser.py): simple regression test for a synthetic board.

## Next steps
1. Add a small Flask or FastAPI endpoint for image upload.
2. Detect the board region more accurately from real screenshots.
3. Extend the parser to identify `x` and `=` markers as separate tokens.
