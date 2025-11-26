"""
engine.py: Handle engine state/configuration and render audio buffers.
"""

from dataclasses import dataclass
import numpy as np

from .scan import build_scan_path
from .mapping import (
    pixel_to_scalar_gray,
    pixel_to_scalar_hsv,
    scalar_to_frequency,
    blend_gray_hsv,
)


@dataclass
class EngineConfig:
    sample_rate: int         # e.g., 44100
    num_voices: int          # Number of voices to mix
    fmin: float              # Minimum frequency of mapping
    fmax: float              # Maximum frequency of mapping
    mode: str                # "grayscale" or "hsv"
    hsv_blend: float         # Blend between HSV/Grayscale (0.0–1.0)
    num_cycles: int          # Number of scan-path cycles


@dataclass
class VoiceState:
    phase: float             # Current scan-path phase
    step: float              # Phase step per sample


@dataclass
class EngineState:
    config: EngineConfig
    scan_path: np.ndarray    # (N, 2) array of scan-path indices
    voices: list
    tile_data: np.ndarray    # The image tile data


def init_engine_state(tile: dict, config: EngineConfig) -> EngineState:
    """
    Initialize the engine state.
    - Build a scan path from the tile.
    - Spread voice phases (evenly distributed along the path).
    """
    scan_path = build_scan_path(tile["width"], tile["height"], pattern="zigzag")
    path_length = len(scan_path)
    
    # Spread voice phases evenly along the path
    voices = []
    for i in range(config.num_voices):
        phase = (i / config.num_voices) * path_length
        step = 1.0  # Default step: 1 pixel per sample
        voices.append(VoiceState(phase=phase, step=step))
    
    return EngineState(
        config=config,
        scan_path=scan_path,
        voices=voices,
        tile_data=tile["data"],
    )


def render_buffer(engine_state: EngineState) -> np.ndarray:
    """
    Render a mono buffer of audio samples based on the engine state.
    - For each sample:
        - Advance each voice along the scan path.
        - Map pixel value to frequency → waveform sample.
        - Mix all voice samples together.
    - Number of samples = num_cycles * path_length.
    Returns: np.ndarray of rendered audio samples.
    """
    config = engine_state.config
    scan_path = engine_state.scan_path
    tile_data = engine_state.tile_data
    voices = engine_state.voices
    
    path_length = len(scan_path)
    num_samples = config.num_cycles * path_length
    
    # Pre-allocate output buffer
    buffer = np.zeros(num_samples, dtype=np.float32)
    
    # Track oscillator phases for each voice (for waveform generation)
    osc_phases = [0.0] * config.num_voices
    
    for sample_idx in range(num_samples):
        sample_sum = 0.0
        
        for voice_idx, voice in enumerate(voices):
            # Get current position in scan path (with wrapping)
            path_idx = int(voice.phase) % path_length
            y, x = scan_path[path_idx]
            
            # Get pixel value at current position
            pixel = tile_data[y, x]
            
            # Map pixel to scalar based on mode
            if config.mode == "hsv":
                gray_val = pixel_to_scalar_gray(pixel)
                hsv_val = pixel_to_scalar_hsv(pixel)
                scalar = blend_gray_hsv(gray_val, hsv_val, config.hsv_blend)
            else:
                # grayscale mode
                scalar = pixel_to_scalar_gray(pixel)
            
            # Map scalar to frequency
            freq = scalar_to_frequency(scalar, config.fmin, config.fmax)
            
            # Generate sawtooth waveform sample
            # Sawtooth: phase goes from 0 to 1, output goes from -1 to 1
            osc_sample = 2.0 * osc_phases[voice_idx] - 1.0
            sample_sum += osc_sample
            
            # Advance oscillator phase
            phase_increment = freq / config.sample_rate
            osc_phases[voice_idx] = (osc_phases[voice_idx] + phase_increment) % 1.0
            
            # Advance voice along scan path
            voice.phase = (voice.phase + voice.step) % path_length
        
        # Mix all voices (normalize by number of voices)
        buffer[sample_idx] = sample_sum / config.num_voices
    
    return buffer
