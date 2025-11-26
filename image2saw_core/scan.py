"""
scan.py: Generate a continuous scan path (e.g., zigzag/raster) over the tile.
"""

import numpy as np


def build_scan_path(width: int, height: int, pattern: str = "zigzag") -> np.ndarray:
    """
    Generate a scan path (e.g., raster or zigzag pattern) over the tile.
    Args:
        width: Tile width.
        height: Tile height.
        pattern: "zigzag" (default) or "raster."
    Returns a 2D array of pixel coordinates: np.ndarray[(N, 2)].
    Path is considered circular (continuous wrapping).
    """
    coords = []
    for y in range(height):
        if pattern == "zigzag" and y % 2 == 1:
            # Odd rows: right to left
            for x in range(width - 1, -1, -1):
                coords.append([y, x])
        else:
            # Even rows (or raster pattern): left to right
            for x in range(width):
                coords.append([y, x])
    return np.array(coords, dtype=np.int32)
