# image2saw-core

# 🔊 image2saw – v0 Core (Minimal Audio Engine)

---

## 🏗️ Project Overview

**image2saw** is an experimental tool that transforms static images into loopable audio textures, bridging the gap between visual art and sound design. By scanning image tiles pixel by pixel, it generates unique, harmonic, and loopable audio outputs. The generated textures offer creative possibilities for:

- Experimental musicians
- Sound designers
- Digital artists
- Researchers exploring the relationships between images and audio

### ✨ Philosophy Behind v0 Core

This **v0 minimal reboot** focuses on a clean, efficient, and highly readable codebase. It re-centers the project on its foundational audio-only functionality to provide a robust platform for future features. While tools for live playback, GUI interfaces, and additional image manipulation are planned for later versions, the purpose of v0 is to demonstrate the simplest core functionality with **deterministic, loopable results.**

---

## ⚡ Key Features of v0 Core

The v0 core includes the following essential features:

- **Audio-only pipeline:** Focused on efficient WAV generation.
- **Full-image processing:** Each image is treated as a single tile.
- **Circular scanning paths:** Ensures seamless looping.
- **Multi-voice synthesis:** Independent phase and step for each voice.
- **Flexible color mappings:** Supports Grayscale and HSV modes with blending options.
- **Loopable WAV output:** Integer scan-path cycles ensure zero clicks or pops.
- **Simple CLI:** Straightforward command-line interface for rendering.

---

## 🧩 Architecture Overview

image2saw v0 operates through the following modular pipeline:

```
Image → Tile → Scan Path → Pixel → Scalar → Frequency → Synth → Loopable WAV
```

### 📂 Module Breakdown

| Module            | Role                                                                                   |
|--------------------|----------------------------------------------------------------------------------------|
| **`image_io.py`** | Handles image loading (via Pillow), normalization, and tile extraction.                |
| **`scan.py`**     | Manages path generation (circular/raster), treated as seamless loops.                  |
| **`mapping.py`**  | Converts pixel data to scalar values and maps them to frequencies. Handles blending.   |
| **`engine.py`**   | Controls synthesis parameters, engine configuration, and audio rendering.             |
| **`image2saw_cli.py`** | Provides a minimal command-line interface for configuring and triggering rendering.| 

---

## 🔄 How Loopability Works

One of the core principles of image2saw is ensuring seamless looping in any environment. Here’s how it achieves this:

1. **Circular Scan Paths**  
   Each pixel scan follows a circular path. When the end of the path is reached, it wraps around cleanly to the beginning (modulo operation).

2. **Integer Cycles**  
   By rendering an **integer number of scan-path cycles**, the audio ends precisely where it started, enabling perfect looping.

3. **Even Voice Phases**  
   Voices in the engine are evenly spaced in phase, ensuring harmonious playback across multiple voices.

4. **Sample-Accurate Output**  
   The system uses deterministic calculations to ensure no drift or unexpected artifacts in the waveform.

_Planned improvements for seamlessness include: higher resolution scanning, crossfades between phases, and nonlinear paths._

---

## 📥 Installation

### Prerequisites
Ensure the following dependencies are installed:

- **Python**: Version 3.10 or newer
- **Libraries**: `numpy`, `pillow`

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/pierrepomiers/image2saw-core.git
   cd image2saw-core
   ```

2. Install the required Python packages:
   ```bash
   pip install numpy pillow
   ```

3. You’re ready!

---

## 🖥️ Usage

Access the engine via the command-line interface:

### Example Command
```bash
python image2saw_cli.py \
  --input myimage.png \
  --output tile.wav \
  --mode hsv \
  --hsv-blend 0.2 \
  --num-voices 6 \
  --num-cycles 8
```

### CLI Arguments

| Argument             | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| **`--input`**        | Input image path (e.g., `myimage.png`).                                    |
| **`--output`**       | Output WAV file path (e.g., `result.wav`).                                 |
| **`--sample-rate`**  | Sampling rate for the output (e.g., 44100).                                |
| **`--mode`**         | Color mapping mode: `grayscale` (default) or `hsv`.                       |
| **`--hsv-blend`**    | Blending strength for HSV mode (0 to 1, default: 0).                      |
| **`--fmin`**         | Minimum frequency for generated pitches (e.g., 120 Hz).                   |
| **`--fmax`**         | Maximum frequency for generated pitches (e.g., 1200 Hz).                  |
| **`--num-voices`**   | Number of simultaneous voices (default: 4).                               |
| **`--num-cycles`**   | Number of full scan cycles (default: 4).                                   |

---

## 🚀 How to Extend the Engine

Future extensions could include:

1. **Interactive GUIs:** PySide6-based desktop tools for live playback and visual modulation.
2. **Advanced Tile Selection:** Break larger images into smaller tiles (e.g., 4x4, 8x8 grids).
3. **Custom Scan Patterns:** Beyond circular paths—explore spirals, Bezier paths, random walks, etc.
4. **Artist Presets:** Provide harmonically rich mappings and preconfigured styles.
5. **Plugin Versions:** Integration as VST or LV2 for live DAW workflows.

---

## 🎯 Design Goals

From the ground up, image2saw v0 emphasizes:

- **Simplicity:** A minimal yet powerful engine.
- **Determinism:** Predictable, repeatable outputs.
- **Pure Functions:** Modular design with minimal state-side effects.
- **Modularity:** Clear separation for future extension in real-time use cases.
- **Lightweight Dependencies:** Focused on core Python libraries.

---

## 📜 License + Credits

### License
This project currently uses a placeholder license. Please check for future license updates before redistribution.

### Credits
image2saw was designed for experimental musicians and digital artists, drawing inspiration from early research on image sonification and creative misuse of computer vision for sound design.
