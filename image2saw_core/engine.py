"""
engine.py: Handle engine state/configuration and render audio buffers.

v0.2:
- Vectorized rendering of a single tile cycle (NumPy).
- Multiple voices, dephased on the scan-path and in oscillator phase.
- Internal loop crossfade on the single cycle, then tiling for num_cycles.
"""

from dataclasses import dataclass
from typing import List
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
    """
    Static configuration of the engine.

    sample_rate       : audio sample rate in Hz.
    num_voices        : number of parallel voices.
    fmin / fmax       : frequency mapping range.
    mode              : "grayscale" or "hsv".
    hsv_blend         : blend factor used in custom modes (0.0–1.0).
    num_cycles        : how many times to repeat the tile cycle.
    loop_crossfade_ms : duration of internal loop crossfade on the single cycle.
    """
    sample_rate: int
    num_voices: int
    fmin: float
    fmax: float
    mode: str
    hsv_blend: float
    num_cycles: int
    loop_crossfade_ms: float = 10.0


@dataclass
class VoiceState:
    """
    Runtime state for a single voice.

    phase     : position along the scan-path index space (0..path_length).
    step      : phase increment per audio sample along the scan-path.
    osc_phase : phase of the audio oscillator in [0,1) for this voice.
    """
    phase: float
    step: float
    osc_phase: float = 0.0


@dataclass
class EngineState:
    """
    Bundles configuration, scan path, tile data and voices.
    """
    config: EngineConfig
    scan_path: np.ndarray          # (N, 2) array of (y, x)
    voices: List[VoiceState]
    tile_data: np.ndarray          # (H, W, 3) float32 RGB [0,1]


def init_engine_state(tile: dict, config: EngineConfig) -> EngineState:
    """
    Initialize the engine state from a Tile-like dict:
    { "data": np.ndarray(H,W,3), "width": int, "height": int }.

    - Build zigzag scan_path over the full tile.
    - Spread voices evenly along the scan-path.
    - Dephase oscillator phases across voices.
    """
    width = tile["width"]
    height = tile["height"]
    tile_data = tile["data"]

    scan_path = build_scan_path(width, height, pattern="zigzag")
    path_length = len(scan_path)

    num_voices = max(1, config.num_voices)
    voices: List[VoiceState] = []

    for v in range(num_voices):
        # Phase along the path: spread voices around the tile
        phase = (path_length * v) / num_voices
        step = 1.0  # 1 pixel (scan index) per audio sample in v0.2

        # Oscillator initial phase: spread in [0,1) to avoid all voices in phase
        osc_phase = (v / num_voices) % 1.0

        voices.append(VoiceState(phase=phase, step=step, osc_phase=osc_phase))

    return EngineState(
        config=config,
        scan_path=scan_path,
        voices=voices,
        tile_data=tile_data,
    )


# ---------------------------------------------------------------------
# Vectorized helpers
# ---------------------------------------------------------------------


def _render_single_cycle_vectorized(
    config: EngineConfig,
    scan_path: np.ndarray,
    tile_data: np.ndarray,
    voice_phases: np.ndarray,
    voice_steps: np.ndarray,
    osc_initial_phases: np.ndarray,
) -> np.ndarray:
    """
    Generate a single cycle (length == len(scan_path)) of mixed audio using
    fully vectorized NumPy operations.

    Parameters:
        config             : EngineConfig
        scan_path          : (L, 2) int array of (y, x)
        tile_data          : (H, W, 3) float32, RGB in [0,1]
        voice_phases       : (V,) array of starting phases along the path (can be fractional)
        voice_steps        : (V,) array of step-per-sample values
        osc_initial_phases : (V,) array of initial oscillator phases in [0,1)

    Returns:
        single_cycle : (L,) float32 mono buffer (one tile cycle)
    """
    path_length = len(scan_path)
    if path_length == 0:
        return np.zeros(0, dtype=np.float32)

    num_voices = int(config.num_voices)
    sample_rate = float(config.sample_rate)
    fmin, fmax = float(config.fmin), float(config.fmax)

    # Sample indices for one cycle: s = 0 .. L-1
    s = np.arange(path_length, dtype=np.float64)  # (L,)

    # Broadcast phases/steps to (V, L):
    voice_phases = np.asarray(voice_phases, dtype=np.float64)  # (V,)
    voice_steps = np.asarray(voice_steps, dtype=np.float64)    # (V,)

    # phase_matrix[v, s] = voice_phases[v] + s * voice_steps[v]
    phase_matrix = voice_phases[:, None] + voice_steps[:, None] * s[None, :]  # (V, L)
    path_idx = np.floor(phase_matrix).astype(np.int64) % path_length          # (V, L)

    # Lookup scan_path coordinates per voice/sample
    coords = scan_path[path_idx]  # (V, L, 2)
    ys = coords[..., 0]
    xs = coords[..., 1]

    # Gather pixel values for all voices and samples: pixels shape (V, L, 3)
    pixels = tile_data[ys, xs]  # (V, L, 3)
    r = pixels[..., 0]
    g = pixels[..., 1]
    b = pixels[..., 2]

    # ---- Pixel -> scalar mapping (vectorized) ----
    # Grayscale luminance (approx) in [0,1]
    gray_val = 0.2126 * r + 0.7152 * g + 0.0722 * b
    gray_val = np.clip(gray_val, 0.0, 1.0)

    # HSV-like value: use max channel as simple V substitute
    hsv_val = np.maximum(np.maximum(r, g), b)
    hsv_val = np.clip(hsv_val, 0.0, 1.0)

    if config.mode == "grayscale":
        scalar = gray_val
    elif config.mode == "hsv":
        # Simple blend between gray and "V" based on hsv_blend
        blend = float(np.clip(config.hsv_blend, 0.0, 1.0))
        scalar = (1.0 - blend) * gray_val + blend * hsv_val
    else:
        # Fallback: use full blend helper on per-voice basis if needed
        # For now, approximate with gray_val.
        scalar = gray_val

    # ---- Scalar -> frequency (vectorized) ----
    freq_cycle = fmin + scalar * (fmax - fmin)  # (V, L)

    # ---- Build oscillator phases per voice/sample ----
    # increments[v, s] = freq_cycle[v, s] / sample_rate
    increments = freq_cycle / sample_rate  # (V, L)
    cumsum_incr = np.cumsum(increments, axis=1)  # (V, L)

    # We want osc_phase[v, s] = osc_initial_phases[v] + sum_{t=0..s-1} increments[v, t]
    # So we shift the cumsum by one and insert 0 at the start.
    cumsum_shifted = np.concatenate(
        (
            np.zeros((num_voices, 1), dtype=np.float64),
            cumsum_incr[:, :-1],
        ),
        axis=1,
    )  # (V, L)

    osc_initial_phases = np.asarray(osc_initial_phases, dtype=np.float64)  # (V,)
    osc_phase_matrix = (osc_initial_phases[:, None] + cumsum_shifted) % 1.0  # (V, L)

    # ---- Generate sawtooth waveform (vectorized) ----
    osc_samples = 2.0 * osc_phase_matrix - 1.0  # (V, L) in [-1,1]

    # ---- Mix voices ----
    mixed = np.sum(osc_samples, axis=0) / float(num_voices)  # (L,)

    return mixed.astype(np.float32)


