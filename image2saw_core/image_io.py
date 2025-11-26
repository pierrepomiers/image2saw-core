"""
image_io.py: Handle image loading and treat the full image as a single "tile."
"""

import numpy as np
from PIL import Image


def load_image(path: str) -> np.ndarray:
    """
    Load an image file from the given path and return it as a NumPy array.
    Image dimensions: (height, width, channels), normalized to [0–1].
    """
    img = Image.open(path).convert("RGB")
    arr = np.array(img, dtype=np.float32) / 255.0
    return arr


def full_image_tile(image: np.ndarray) -> dict:
    """
    Treat the full image as the "tile."
    Returns a dictionary with tile dimensions and pixel data:
    { 'data': np.ndarray, 'width': int, 'height': int }
    """
    height, width = image.shape[:2]
    return {
        "data": image,
        "width": width,
        "height": height,
    }
