"""Voice-over clips (Kokoro af_heart, en-us) -> vo/<key>.wav; prints durations."""
import soundfile as sf
from kokoro_onnx import Kokoro

CLIPS = {
    'threeam': "Three a.m.",
    'awake': "Wide awake. Again.",
    'hot': "Hot.",
    'foggy': "Foggy.",
    'flat': "Flat.",
    'wired': "Tired, but wired.",
    'peri': "Perimenopause can bring changes that come and go.",
    'pattern': "Written down, day by day, a pattern can appear.",
    'book': "The Perimenopause Companion. A guide, plus a thirty-day printable workbook.",
    'summary': "And a thirty-day summary, ready for the appointment.",
    'end': "Sage and Season. Link in bio.",
}
k = Kokoro('/root/tts-models/kokoro-v1.0.onnx', '/root/tts-models/voices-v1.0.bin')
for key, s in CLIPS.items():
    a, sr = k.create(s, voice='af_heart', speed=0.92, lang='en-us')
    sf.write(f'vo/{key}.wav', a, sr)
    print(key, round(len(a) / sr, 2))
