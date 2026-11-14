"""Word timestamps for an audio file with faster-whisper: prints JSON [[word, start, end], ...]."""
import json, sys
from faster_whisper import WhisperModel
try:
    m = WhisperModel("small.en", device="cuda", compute_type="float16")
    segs, _ = m.transcribe(sys.argv[1], language="en", word_timestamps=True, beam_size=5)
    segs = list(segs)
except Exception as e:
    print("cuda failed, cpu:", e, file=sys.stderr)
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(sys.argv[1], language="en", word_timestamps=True, beam_size=5)
    segs = list(segs)
json.dump([[w.word.strip(), w.start, w.end] for s in segs for w in s.words], open(sys.argv[2], "w"))
print("words", sum(len(s.words) for s in segs), file=sys.stderr)
