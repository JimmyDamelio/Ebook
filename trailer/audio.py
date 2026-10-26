"""Synthesises the trailer soundtrack (30 s, stereo, 44.1 kHz) -> audio.wav"""
import wave
import numpy as np

SR = 44100
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def hz(note):
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= N:
        return
    sig = sig[:N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def piano(f, dur=3.5, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros_like(t)
    for n in range(1, 9):
        fn = f * n * np.sqrt(1 + 0.0004 * n * n)
        if fn > SR / 2.2:
            break
        out += (1 / n ** 1.6) * np.exp(-t * (0.9 + 0.55 * n)) * np.sin(2 * np.pi * fn * t + n)
    att = np.minimum(1, t / 0.006)
    rel = np.minimum(1, (dur - t) / 0.4)
    return out * att * rel * vel


def bell(f, dur=5.0, vel=0.4):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros_like(t)
    for ratio, amp, dec in [(1, 1, 0.7), (2.0, .5, 1.1), (2.76, .35, 1.6), (5.4, .2, 2.5), (8.93, .1, 3.5)]:
        out += amp * np.exp(-t * dec) * np.sin(2 * np.pi * f * ratio * t)
    return out * np.minimum(1, t / 0.003) * np.minimum(1, (dur - t) / 0.3) * vel


def pad(freqs, start, end, vel=0.12, fade=1.4):
    dur = end - start + fade
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / fade) * np.minimum(1, (dur - t) / fade)
    for k, f in enumerate(freqs):
        for det in (-0.12, 0.0, 0.13):
            ph = rng.uniform(0, 6.28)
            w = np.sin(2 * np.pi * (f + det) * t + ph) + 0.18 * np.sin(2 * np.pi * 2 * (f + det) * t + ph) + 0.06 * np.sin(2 * np.pi * 3 * (f + det) * t)
            lfo = 1 + 0.15 * np.sin(2 * np.pi * 0.21 * t + k)
            add(w * env * lfo * vel / 3, start - fade / 2, pan=(k / max(1, len(freqs) - 1) - .5) * 0.6)


def swoosh(start, dur, vel=0.18, lo=300, hi=2500):
    n = int(SR * dur)
    noise = rng.standard_normal(n)
    spec = np.fft.rfft(noise)
    fr = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-((np.log(fr + 1) - np.log((lo * hi) ** .5)) ** 2) / (2 * 0.7 ** 2))
    s = np.fft.irfft(spec, n)
    s /= np.abs(s).max() + 1e-9
    t = np.arange(n) / n
    env = np.sin(np.pi * t) ** 2
    for k in range(2):
        add(s * env * vel, start, pan=(-.6 + 1.2 * t[0]) if k == 0 else .3, gain=.5)


# ---- harmony: (start, end, pad notes, arp notes, bass)
CH = [
    (0.0, 5.0, ['B2', 'F#3', 'A3', 'D4'], ['B4', 'D5', 'F#5', 'A5'], 'B1'),
    (5.0, 10.2, ['G2', 'D3', 'F#3', 'B3'], ['G4', 'B4', 'D5', 'F#5'], 'G1'),
    (10.2, 14.6, ['A2', 'E3', 'G3', 'C#4'], ['A4', 'C#5', 'E5', 'G5'], 'A1'),
    (14.6, 20.0, ['D3', 'A3', 'C#4', 'F#4'], ['D5', 'F#5', 'A5', 'C#6'], 'D2'),
    (20.0, 25.2, ['E2', 'B2', 'D3', 'G3'], ['E5', 'G5', 'B5', 'D6'], 'E1'),
    (25.2, 27.4, ['A2', 'E3', 'G3', 'D4'], ['A4', 'D5', 'E5', 'G5'], 'A1'),
    (27.4, 30.5, ['D3', 'A3', 'C#4', 'E4', 'F#4'], ['D5', 'F#5', 'A5', 'E6'], 'D2'),
]
for s, e, p, arp, b in CH:
    pad([hz(n) for n in p], s, e, vel=0.10 if s < 5 else 0.12)
    if s > 0:
        add(piano(hz(b), 4.0, 0.55), s, pan=-.1)
        add(piano(hz(b) * 2, 4.0, 0.25), s, pan=-.1)

# night: sparse notes
for tt, n in [(0.6, 'F#5'), (2.2, 'D5'), (3.4, 'A4'), (4.2, 'B4')]:
    add(piano(hz(n), 4, .32), tt, pan=.25)

# arpeggios from 5.0, 8th notes at 76 bpm
step = 60 / 76 / 2
pattern = [0, 2, 1, 3, 2, 1, 3, 2]
tt, k = 5.0, 0
while tt < 28.9:
    chord = next(c for c in CH if c[0] <= tt < c[1])
    arp = chord[3]
    if tt >= 27.4 and k % 2:
        tt += step; k += 1; continue  # thin out at the end
    vel = 0.20 + 0.08 * (k % 4 == 0) + 0.03 * np.sin(k * .7)
    if tt > 14.6:
        vel *= 1.15
    add(piano(hz(arp[pattern[k % 8]]), 2.6, vel), tt + rng.uniform(-.008, .008), pan=.35 * np.sin(k * .9))
    tt += step; k += 1

# accents
add(bell(hz('F#6'), 5, .22), 1.45, pan=-.2)          # clock minute change
for i, n in enumerate(['A5', 'C#6', 'F#6', 'A6']):     # book reveal shimmer
    add(bell(hz(n), 5, .12), 14.6 + i * .07, pan=-.4 + i * .27)
for i, n in enumerate(['D6', 'A6']):                   # end card
    add(bell(hz(n), 6, .16), 27.45 + i * .1, pan=-.2 + i * .4)
for s, d in [(4.4, 1.3), (9.65, .9), (13.95, 1.0), (19.45, .95), (24.85, .95), (27.05, 1.0)]:
    swoosh(s, d)

# ---- reverb (FFT convolution with decaying noise IR)
def reverb(x, seed, secs=2.6, mix=.32):
    r = np.random.default_rng(seed)
    n = int(SR * secs)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * 3.0)
    ir[:int(.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    m = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return x * (1 - mix) + wet * mix * 1.6


L, R = reverb(L, 1), reverb(R, 2)
t = np.arange(N) / SR
master = np.minimum(1, t / .6) * np.minimum(1, (DUR - t) / 1.0)
L *= master; R *= master
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * .89, R / peak * .89
pcm = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', pcm.shape)
