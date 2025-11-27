---
## Role of the Scan Path in the Sound

The **scan path** determines the trajectory over an image, directly influencing the generated audio texture. Key considerations are **continuity**, **circularity**, and **loopability**.

### Scan Path Types

1. **Zigzag (Correct Example)**  
   The zigzag path ensures local pixel continuity, with back-and-forth scanning in rows. This avoids perceptual jumps and promotes smoother frequency variations.

   ```
   Zigzag (even rows →, odd rows ←):
   Row 0: → → → → →
   Row 1: ← ← ← ← ←
   Row 2: → → → → →
   Row 3: ← ← ← ← ←
   ```

2. **Raster (for comparison)**  
   Raster scanning introduces jumps between rows, creating discontinuities that can result in more abrupt transitions sonically.

   ```
   Raster:
   → → → → →  ↓
   ← ← ← ← ←  ↓
   → → → → →  ↓
   ```

   **Key Differences:**
   - Zigzag maintains continuity across image rows.
   - Raster introduces stronger discontinuities at row edges.

#### Why Continuity Matters
- **Preserves Pixel Continuity:** Close pixels map to similar frequencies, avoiding abrupt changes.
- **Psychoacoustic Benefits:** Smoother transitions lead to more harmonious textures.
- **Musical Loopability:** Assets created align better with looping aesthetics.

#### Future Scan Path Types
All future scan paths (e.g., spirals, curves) must retain:
- **Continuity:** Avoid large perceptual frequency jumps.
- **Circularity:** Wrap around perfectly.
- **Loopability:** Fit integer cycles for seamless looping.

---

## Multi-Voice Continuous Scanning

In multi-voice setups:
- All voices share the same scan path.
- Each voice begins with a unique **phase** offset and advances with its own **step**.

#### Phase Evolution Over Time
```
t = 0:
Voice1: o----------
Voice2: ----o-------
Voice3: --------o---

t = 1:
Voice1: -o---------
Voice2: -----o------
Voice3: ---------o--

t = 2:
Voice1: --o--------
Voice2: ------o-----
Voice3: ----------o-
```

#### Why Phase Offsets Matter
- **Chorus-Like Width:** By spreading voice phases, the output texture becomes richer and more complex.
- **Thickened Audio Textures:** Independent movement adds dynamic depth.

---

## HSV Mapping Philosophy

#### Philosophy of HSV Mapping

1. **Hue (H):** Maps to **pitch regions** or **octaves**, influencing overall tonal quality.
2. **Saturation (S):** Controls **vibrato depth**, **detune width**, or **modulation intensity**.
3. **Value (V):** Modulates **amplitude** levels, connecting brightness to volume or luminance-based timbral shifts.

#### Dataflow with Annotations
```
(pixel RGB)
      |
      +--> grayscale → gray_scalar  (smooth, luminance-based pitch)
      |
      +--> HSV → (H, S, V)
           |    |     |
           |    |     +--> Amplitude modulation (V-based)
           |    +--------> Vibrato depth (from S)
           +-------------> Pitch region selector (H → frequencies)
```

#### Role of `blend`
- `blend=0.0` → Uses pure HSV data.
- `blend=1.0` → Relies entirely on grayscale.
- `blend=0.5` → Equal contribution, balancing luminance and color impact.

---

## Loopability Section

#### Return-to-Origin Behavior
For perfect looping:
1. **Scan Path Cycles:**
   ```
   Scan Path Length = N

   If num_cycles = 2:
   Cycle 1: 0 → 1 → 2 → … → N-1
   Cycle 2: 0 → 1 → 2 → … → N-1
   Result:
   - First sample == Last sample (numerically identical).
   ```

2. **Voice Phase Alignment:**
   ```
   Voice Phase Progression (mod N):
   Initial Phases:
   v1: 0.0
   v2: 33.3
   v3: 66.6

   After One Cycle:
   v1: 0.0
   v2: 33.3
   v3: 66.6
   ```

3. **Cyclic Alignment Diagram:**
   ```
   Circular Path:
   0 → 1 → 2 → … → N-1
   ^               |
   |————— Seamless Loop —————|
   ```

---

## Distinction Between EngineState vs EngineConfig

#### Configuration vs State
```
EngineConfig (Static):
├─ sample_rate
├─ fmin, fmax
├─ mode
├─ hsv_blend
├─ num_cycles
└─ num_voices

EngineState (Dynamic):
├─ scan_path (fixed at initialization)
├─ voices:
│    ├─ VoiceState.phase (evolves per sample)
│    └─ VoiceState.step  (may become dynamic)
└─ runtime counters (future block state tracking)
```

#### Key Distinction:
- **EngineConfig:** Immutable settings defined at startup.
- **EngineState:** Evolves during runtime, tracking real-time synthesis behavior.

---

## Why This Architecture Enables Real-Time Rendering

This modular design supports real-time audio rendering by:
1. **Block-Based Evolution:**
   - `render_block()` advances voice phases logically.
   - All voices remain continuous between blocks.
2. **Dynamic Tile Selection:**
   - A live GUI can update `scan_path` dynamically without disrupting voice continuity.
3. **Flexible Parameter Updates:**
   - `EngineState` ensures smooth transitions for real-time GUI interaction.
