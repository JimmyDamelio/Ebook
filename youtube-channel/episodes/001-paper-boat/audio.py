"""Episode 001 soundtrack (21 s, stereo, 44.1 kHz): typing, rain, thunder, a pad that resolves when the lighthouse finds the boat."""
import sys
import wave
import numpy as np

SR, DUR = 44100, 21.0
N = int(SR * DUR)
rng = np.random.default_rng(1)
L, R = np.zeros(N), np.zeros(N)
PROMPT = 'A tiny paper boat lost in an ink-black storm at sea, until a lighthouse finds it.'


def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    sig = sig[:max(0, N - i)] * gain
    L[i:i + len(sig)] += sig * np.sqrt(.5 * (1 - pan))
    R[i:i + len(sig)] += sig * np.sqrt(.5 * (1 + pan))


def lowpass(x, a):  # one-pole, a in (0,1): smaller = darker
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def env(t, pts):  # piecewise-linear envelope from (time, level) points
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])


def hz(n):  # MIDI note -> Hz
    return 440 * 2 ** ((n - 69) / 12)


t = np.arange(N) / SR

# typing ticks, matched to the on-screen typewriter (0.3 s -> 2.8 s)
for i, ch in enumerate(PROMPT):
    if ch == ' ':
        continue
    n = int(SR * .018)
    tick = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * .003))
    add(np.diff(tick, prepend=0), .3 + 2.5 * i / len(PROMPT), pan=rng.uniform(-.3, .3), gain=.12)

# rain: filtered noise, swells in with the storm and fades as it clears (11 -> 14.5 s)
rain_env = env(t, [(0, 0), (3.2, 0), (4.2, .22), (11, .22), (14.5, 0), (DUR, 0)])
L += lowpass(rng.standard_normal(N), .18) * rain_env  # independent noise per side = wide stereo
R += lowpass(rng.standard_normal(N), .18) * rain_env

# thunder at the two lightning strikes
for tb in (6.2, 8.0):
    n = int(SR * 3)
    rum = lowpass(rng.standard_normal(n), .01) * np.exp(-np.arange(n) / (SR * .8))
    crack = lowpass(rng.standard_normal(n), .3) * np.exp(-np.arange(n) / (SR * .04)) * 1.2
    add((rum * 6 + crack), tb, pan=-.3 if tb < 7 else .3, gain=.5)


def pad(notes, start, end, vel=.1, fade=1.2):
    n = int(SR * (end - start))
    tt = np.arange(n) / SR
    e = np.minimum(1, tt / fade) * np.minimum(1, (end - start - tt) / fade)
    for k, m in enumerate(notes):
        for det in (-.15, 0, .15):
            w = np.sin(2 * np.pi * (hz(m) + det) * tt + rng.uniform(0, 6.28))
            add(w * e * vel / 3, start, pan=(k / max(1, len(notes) - 1) - .5) * .6)


def bell(m, start, vel=.18):
    n = int(SR * 4)
    tt = np.arange(n) / SR
    s = sum(a * np.exp(-tt * d) * np.sin(2 * np.pi * hz(m) * r * tt) for r, a, d in [(1, 1, .8), (2, .5, 1.2), (2.76, .3, 1.8), (5.4, .15, 3)])
    add(s * np.minimum(1, tt / .003) * vel, start)


pad([45, 52, 57, 60], 0, 12.4)            # A minor, from the prompt card through the storm
pad([48, 55, 60, 64, 67], 11.6, 21)       # C major, found
for i in range(16):                        # slow piano-like arpeggio under the storm
    bell([57, 60, 64, 69][i % 4], 3.6 + i * .5, .05)
bell(84, 9.0, .1)                          # lamp turns on
bell(79, 11.9)                             # beam finds the boat
bell(84, 12.1, .12)
for i, m in enumerate([72, 76, 79, 84]):   # end card
    bell(m, 17.5 + i * .45, .1)

mix = np.stack([L, R], 1)
mix *= .89 / np.abs(mix).max()
fade = np.minimum(1, (DUR - t) / .8)[:, None]
out = (mix * fade * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'audio.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(out.tobytes())
