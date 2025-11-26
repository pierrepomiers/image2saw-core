"""
mapping.py: Implement pixel → scalar mapping and blending for grayscale/HSV modes.
"""

import numpy as np


def pixel_to_scalar_gray(pixel: np.ndarray) -> float:
    """
    Map a pixel to a grayscale scalar in the range [0, 1] based on luminance.
    Uses standard luminance weights for RGB: 0.2126*R + 0.7152*G + 0.0722*B
    """
    r, g, b = pixel[0], pixel[1], pixel[2]
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return float(np.clip(luminance, 0.0, 1.0))


def pixel_to_scalar_hsv(pixel: np.ndarray) -> float:
    """
    Map a pixel to an HSV-based scalar in the range [0, 1].
    Uses the Value (brightness) component from HSV color space.
    """
    r, g, b = pixel[0], pixel[1], pixel[2]
    # Value is the maximum of R, G, B
    value = max(r, g, b)
    return float(np.clip(value, 0.0, 1.0))


def scalar_to_frequency(value: float, fmin: float, fmax: float) -> float:
    """
    Map a scalar value [0, 1] to a frequency between fmin and fmax.
    """
    return fmin + value * (fmax - fmin)


def blend_gray_hsv(gray_val: float, hsv_val: float, blend: float) -> float:
    """
    Blend grayscale and HSV scalars based on the blend factor (0.0–1.0).
    blend=0.0 means full grayscale, blend=1.0 means full HSV.
    """
    blend = float(np.clip(blend, 0.0, 1.0))
    return (1.0 - blend) * gray_val + blend * hsv_val