def _apply_internal_loop_crossfade(single_cycle: np.ndarray, sample_rate: int, loop_crossfade_ms: float) -> np.ndarray:
    """
    Apply an internal loop crossfade between the LAST samples and the FIRST samples
    of the given single_cycle buffer.

    This is applied on the single cycle so that it can be tiled num_cycles times
    without creating hard discontinuities.

    If loop_crossfade_ms <= 0, this is a no-op.
    """
    if loop_crossfade_ms <= 0.0:
        return single_cycle

    length = single_cycle.shape[0]
    fade_samples = int(sample_rate * loop_crossfade_ms / 1000.0)

    if fade_samples <= 0 or fade_samples * 2 >= length:
        return single_cycle

    out = single_cycle.copy()

    fade_out = np.linspace(1.0, 0.0, fade_samples, endpoint=False, dtype=np.float32)
    fade_in = np.linspace(0.0, 1.0, fade_samples, endpoint=False, dtype=np.float32)

    tail = out[-fade_samples:].copy()
    head = out[:fade_samples].copy()

    blended = tail * fade_out + head * fade_in

    out[-fade_samples:] = blended
    out[:fade_samples] = blended

    return out


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def render_buffer(engine_state: EngineState) -> np.ndarray:
    """
    Render the FULL mono buffer according to engine_state.config.num_cycles.

    Strategy v0.2:
    - Render a SINGLE tile cycle (one pass on the scan path) using vectorized ops.
    - Apply an internal loop crossfade on that cycle (config.loop_crossfade_ms).
    - Repeat that cycle num_cycles times (simple tiling).
    - Update voice.phase to reflect advancement (osc_phase is not persisted yet).
    """
    config = engine_state.config
    scan_path = engine_state.scan_path
    tile_data = engine_state.tile_data
    voices = engine_state.voices

    path_length = len(scan_path)
    if path_length == 0 or config.num_cycles <= 0:
        return np.zeros(0, dtype=np.float32)

    num_voices = max(1, config.num_voices)
    num_samples = path_length * config.num_cycles

    # Vectorized views of voice states
    voice_phases = np.array([v.phase for v in voices], dtype=np.float64)   # (V,)
    voice_steps = np.array([v.step for v in voices], dtype=np.float64)     # (V,)
    osc_initial_phases = np.array([v.osc_phase for v in voices], dtype=np.float64)  # (V,)

    # 1) Generate single cycle
    single_cycle = _render_single_cycle_vectorized(
        config=config,
        scan_path=scan_path,
        tile_data=tile_data,
        voice_phases=voice_phases,
        voice_steps=voice_steps,
        osc_initial_phases=osc_initial_phases,
    )  # (path_length,)

    # 2) Make the cycle loop-friendly
    single_cycle = _apply_internal_loop_crossfade(
        single_cycle,
        sample_rate=config.sample_rate,
        loop_crossfade_ms=config.loop_crossfade_ms,
    )

    # 3) Tile the cycle num_cycles times
    buffer = np.tile(single_cycle, config.num_cycles).astype(np.float32)

    # 4) Update voice.phase (so if we render again, scan continues correctly)
    total_advances = num_samples * voice_steps  # (V,)
    new_phases = (voice_phases + total_advances) % path_length
    for i, v in enumerate(voices):
        v.phase = float(new_phases[i])

    return buffer

