"""Soundtrack for a social film: synthesised score (D major palette) + Kokoro voice (vo/) + small effects -> audio.wav

usage (from the film folder, which holds score.json and vo.json): python3 ../lib/music.py
score.json: {"duration": 27.8,
             "chords": [[0, 4.2, "Bm"], ...],          # names from CHORDS below
             "accents": [[4.3, "G2", "D6", -0.3], ...],  # scene-cut attack: sub thump + low piano + bell
             "swooshes": [[4.0, 0.9], ...],
             "scribbles": [[0.3, 0.9], ...],             # pencil writing: start, length
             "sfx": [[9.9, "tick", -6, 0.2], ...]}       # lib/sfx/<name>.wav, gain dB, pan
"""
import json
import os
import wave

import numpy as np
import soundfile as sf

SR = 44100
score = json.load(open('score.json'))
vo = json.load(open('vo.json'))
DUR = score['duration']
N = int(SR * DUR)
rng = np.random.default_rng(7)
L, R = np.zeros(N), np.zeros(N)
HERE = os.path.dirname(os.path.abspath(__file__))

CHORDS = {  # pad, arp, bass
    'Bm': (['B2', 'F#3', 'A3', 'D4'], ['B4', 'D5', 'F#5', 'A5'], 'B1'),
    'G': (['G2', 'D3', 'F#3', 'B3'], ['G4', 'B4', 'D5', 'F#5'], 'G1'),
    'Em': (['E2', 'B2', 'D3', 'G3'], ['E5', 'G5', 'B5', 'D6'], 'E1'),
    'A': (['A2', 'E3', 'G3', 'C#4'], ['A4', 'C#5', 'E5', 'G5'], 'A1'),
    'D': (['D3', 'A3', 'C#4', 'F#4'], ['D5', 'F#5', 'A5', 'C#6'], 'D2'),
    'Dadd9': (['D3', 'A3', 'C#4', 'E4', 'F#4'], ['D5', 'F#5', 'A5', 'E6'], 'D2'),
    'F#m': (['F#2', 'C#3', 'E3', 'A3'], ['F#4', 'A4', 'C#5', 'E5'], 'F#1'),
}


def hz(note):
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0, dst=None):
    dl, dr = dst or (L, R)
    i = int(start * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= N:
        return
    sig = sig[:N - i] * gain
    dl[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    dr[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def piano(f, dur=3.5, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros_like(t)
    for n in range(1, 9):
        fn = f * n * np.sqrt(1 + 0.0004 * n * n)
        if fn > SR / 2.2:
            break
        out += (1 / n ** 1.6) * np.exp(-t * (0.9 + 0.55 * n)) * np.sin(2 * np.pi * fn * t + n)
    return out * np.minimum(1, t / 0.006) * np.minimum(1, (dur - t) / 0.4) * vel


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
            add(w * env * lfo * vel / 3, start - fade / 2, pan=(k / max(1, len(freqs) - 1) - .5) * 1.2)


def band_noise(n, lo, hi):
    spec = np.fft.rfft(rng.standard_normal(n))
    fr = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-((np.log(fr + 1) - np.log((lo * hi) ** .5)) ** 2) / (2 * 0.7 ** 2))
    s = np.fft.irfft(spec, n)
    return s / (np.abs(s).max() + 1e-9)


def swoosh(start, dur, vel=0.15):
    n = int(SR * dur)
    s = band_noise(n, 300, 2500) * np.sin(np.pi * np.arange(n) / n) ** 2
    add(s * vel * .5, start, pan=-.4); add(s * vel * .5, start, pan=.3)


# ---- score
CH = [(s, e, *CHORDS[c]) for s, e, c in score['chords']]
for s, e, p, arp, b in CH:
    pad([hz(n) for n in p], s, e, vel=0.11)
    if s > 0:
        add(piano(hz(b), 4.0, 0.5), s, pan=-.1)
        add(piano(hz(b) * 2, 4.0, 0.22), s, pan=-.1)
step = 60 / 76 / 2
pattern = [0, 2, 1, 3, 2, 1, 3, 2]
tt, k = score.get('arp_from', 0.0), 0
while tt < DUR - 1.2:
    arp = next(c for c in CH if c[0] <= tt < c[1])[3]
    if tt >= score.get('thin_from', DUR) and k % 2:
        tt += step; k += 1; continue
    vel = (0.18 + 0.07 * (k % 4 == 0) + 0.03 * np.sin(k * .7)) * (1.1 if tt > DUR * .5 else 1)
    add(piano(hz(arp[pattern[k % 8]]), 2.6, vel), tt + rng.uniform(-.008, .008), pan=.7 * np.sin(k * .9))
    tt += step; k += 1
for s, d in score.get('swooshes', []):
    swoosh(s, d)


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
master = np.minimum(1, t / .05) * np.minimum(1, (DUR - t) / .5)
L *= master; R *= master
mpk = max(np.abs(L).max(), np.abs(R).max())
L, R = L / mpk, R / mpk

# ---- voice
V = np.zeros(N)
for c in vo['clips']:
    a, sr = sf.read(f"vo/{c['key']}.wav")
    a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    i = int(c['at'] * SR); a = a[:N - i]; V[i:i + len(a)] += a
V /= np.abs(V).max()
env = np.convolve(np.abs(V), np.ones(int(.25 * SR)) / int(.25 * SR), mode='same')
duck = 1 - .65 * np.clip(env / (env.max() * .35), 0, 1)

# ---- effects (above the duck): cut accents, pencil scribbles, ticks
AL, AR = np.zeros(N), np.zeros(N)
for at, note, bn, pan in score.get('accents', []):
    n = int(SR * .9); tt_ = np.arange(n) / SR
    sig = np.sin(2 * np.pi * (48 + 30 * np.exp(-tt_ * 18)) * tt_) * np.exp(-tt_ * 7) * np.minimum(1, tt_ / .004) * .8
    p = piano(hz(note), .9, .5); sig[:len(p)] += p
    b = bell(hz(bn), .9, .22); sig[:len(b)] += b
    add(sig * .32, at, pan, dst=(AL, AR))
for at, d in score.get('scribbles', []):  # graphite on paper: bright band noise, stroke rhythm ~9 Hz
    n = int(SR * d); tt_ = np.arange(n) / SR
    strokes = (.55 + .45 * np.abs(np.sin(np.pi * 9.3 * tt_ + rng.uniform(0, 3)))) * np.minimum(1, tt_ / .03) * np.minimum(1, (d - tt_) / .06)
    add(band_noise(n, 2500, 7000) * strokes * .05, at, pan=.15, dst=(AL, AR))
for at, name, gdb, pan in score.get('sfx', []):
    a, sr = sf.read(os.path.join(HERE, 'sfx', name + '.wav'))
    a = a.mean(1) if a.ndim > 1 else a
    a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    add(a * 10 ** (gdb / 20) * .4, at, pan, dst=(AL, AR))

L = L * duck * .32 + V * .9 + AL
R = R * duck * .32 + V * .9 + AR
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * .89, R / peak * .89
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L, R], 1) * 32767).astype(np.int16).tobytes())
print('audio.wav', round(DUR, 2), 's')
