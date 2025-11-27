# ARCHITECTURE.md

## High-level Architecture Overview

The image2saw core v0 pipeline transforms image tiles into loopable audio textures using pixel-based frequency mapping. The flow data is as follows:

```
image file → image array → tile → scan path → engine → audio buffer → WAV
```

### ASCII Block Diagram

```
image2saw_cli.py
        |
        v
  image_io.load_image
        |
        v
  image_io.full_image_tile --> scan.build_scan_path
               |                      |
               v                      v
        scan_path             engine.init_engine_state
                                     |
                           engine.render_buffer
                                     |
                           writes to WAV output
```

## Module-by-Module Description

### `image_io.py`
- **Responsibility:** Load and process images, normalize pixel values, handle tile division.
- **Main Functions:**
  - `load_image(file_path)`: Loads image via Pillow and converts to NumPy array.
  - `full_image_tile(image_array)`: Treats the entire image as a single tile.
- **Consumes:** Image file paths.
- **Produces:** Numpy arrays of shape `(height, width, channels)`.

### `scan.py`
- **Responsibility:** Generate and manage scan paths for image traversal.
- **Main Functions:**
  - `build_scan_path(tile)`: Creates a raster path (treated as circular).
- **Consumes:** Image tiles.
- **Produces:** Arrays of coordinates `[(y0, x0), (y1, x1), ...]`.

### `mapping.py`
- **Responsibility:** Map pixel values to audio parameters.
- **Main Functions:**
  - `pixel_to_scalar_gray(pixel)`: Converts grayscale pixels to scalar values.
  - `pixel_to_scalar_hsv(pixel)` and `blend_gray_hsv(...)`.
  - `scalar_to_frequency(value, fmin, fmax)`: Maps normalized scalars to frequencies.
- **Consumes:** Pixel values.
- **Produces:** Scalar values or frequencies.

### `engine.py`
- **Responsibility:** Synthesizes audio from scan paths and pixel mappings.
- **Main Functions:**
  - `EngineConfig`: Configuration (number of voices, sample rate, etc.).
  - `VoiceState`: Holds `phase` and `step` per voice.
  - `EngineState`: Tracks engine runtime state (scan path + voices).
  - `render_buffer(state)`: Produces audio buffers via iterative synthesis.
- **Consumes:** Scan paths, scalar values.
- **Produces:** Audio buffers (NumPy arrays).

### `image2saw_cli.py`
- **Responsibility:** Manages the command-line interface.
- **Main Functions:**
  - Parses arguments (`argparse`).
  - Uses other modules to coordinate rendering.
- **Consumes:** Input arguments, image files.
- **Produces:** Audio WAV files.

---

## Data Structures and Types

### Tile Representation
- **Shape:** `(height, width, channels)`.
- **Value Ranges:** Grayscale (`0–255`), HSV (`0–1`).

### Scan Path Array
- **Shape:** `(N, 2)`.
- **Coordinates:** `(y, x)` array.

### Engine Data Structures
```
EngineState
├─ config: EngineConfig
├─ scan_path: [(y0,x0), (y1,x1), ...]
└─ voices:
   ├─ VoiceState(phase=..., step=...)
   ├─ VoiceState(phase=..., step=...)
   └─ ...
```

---

## Flow of a Typical Render

1. Parse CLI arguments.
2. Load image.
3. Build tile (entire image).
4. Generate scan path.
5. Initialize engine state.
6. Render audio buffer via `render_buffer`.
7. Export as WAV file.

### Sequence Diagram

```
image2saw_cli.py          image_io            scan           engine
       |                    |                  |               |
       |-- load_image() --> |                  |               |
       |                    |-- np.ndarray --> |               |
       |                    |                  |               |
       |-- full_image_tile()-----------------> |               |
       |                    |                  |               |
       |--------------------- build_scan_path() -------------> |
       |                                                       |
       |------------------------ init_engine_state() --------> |
       |                                                       |
       |------------------------- render_buffer() -----------> |
       |                                                       |
       |---------------------------- write_wav() -------------|
```

---

## Circular Scanning and Loopability

The scan path is treated as circular:
```
Scan indices:
   0 → 1 → 2 → ... → N-2 → N-1
   ^                       |
   |_______________________|

Voice phase:
   phase = (phase + step) % N
```

### `num_cycles`
Defines total sample output:
```samples = num_cycles × len(scan_path) × samples_per_step```

---

## Grayscale / HSV Mapping and Blend

Mapping flow:
```
pixel (R,G,B)
     |
     +--> grayscale → gray_scalar
     |
     +--> HSV ------→ hsv_scalar

gray_scalar, hsv_scalar
     |
     +--> blend_gray_hsv(...) → value [0,1]
                          |
                          v
                   scalar_to_frequency(...)
                          |
                          v
                       frequency (Hz)
```

---

## Future Extension Points

- **Tile Selection:** Sub-regions of a larger image.
- **Additional Scan Patterns:** Spirals or user-defined paths.
- **Real-time Rendering:** Audio blocks for live playback.
- **GUI Integration:** Leverage PySide6 for usability.
