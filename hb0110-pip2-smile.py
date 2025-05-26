# Smiley face: mouth and eyebrows recreated per update

import time, math
import board, rotaryio, keypad
import audiobusio, audiomixer, synthio
import ulab.numpy as np
import displayio
import busio
from fourwire import FourWire
import gc9a01
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line

DW, DH = 240, 240
displayio.release_displays()
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = FourWire(spi, command=board.GP8, chip_select=board.GP9, reset=board.GP12, baudrate=32_000_000)
display = gc9a01.GC9A01(display_bus, width=DW, height=DH, auto_refresh=True)

main_group = displayio.Group()
display.root_group = main_group

# Face background
face = Circle(DW//2, DH//2, DW//2 - 4, fill=0xFFFF00, outline=0x000000)
main_group.append(face)

# Eyes
left_eye = Circle(DW//2 - 50, DH//2 - 40, 10, fill=0x000000)
right_eye = Circle(DW//2 + 50, DH//2 - 40, 10, fill=0x000000)
main_group.append(left_eye)
main_group.append(right_eye)

# Global for replacing
mouth_lines = []
left_brow = None
right_brow = None

# Audio + Input
keys = keypad.Keys((board.GP18, board.GP7), value_when_pressed=False, pull=True)
right_encoder = rotaryio.IncrementalEncoder(board.GP15, board.GP14)
left_encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)

sample_rate = 44100
i2s_bclk, i2s_lclk, i2s_data = board.GP3, board.GP4, board.GP5
audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lclk, data=i2s_data)
mixer = audiomixer.Mixer(voice_count=1, channel_count=1, sample_rate=sample_rate, buffer_size=2048)
synth = synthio.Synthesizer(channel_count=1, sample_rate=sample_rate)
audio.play(mixer)
mixer.voice[0].play(synth)

lfo = synthio.LFO(rate=5)
amp_env = synthio.Envelope(attack_time=0.5, release_time=0.5)
wave_saw = np.linspace(30000, -30000, num=512, dtype=np.int16)
note1 = synthio.Note(frequency=100, waveform=wave_saw, amplitude=0.5, envelope=amp_env)
note2 = synthio.Note(frequency=100, waveform=wave_saw, amplitude=0.5, envelope=amp_env)
synth.press((note1, note2))

def update_expression(f1, f2):
    global mouth_lines, left_brow, right_brow

    # Remove old mouth
    for line in mouth_lines:
        main_group.remove(line)
    mouth_lines = []

    # Draw new mouth based on f1
    mouth_y = DH // 2 + 40
    mouth_width = 80
    segments = 20
    curve_amount = max(-1, min(1, (f1 - 440) / 220))

    for i in range(segments):
        x0 = DW//2 - mouth_width//2 + i * (mouth_width // segments)
        x1 = x0 + (mouth_width // segments)
        y_offset = int(math.sin(i / segments * math.pi) * 40 * -curve_amount)
        y0 = mouth_y + y_offset
        y1 = mouth_y + y_offset
        line = Line(x0, y0, x1, y1, color=0x000000)
        mouth_lines.append(line)
        main_group.append(line)

    # Replace eyebrows
    if left_brow:
        main_group.remove(left_brow)
    if right_brow:
        main_group.remove(right_brow)

    brow_level = max(0, min(8, int((f2 - 220) / 40)))  # range 0 to 8, includes downward tilt
    # Interpolated tilt
    tilt_offsets = [
        (-36, -64),  # -45°
        (-39, -61),
        (-42, -58),
        (-45, -55),
        (-50, -50),  # neutral
        (-54, -46),  # +15°
        (-58, -42),  # +30°
        (-61, -39),  # +40°
        (-64, -36),  # +45°
    ]
    ly1, ly2 = tilt_offsets[brow_level]
    ry2, ry1 = tilt_offsets[brow_level]  # mirrored reverse

    left_brow = Line(DW//2 - 65, DH//2 + ly1, DW//2 - 35, DH//2 + ly2, color=0x000000)
    right_brow = Line(DW//2 + 35, DH//2 + ry1, DW//2 + 65, DH//2 + ry2, color=0x000000)

    main_group.append(left_brow)
    main_group.append(right_brow)
    display.refresh()

k1, k2 = 0, 0
while True:
    if key := keys.events.get():
        if key.key_number == 0:
            note1.bend = lfo if key.pressed else 0
        elif key.key_number == 1:
            if key.pressed:
                synth.release_all()
            else:
                synth.press((note1, note2))

    k1 = 80 + right_encoder.position
    k2 = 75 + left_encoder.position
    k1 = max(35, min(140, k1))
    k2 = max(35, min(140, k2))

    note1.frequency = synthio.midi_to_hz(k1)
    note2.frequency = synthio.midi_to_hz(k2)

    update_expression(note1.frequency, note2.frequency)
    time.sleep(0.05)
