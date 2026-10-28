"""Soundtrack for the 9:16 "3 a.m." social clip (27.5 s): music synthesised here + Kokoro voice-over (vo/) -> audio.wav"""
import wave
import numpy as np
import soundfile as sf

SR = 44100
DUR = 27.5
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
            add(w * env * lfo * vel / 3, start - fade / 2, pan=(k / max(1, len(freqs) - 1) - .5) * 1.2)


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


# ---- harmony per scene: (start, end, pad notes, arp notes, bass)
CH = [
    (0.0, 3.0, ['B2', 'F#3', 'A3', 'D4'], ['B4', 'D5', 'F#5', 'A5'], 'B1'),
    (3.0, 6.4, ['G2', 'D3', 'F#3', 'B3'], ['G4', 'B4', 'D5', 'F#5'], 'G1'),
    (6.4, 10.0, ['E2', 'B2', 'D3', 'G3'], ['E5', 'G5', 'B5', 'D6'], 'E1'),
    (10.0, 14.2, ['A2', 'E3', 'G3', 'C#4'], ['A4', 'C#5', 'E5', 'G5'], 'A1'),
    (14.2, 19.8, ['D3', 'A3', 'C#4', 'F#4'], ['D5', 'F#5', 'A5', 'C#6'], 'D2'),
    (19.8, 23.5, ['G2', 'D3', 'F#3', 'B3'], ['G4', 'B4', 'D5', 'F#5'], 'G1'),
    (23.5, 28.0, ['D3', 'A3', 'C#4', 'E4', 'F#4'], ['D5', 'F#5', 'A5', 'E6'], 'D2'),
]
for s, e, p, arp, b in CH:
    pad([hz(n) for n in p], s, e, vel=0.10 if s < 3 else 0.12)
    if s > 0:
        add(piano(hz(b), 4.0, 0.5), s, pan=-.1)
        add(piano(hz(b) * 2, 4.0, 0.22), s, pan=-.1)

# night: sparse notes
for tt, n in [(0.1, 'F#5'), (1.2, 'D5'), (2.2, 'A4')]:
    add(piano(hz(n), 4, .3), tt, pan=.25)

# arpeggios from 3.0, 8th notes at 76 bpm
step = 60 / 76 / 2
pattern = [0, 2, 1, 3, 2, 1, 3, 2]
tt, k = 3.0, 0
while tt < 26.6:
    arp = next(c for c in CH if c[0] <= tt < c[1])[3]
    if tt >= 23.5 and k % 2:
        tt += step; k += 1; continue  # thin out on the end card
    vel = 0.18 + 0.07 * (k % 4 == 0) + 0.03 * np.sin(k * .7)
    if tt > 14.2:
        vel *= 1.12
    add(piano(hz(arp[pattern[k % 8]]), 2.6, vel), tt + rng.uniform(-.008, .008), pan=.7 * np.sin(k * .9))
    tt += step; k += 1

# accents
add(bell(hz('F#6'), 4, .2), 0.45, pan=-.2)                      # clock glow pulse
add(bell(hz('A6'), 4, .12), 12.85, pan=-.3)                     # pattern circled
add(bell(hz('F#6'), 4, .1), 13.2, pan=.3)
for i, n in enumerate(['A5', 'C#6', 'F#6', 'A6']):              # book reveal shimmer
    add(bell(hz(n), 5, .11), 14.3 + i * .07, pan=-.4 + i * .27)
for i, n in enumerate(['D6', 'A6']):                            # end card
    add(bell(hz(n), 5, .14), 23.5 + i * .1, pan=-.2 + i * .4)
for s, d in [(2.75, .9), (6.1, .9), (9.7, .85), (13.9, .9), (19.5, .85), (23.2, .9), (26.85, .7)]:
    swoosh(s, d, vel=.15)

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
master = np.minimum(1, t / .05) * np.minimum(1, (DUR - t) / .5)   # starts at once: the hook is frame 0
L *= master; R *= master
mpeak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / mpeak, R / mpeak

# ---- voice-over, placed on the picture's timeline
VO = [('threeam', .2), ('awake', 1.45), ('hot', 3.15), ('foggy', 3.75), ('flat', 4.35), ('wired', 4.95),
      ('peri', 6.6), ('pattern', 10.3), ('book', 14.45), ('summary', 20.0), ('end', 23.8)]
V = np.zeros(N)
for key, at in VO:
    a, sr = sf.read(f'vo/{key}.wav')
    a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    i = int(at * SR); a = a[:N - i]; V[i:i + len(a)] += a
V /= np.abs(V).max()

# duck the music under the voice (~ -9 dB), smooth attack/release
env = np.abs(V)
win = int(.25 * SR)
env = np.convolve(env, np.ones(win) / win, mode='same')
env = np.clip(env / (env.max() * .35), 0, 1)
duck = 1 - .65 * env
music_gain = .32
# scene-cut accents ride above the duck: soft sub thump + low piano + bell, so each cut has an attack
AL, AR = np.zeros(N), np.zeros(N)


def accent(at, note, bell_note, pan):
    n = int(SR * .9); tt = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (48 + 30 * np.exp(-tt * 18)) * tt) * np.exp(-tt * 7) * np.minimum(1, tt / .004) * .8
    sig = thump.copy()
    p = piano(hz(note), .9, .5); sig[:len(p)] += p
    b = bell(hz(bell_note), .9, .22); sig[:len(b)] += b
    i = int(at * SR); sig = sig[:N - i]
    AL[i:i + len(sig)] += sig * np.sqrt(.5 * (1 - pan)); AR[i:i + len(sig)] += sig * np.sqrt(.5 * (1 + pan))


for at, note, bn, pan in [(3.05, 'G2', 'D6', -.3), (6.45, 'E2', 'B5', .3), (10.12, 'A2', 'E6', -.3),
                          (14.25, 'D2', 'A6', .3), (19.9, 'G2', 'D6', -.3), (23.55, 'D2', 'F#6', .3), (27.12, 'B1', 'F#5', 0)]:
    accent(at, note, bn, pan)
apk = max(np.abs(AL).max(), np.abs(AR).max())
L = L * duck * music_gain + V * .9 + AL / apk * .32
R = R * duck * music_gain + V * .9 + AR / apk * .32
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * .89, R / peak * .89
pcm = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', pcm.shape)
