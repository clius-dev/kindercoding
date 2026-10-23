"""B-1_01 algorithms 용 신나는 BGM 루프 (C major, 132 BPM, 16마디 ≈ 29s).
출력 RMS 를 기존 BGM(B-2-spring-strawberry-garden-loop.wav, 0.1041)에 맞춘다."""
from pathlib import Path
import wave
import numpy as np

SR = 44_100
BPM = 132
BEAT = 60 / BPM
BARS = 16
TOTAL = BARS * 4
DUR = TOTAL * BEAT
OUT = Path(__file__).with_name("B-1_01-happy-bounce-loop.wav")
TARGET_RMS = 0.1041          # B-2 wav 실측값
RNG = np.random.default_rng(20261013)
N = int(round(DUR * SR))
mix = np.zeros((N, 2))

def fr(m): return 440.0 * 2 ** ((m - 69) / 12)

def pan(sig, p):
    a = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.column_stack((sig * np.cos(a), sig * np.sin(a)))

def put(sig, beat, p=0.0):
    s = int(round(beat * BEAT * SR))
    st = pan(sig, p)
    n = len(st)
    idx = (np.arange(n) + s) % N          # 끝을 넘으면 처음으로 감아 이음새 없는 루프
    np.add.at(mix, idx, st)

def pluck(m, sec, bright=1.0):
    n = int(sec * SR); t = np.arange(n) / SR; f = fr(m)
    s = (np.sin(2*np.pi*f*t) + .38*bright*np.sin(2*np.pi*f*2*t)*np.exp(-t/.18)
         + .16*bright*np.sin(2*np.pi*f*3*t)*np.exp(-t/.10))
    return s * (1 - np.exp(-t/.003)) * np.exp(-t/.26)

def bell(m, sec):
    n = int(sec * SR); t = np.arange(n) / SR; f = fr(m)
    s = np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*f*2.76*t)*np.exp(-t/.12)
    return s * (1 - np.exp(-t/.002)) * np.exp(-t/.45)

def bass(m, sec):
    n = int(sec * SR); t = np.arange(n) / SR; f = fr(m)
    s = np.sin(2*np.pi*f*t) + .25*np.sin(2*np.pi*f*2*t)
    e = (1 - np.exp(-t/.006)) * np.exp(-t/.20)
    return s * e

def stab(m, sec):
    n = int(sec * SR); t = np.arange(n) / SR; f = fr(m)
    s = np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*f*2*t)
    return s * (1 - np.exp(-t/.004)) * np.exp(-t/.07)

def kick():
    n = int(.22*SR); t = np.arange(n)/SR
    ph = 2*np.pi*(45*t + 75*(1-np.exp(-t/.035))*.035)
    return np.sin(ph) * np.exp(-t/.09)

def clap():
    n = int(.14*SR); t = np.arange(n)/SR
    x = RNG.normal(0, 1, n)
    x = x - np.convolve(x, np.ones(9)/9, mode='same')     # 간단 하이패스
    return x * np.exp(-t/.035)

def hat(open_=False):
    n = int((.12 if open_ else .035)*SR); t = np.arange(n)/SR
    x = RNG.normal(0, 1, n)
    x = x - np.convolve(x, np.ones(5)/5, mode='same')
    return x * np.exp(-t/(.05 if open_ else .012))

# ---- 코드 진행 (한 마디 한 코드): C G Am F | C G F G ----
PROG = [(48,[60,64,67]),(43,[59,62,67]),(45,[60,64,69]),(41,[60,65,69]),
        (48,[60,64,67]),(43,[59,62,67]),(41,[60,65,69]),(43,[59,62,67])]

# ---- 멜로디 (마디 내 박 위치, MIDI, 길이[박]) ----
A = [
 [(0,72,.5),(.5,76,.5),(1,79,.5),(1.5,76,.5),(2,84,1),(3,79,.5),(3.5,76,.5)],
 [(0,74,.5),(.5,79,.5),(1,83,.5),(1.5,79,.5),(2,86,1),(3,83,.5),(3.5,79,.5)],
 [(0,72,.5),(.5,76,.5),(1,81,.5),(1.5,76,.5),(2,84,1),(3,81,.5),(3.5,76,.5)],
 [(0,77,.5),(.5,81,.5),(1,84,.5),(1.5,81,.5),(2,79,1),(3,77,1)],
]
B = [
 [(0,79,.5),(.5,79,.5),(1,84,1),(2,83,.5),(2.5,84,.5),(3,88,1)],
 [(0,86,.5),(.5,86,.5),(1,83,1),(2,79,.5),(2.5,83,.5),(3,86,1)],
 [(0,84,.5),(.5,81,.5),(1,77,.5),(1.5,81,.5),(2,84,.5),(2.5,81,.5),(3,77,1)],
 [(0,79,.5),(.5,83,.5),(1,86,.5),(1.5,83,.5),(2,79,.5),(2.5,74,.5),(3,71,.5),(3.5,74,.5)],
]
MEL = A + B

for rep in range(2):                         # 16마디 = 8마디 x 2
    for bar in range(8):
        b0 = (rep*8 + bar) * 4
        root, ch = PROG[bar]
        # 멜로디: 앞 8마디는 pluck, 뒤 8마디는 pluck + 한 옥타브 위 bell
        for (at, m, ln) in MEL[bar]:
            g = 0.34 * RNG.uniform(.95, 1.05)
            put(pluck(m, ln*BEAT + .3) * g, b0 + at, -0.12)
            if rep == 1:
                put(bell(m + 12, ln*BEAT + .4) * 0.10, b0 + at, 0.2)
        # 베이스: 루트-옥타브 튀는 패턴
        for at, off, ln in ((0,0,.9),(1,12,.45),(1.5,0,.45),(2,0,.9),(3,7,.45),(3.5,12,.45)):
            put(bass(root + off, ln*BEAT + .1) * 0.36, b0 + at, 0.0)
        # 코드 스탭: 엇박(and)
        for at in (0.5, 1.5, 2.5, 3.5):
            for i, m in enumerate(ch):
                put(stab(m, .2) * 0.060, b0 + at, -0.3 + 0.3*i)
        # 드럼
        for at in (0, 2):
            put(kick() * 0.55, b0 + at)
        if rep == 1: put(kick() * 0.40, b0 + 3.5)
        for at in (1, 3):
            put(clap() * 0.07, b0 + at, 0.1)
        for k in range(8):
            put(hat(open_=(k % 4 == 3)) * (0.030 if k % 2 else 0.018), b0 + k*.5, 0.25)

# ---- 짧은 룸 리버브 (순환 지연 → 루프 이음새 유지) ----
dry = mix.copy()
for d, a, cross in ((0.061,.10,False),(0.097,.07,True),(0.151,.05,False)):
    sh = int(d*SR)
    src = np.roll(dry, sh, axis=0)
    mix += (src[:, ::-1] if cross else src) * a

mix = np.tanh(mix * 1.0)
rms = float(np.sqrt((mix**2).mean()))
mix *= TARGET_RMS / rms
peak = float(np.abs(mix).max())
print("rms", float(np.sqrt((mix**2).mean())), "peak", peak, "dur", DUR)
if peak > 0.95:
    raise SystemExit("peak too high")
pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
with wave.open(str(OUT), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", OUT)
