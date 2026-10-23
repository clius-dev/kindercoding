"""Generate the melodic B-1 kindergarten morning loop (v2)."""

from pathlib import Path
import wave

import numpy as np


SR = 44_100
BPM = 116
BEAT = 60 / BPM
TOTAL_BEATS = 32
DURATION = TOTAL_BEATS * BEAT
OUT = Path(__file__).with_name("B-1-kindergarten-morning-melody-v2.wav")
RNG = np.random.default_rng(20261007)

mix = np.zeros((int(DURATION * SR), 2), dtype=np.float64)


def frequency(midi):
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def stereo_pan(signal, pan):
    angle = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.column_stack((signal * np.cos(angle), signal * np.sin(angle)))


def piano_tone(midi, seconds, warmth=1.0):
    """Soft felt-piano tone with individually decaying, slightly inharmonic strings."""
    n = max(1, int(seconds * SR))
    t = np.arange(n) / SR
    f = frequency(midi)
    tone = np.zeros(n)
    phases = RNG.uniform(-0.08, 0.08, 9)
    for harmonic in range(1, 10):
        inharmonic = np.sqrt(1 + 0.00009 * harmonic * harmonic)
        partial_f = f * harmonic * inharmonic
        partial_gain = (1 / harmonic**1.48) * np.exp(-0.055 * (harmonic - 1))
        decay = (1.85 / (1 + 0.24 * harmonic)) * warmth
        tone += partial_gain * np.sin(2 * np.pi * partial_f * t + phases[harmonic - 1]) * np.exp(-t / decay)
    attack = 1 - np.exp(-t / 0.007)
    release = np.ones(n)
    release_len = min(n, int(0.20 * SR))
    release[-release_len:] *= np.linspace(1, 0, release_len) ** 1.35
    hammer_n = min(n, int(0.022 * SR))
    hammer = np.zeros(n)
    if hammer_n:
        noise = RNG.normal(0, 1, hammer_n)
        noise = np.convolve(noise, np.ones(7) / 7, mode="same")
        hammer[:hammer_n] = noise * np.exp(-np.arange(hammer_n) / SR / 0.006) * 0.025
    return (tone * attack * release + hammer) * 0.58


def kalimba_tone(midi, seconds):
    """Warm wooden tine used only for small answering notes."""
    n = max(1, int(seconds * SR))
    t = np.arange(n) / SR
    f = frequency(midi)
    tone = (
        np.sin(2 * np.pi * f * t)
        + 0.22 * np.sin(2 * np.pi * f * 2.03 * t + 0.3)
        + 0.09 * np.sin(2 * np.pi * f * 3.92 * t + 0.7)
    )
    env = (1 - np.exp(-t / 0.004)) * np.exp(-t / 0.62)
    return tone * env * 0.55


def bass_tone(midi, seconds):
    n = max(1, int(seconds * SR))
    t = np.arange(n) / SR
    f = frequency(midi)
    tone = np.sin(2 * np.pi * f * t) + 0.16 * np.sin(2 * np.pi * f * 2 * t)
    env = (1 - np.exp(-t / 0.018)) * np.exp(-t / 0.78)
    release_len = min(n, int(0.18 * SR))
    env[-release_len:] *= np.linspace(1, 0, release_len)
    return tone * env * 0.68


def add_note(midi, beat_at, beat_length, gain, instrument="piano", pan=0.0, humanize=True):
    timing = RNG.uniform(-0.010, 0.010) if humanize else 0
    start = max(0, int((beat_at * BEAT + timing) * SR))
    seconds = beat_length * BEAT + 0.36
    if instrument == "kalimba":
        signal = kalimba_tone(midi, seconds)
    elif instrument == "bass":
        signal = bass_tone(midi, seconds)
    else:
        signal = piano_tone(midi, seconds, warmth=1.08 if instrument == "felt" else 1.0)
    signal *= gain * RNG.uniform(0.94, 1.06)
    end = min(len(mix), start + len(signal))
    if end > start:
        mix[start:end] += stereo_pan(signal[: end - start], pan)


# A singable D-major melody with clear four-bar phrases and natural note lengths.
MELODY = [
    (0, 74, 0.90), (1, 78, 0.42), (1.5, 81, 0.42), (2, 78, 0.90), (3, 76, 0.72),
    (4, 74, 0.90), (5, 76, 0.90), (6, 78, 1.72),
    (8, 79, 0.90), (9, 81, 0.42), (9.5, 83, 0.42), (10, 81, 0.90), (11, 78, 0.72),
    (12, 76, 0.90), (13, 78, 0.90), (14, 74, 1.72),
    (16, 81, 0.90), (17, 83, 0.42), (17.5, 86, 0.42), (18, 85, 0.90), (19, 83, 0.72),
    (20, 79, 0.90), (21, 81, 0.90), (22, 83, 1.72),
    (24, 81, 0.90), (25, 78, 0.90), (26, 76, 0.90), (27, 73, 0.72),
    (28, 74, 0.90), (29, 78, 0.90), (30, 81, 0.46), (30.5, 78, 0.46), (31, 74, 0.68),
]

for index, (at, note, length) in enumerate(MELODY):
    phrase_gain = 0.108 + 0.012 * np.sin(index * 0.72)
    add_note(note, at, length, phrase_gain, "felt", pan=-0.10 + 0.20 * ((index % 5) / 4))

# Gentle answering notes make the tune conversational without turning into a beep pattern.
ANSWERS = [(7.25, 81), (15.25, 78), (23.25, 86), (31.35, 78)]
for at, note in ANSWERS:
    add_note(note, at, 0.48, 0.040, "kalimba", pan=0.34, humanize=False)

# Two soft piano pulses per bar. Voicings move smoothly instead of repeating a rigid arpeggio.
CHORDS = [
    (0, [62, 66, 69]), (4, [59, 62, 67]), (8, [61, 64, 69]), (12, [62, 66, 69]),
    (16, [59, 62, 66]), (20, [59, 62, 67]), (24, [61, 64, 69]), (28, [62, 66, 69]),
]
for bar, chord in CHORDS:
    for pulse, at in enumerate((bar, bar + 2)):
        for voice_index, note in enumerate(chord):
            add_note(note, at + voice_index * 0.035, 1.35, 0.031, "piano", pan=-0.24 + voice_index * 0.24)
    root = chord[0] - 24
    add_note(root, bar, 1.35, 0.052, "bass", pan=-0.04)
    add_note(root, bar + 2, 1.35, 0.044, "bass", pan=0.04)

# Light stereo room reverb; enough to blend tones, short enough for a clean loop.
dry = mix.copy()
for delay_s, amount, cross in ((0.072, 0.13, False), (0.119, 0.095, True), (0.183, 0.070, False), (0.267, 0.045, True)):
    delay = int(delay_s * SR)
    source = dry[:-delay, ::-1] if cross else dry[:-delay]
    mix[delay:] += source * amount

# Smooth dynamics and leave a tiny quiet seam for unobtrusive looping.
mix = np.tanh(mix * 1.08)
fade = int(0.016 * SR)
mix[:fade] *= np.linspace(0, 1, fade)[:, None]
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
peak = float(np.max(np.abs(mix)))
if peak:
    mix *= 0.72 / peak

pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
with wave.open(str(OUT), "wb") as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(SR)
    wav.writeframes(pcm.tobytes())

print(f"wrote {OUT} ({DURATION:.2f}s, {SR} Hz stereo, melodic v2)")
