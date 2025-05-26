HackerBox 0110 — RP2040-based synth expression visualizer
Purpose

   Generates 2-note synth drone sounds using the onboard rotary encoders

   Visualizes pitch via an expressive smiley face:
 🟢 Mouth curves from smile to frown based on note1
 🔵 Eyebrows tilt from sad to angry across −45° to +45° based on note2

Hardware Requirements

  HackerBox 0110 kit
  240×240 Circular TFT Display (GC9A01)
  MAX98357 I2S Audio Amplifier or compatible DAC
  Rotary Encoders ×2 (wired to GP15/14 and GP17/16)
  RP2040 board (Pico-compatible)
  Speaker

Pin Assignments
Function	RP2040 Pin	Notes
I2S BCLK	GP3	Audio bit clock
I2S L/R Select	GP4	Audio word select
I2S DATA	GP5	Audio output
Rotary Encoder A1	GP15	Right encoder
Rotary Encoder B1	GP14	Right encoder
Rotary Encoder A2	GP17	Left encoder
Rotary Encoder B2	GP16	Left encoder
Display SPI CLK	GP10	SPI clock to GC9A01
Display MOSI	GP11	SPI data to GC9A01
Display DC (Command)	GP8	Data/Command select
Display CS (Select)	GP9	Chip select
Display Reset	GP12	Hardware reset
Button Input (A/B)	GP18 / GP7	Optional control buttons
Software Features

  - synthio: real-time waveform synthesis (saw waves)
  - audiomixer & audiobusio: I2S audio output
  - ulab.numpy: custom waveform generation
  - adafruit_display_shapes: drawing smiley face, lines, and arcs

Expression updates every 50ms, based on encoder-controlled note frequency

Library Dependencies

Ensure these libraries are in your /lib folder:
- adafruit_display_shapes/
- ulab/ (usually bundled with CircuitPython 9+)

    synthio/ (built into firmware — needs CircuitPython ≥ 8.2)
