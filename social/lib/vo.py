"""Voice-over for a social film: Kokoro clips + word timings for on-screen captions.

usage (run inside the film folder, which holds vo.json):
  python3 ../lib/vo.py gen      -> vo/<key>.wav, prints each clip's length
  python3 ../lib/vo.py align    -> words.js (window.WORDS for karaoke captions), needs "at" on every clip

vo.json: {"voice": "af_heart", "speed": 0.9,
          "show": {"forty-five": "45"},                  # caption spelling for spoken words (optional)
          "clips": [{"key": "hook", "text": "...", "at": 0.2}, ...]}
Captions use the script's own words; Whisper only supplies the timing.
"""
import difflib
import json
import re
import sys

import numpy as np
import soundfile as sf

spec = json.load(open('vo.json'))


def gen():
    from kokoro_onnx import Kokoro
    k = Kokoro('/root/tts-models/kokoro-v1.0.onnx', '/root/tts-models/voices-v1.0.bin')
    import os
    os.makedirs('vo', exist_ok=True)
    for c in spec['clips']:
        a, sr = k.create(c['text'], voice=spec.get('voice', 'af_heart'), speed=spec.get('speed', .9), lang='en-us')
        sf.write(f"vo/{c['key']}.wav", a, sr)
        print(f"{c['key']:10s} {len(a) / sr:5.2f}s  {c['text']}")


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def align():
    from faster_whisper import WhisperModel
    model = WhisperModel('base.en', device='cpu', compute_type='int8')
    show = spec.get('show', {})
    out, line = [], 0
    for c in spec['clips']:
        a, sr = sf.read(f"vo/{c['key']}.wav")
        a16 = np.interp(np.arange(int(len(a) * 16000 / sr)) * sr / 16000, np.arange(len(a)), a).astype(np.float32)
        mtxt = ''.join(norm(w) for w in c['text'].split())
        best = None
        for prompt in (None, c['text']):  # a prompt helps rare words but can make Whisper hallucinate
            segs, _ = model.transcribe(a16, word_timestamps=True, initial_prompt=prompt)
            ws = [w for s in segs for w in s.words]
            r = difflib.SequenceMatcher(None, mtxt, ''.join(norm(w.word) for w in ws), autojunk=False).ratio()
            if best is None or r > best[0]:
                best = (r, ws)
            if r > .85:
                break
        heard = best[1]
        loud = np.flatnonzero(np.abs(a) > np.abs(a).max() * .05)
        speech_end = loud[-1] / sr if len(loud) else len(a) / sr
        # time of every character of what Whisper heard
        htxt, htime = '', []
        for w in heard:
            n = norm(w.word)
            for i, _ in enumerate(n):
                htime.append(w.start + (w.end - w.start) * i / max(1, len(n)))
            htxt += n
        mine = c['text'].split()
        mtxt = ''.join(norm(w) for w in mine)
        cmap = {}
        for blk in difflib.SequenceMatcher(None, mtxt, htxt, autojunk=False).get_matching_blocks():
            for i in range(blk.size):
                cmap[blk.a + i] = htime[blk.b + i]
        pos, starts = 0, []
        for w in mine:
            n = len(norm(w))
            ts = [cmap[p] for p in range(pos, pos + n) if p in cmap]
            starts.append(ts[0] if ts else None)
            pos += n
        end = max(heard[-1].end if heard else 0, speech_end)
        # fill gaps by interpolation, keep order
        known = [i for i, s in enumerate(starts) if s is not None] or [0]
        if starts[0] is None:
            starts[0] = heard[0].start if heard else 0
        for i in range(len(starts)):
            if starts[i] is None:
                nxt = next((j for j in range(i + 1, len(starts)) if starts[j] is not None), None)
                prv = starts[i - 1]
                starts[i] = prv + ((starts[nxt] if nxt is not None else end) - prv) / ((nxt if nxt is not None else len(starts)) - i + 1)
        # alignment collapsed (Whisper mis-heard the clip): spread words by length over the spoken span
        first = heard[0].start if heard else 0
        if len(mine) > 3 and starts[-1] - starts[0] < .4 * (end - first):
            print(f"  {c['key']}: alignment collapsed (heard: {''.join(w.word for w in heard).strip()!r}), spreading by length")
            lens = np.cumsum([0] + [len(norm(w)) + 2 for w in mine])
            starts = list(first + (end - first) * lens[:-1] / lens[-1])
        # caption pages: break after . ? ! or every ~6 words
        count = 0
        for i, w in enumerate(mine):
            t0 = c['at'] + starts[i]
            t1 = c['at'] + (starts[i + 1] if i + 1 < len(mine) else end)
            word = ' '.join(show.get(p, p) for p in [w]) if w in show else w
            for k, v in show.items():
                word = word.replace(k, v)
            out.append({'w': word, 't0': round(t0, 3), 't1': round(t1, 3), 'line': line})
            count += 1
            if re.search(r'[.?!]$', w) or (count >= 6 and re.search(r'[,;:]$', w)) or count >= 7:
                line += 1; count = 0
        if count:
            line += 1
        print(c['key'], ' '.join(f"{o['w']}@{o['t0']:.2f}" for o in out if o['t0'] >= c['at'] - .01)[:200])
    open('words.js', 'w').write('window.WORDS = ' + json.dumps(out) + ';\n')


{'gen': gen, 'align': align}[sys.argv[1]]()
