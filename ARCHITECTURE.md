## Role of the Scan Path in the Sound

The scan path is crucial in shaping the output sound by defining how audio data is accessed and processed. Here, we describe three types of scan paths:

### Zigzag
The zigzag scan path moves diagonally back and forth, allowing for smooth transitions between points.  

```
Zigzag:
→ → → → ↙ → → → → ↙
```

### Raster
In contrast, the raster scan path operates horizontally, line by line:

```
Raster:
→ → → → -
← ← ← ← -
```

### Future Path Types
We anticipate developing future path types that may combine features of zigzag and raster scans for optimized sound processing.


## Multi-Voice Continuous Scanning

In this system, all voices utilize the same scan path but differ in their phase and step:

```
Voice 1 phase: o----------  
Voice 2 phase: ----o-------  
Voice 3 phase: --------o---  
```

This multi-voice approach allows for a richer auditory experience, as different voices contribute varied elements to the overall sound.

## HSV Mapping Philosophy

HSV mapping plays a significant role in shaping the audio output:
- **Hue** refers to the frequency selection, affecting tonal changes.
- **Saturation** controls modulation, influencing vibrancy.
- **Value** corresponds to amplitude, determining loudness.

Additionally, the blend parameter facilitates smooth transitions between mappings.

## Loopability Section

The system incorporates loopability through:
- `num_cycles × path_length` ensures endings align correctly for seamless playback.

Examples of engine phases/synchrony:
```
Engine Phases:
| Voice 1 | Voice 2 | Voice 3 |
|----------|----------|----------|
| Phase 1 | Phase 1 | Phase 1 |
| Phase 2 | Phase 2 | Phase 2 |
```

All voices loop back precisely, maintaining harmony throughout.

## Future PySide6 Integration

Future integration will streamline GUI interactions, particularly concerning:
- Tile selection methods for better user input  
- Live real-time rendering blocks to enhance the interface
- Maintaining `EngineState` for live playback and re-rendering, allowing for dynamic adjustments during operation.

## Distinction Between EngineState and EngineConfig

It is vital to distinguish between static configurations versus evolving runtime states. 

- **EngineState** refers to the current conditions and status during operation.
- **EngineConfig** is the static setup that remains consistent unless explicitly changed. 

Mapping future GUI connections will be essential for maintaining rendering continuity across different states.

## Optional Render Blocks Sequences

Examples of render block sequences:
```
[Block 1] Voice phase = 0.0 → 52.3  
[Block 2] Voice phase = 52.3 → 104.7  
[Block 3] Voice phase = 104.7 → 157.1 → wraps → 5.1  
```
These optional sequences allow for flexible audio manipulation and creative sound design.
