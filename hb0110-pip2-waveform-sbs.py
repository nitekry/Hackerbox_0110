# Vertical dual waveform display: note1 (left) and note2 (right)

import time, math, random
import board, rotaryio, keypad
import audiobusio, audiocore, audiomixer, synthio
import ulab.numpy as np
import busio, displayio
from fourwire import FourWire
import gc9a01

DW, DH = 240, 240
displayio.release_displays()
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = FourWire(spi, command=board.GP8, chip_select=board.GP9, reset=board.GP12, baudrate=32_000_000)
display = gc9a01.GC9A01(display_bus, width=DW, height=DH, auto_refresh=False)

maingroup = displayio.Group()
display.root_group = maingroup

wave_bitmap = displayio.Bitmap(DW, DH, 3)
wave_palette = displayio.Palette(3)
wave_palette[0] = 0x000000
wave_palette[1] = 0x00FF00
wave_palette[2] = 0x0000FF
wave_tilegrid = displayio.TileGrid(wave_bitmap, pixel_shader=wave_palette)
maingroup.append(wave_tilegrid)

keys = keypad.Keys((board.GP18, board.GP7), value_when_pressed=False, pull=True)
right_encoder = rotaryio.IncrementalEncoder(board.GP15, board.GP14)
left_encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)

sample_rate = 44100
i2s_bclk, i2s_lclk, i2s_data = board.GP3, board.GP4, board.GP5
audio = audiobusio.I2SOut(bit_clock=i2s_bclk, word_select=i2s_lclk, data=i2s_data)
mixer = audiomixer.Mixer(voice_count=1, channel_count=1, sample_rate=sample_rate, buffer_size=2048)
synth = synthio.Synthesizer(channel_count=1, sample_rate=sample_rate)
audio.play(mixer)

try:
    import audiodelays
    effect = audiodelays.Echo(max_delay_ms=600, delay_ms=600,
                               decay=.07, mix=0.4, freq_shift=False,
                               buffer_size=2048, sample_rate=sample_rate)
    mixer.voice[0].play(effect)
    effect.play(synth)
except ImportError:
    mixer.voice[0].play(synth)

lfo = synthio.LFO(rate=5)
amp_env = synthio.Envelope(attack_time=0.5, release_time=0.5)
wave_saw = np.linspace(30000, -30000, num=512, dtype=np.int16)
note1 = synthio.Note(frequency=100, waveform=wave_saw, amplitude=0.5, envelope=amp_env)
note2 = synthio.Note(frequency=100, waveform=wave_saw, amplitude=0.5, envelope=amp_env)
synth.press((note1, note2))

def draw_waveform(freq1, freq2):
    wave_bitmap.fill(0)
    for y in range(DH):
        angle1 = y * freq1 / 800.0
        angle2 = y * freq2 / 800.0

        x1 = int(3 * DW / 4 + math.sin(angle1) * (DW / 4))
        x2 = int(DW / 4 + math.sin(angle2) * (DW / 4))

        for thickness in range(-1, 1):
            tx1 = x1 + thickness
            tx2 = x2 + thickness
            if 0 <= tx1 < DW:
                wave_bitmap[tx1, y] = 1
            if 0 <= tx2 < DW:
                wave_bitmap[tx2, y] = 2

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
    
    draw_waveform(note1.frequency, note2.frequency)
    display.refresh()
    time.sleep(0.01)
