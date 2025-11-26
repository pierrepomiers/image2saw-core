#!/usr/bin/env python3
"""
image2saw_cli.py: A simple CLI interface for the image2saw core engine.
"""

import argparse
import numpy as np
from scipy.io import wavfile

from image2saw_core.image_io import load_image, full_image_tile
from image2saw_core.engine import EngineConfig, init_engine_state, render_buffer

# Maximum value for 16-bit signed integer audio
INT16_MAX = 32767


def main():
    parser = argparse.ArgumentParser(description="image2saw Audio Generation")
    parser.add_argument("--input", required=True, type=str, help="Input image file.")
    parser.add_argument("--output", required=True, type=str, help="Output WAV file.")
    parser.add_argument("--sample-rate", type=int, default=44100, help="Sample rate.")
    parser.add_argument("--mode", choices=["grayscale", "hsv"], default="grayscale")
    parser.add_argument("--hsv-blend", type=float, default=0.0, help="Blend (0–1).")
    parser.add_argument("--fmin", type=float, default=200.0, help="Minimum freq.")
    parser.add_argument("--fmax", type=float, default=1000.0, help="Maximum freq.")
    parser.add_argument("--num-voices", type=int, default=4, help="Number of voices.")
    parser.add_argument("--num-cycles", type=int, default=5, help="Tile scan cycles.")
    args = parser.parse_args()

    # Load image and treat as a tile
    image = load_image(args.input)
    tile = full_image_tile(image)

    # Configure engine
    config = EngineConfig(
        sample_rate=args.sample_rate,
        num_voices=args.num_voices,
        fmin=args.fmin,
        fmax=args.fmax,
        mode=args.mode,
        hsv_blend=args.hsv_blend,
        num_cycles=args.num_cycles,
    )
    engine_state = init_engine_state(tile, config)

    # Render audio buffer
    buffer = render_buffer(engine_state)

    # Convert to 16-bit integer format for WAV
    # Scale from [-1, 1] to [-INT16_MAX, INT16_MAX]
    buffer_int16 = np.clip(buffer * INT16_MAX, -INT16_MAX, INT16_MAX).astype(np.int16)

    # Save as WAV file
    wavfile.write(args.output, args.sample_rate, buffer_int16)
    print(f"Audio saved to {args.output}")


if __name__ == "__main__":
    main()
