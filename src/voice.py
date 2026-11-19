"""Create the clean voice, measured cue sheet and Hindi SRT."""
import json
import os
from pathlib import Path

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
MODELS = Path(os.getenv("KOKORO_MODELS", ROOT / "models"))
VOICE = "hm_omega"
FPS = 30
SR = 24000


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, rem = divmod(milliseconds, 3600000)
    minutes, rem = divmod(rem, 60000)
    seconds, milliseconds = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def main():
    OUT.mkdir(exist_ok=True)
    settings = ort.SessionOptions()
    settings.intra_op_num_threads = 3
    settings.inter_op_num_threads = 1
    sess = ort.InferenceSession(str(MODELS / "kokoro-v1.0.int8.onnx"),
                                sess_options=settings, providers=["CPUExecutionProvider"])
    engine = Kokoro.from_session(sess, str(MODELS / "voices-v1.0.bin"))
    story = json.loads((ROOT / "assets/story.json").read_text())
    chunks, cues, subtitles = [], [], []
    cursor = 0
    for idx, line in enumerate(story, 1):
        y, rate = engine.create(line["spoken"], voice=VOICE, lang="hi", speed=line["speed"])
        if rate != SR or not len(y):
            raise ValueError("Unexpected or empty voice output")
        active = np.flatnonzero(np.abs(y) > .006)
        if len(active) == 0:
            raise ValueError("Silent voice segment")
        y = y[max(0, active[0]-720):min(len(y), active[-1]+1680)].copy()
        y[:72] *= np.linspace(0, 1, 72)
        y[-72:] *= np.linspace(1, 0, 72)
        start = cursor / SR
        end = (cursor + len(y)) / SR
        frames = int(np.ceil((len(y) + line["pause"] * SR) / (SR / FPS)))
        count = frames * (SR // FPS)
        chunks.extend([y, np.zeros(count - len(y), np.float32)])
        cursor += count
        cues.append(dict(**line, start_s=start, speech_end_s=end, end_s=cursor/SR))
        subtitles.append(f"{idx}\n{timestamp(start)} --> {timestamp(end)}\n{line['spoken']}\n")
        print(idx, line["shot"], round(end-start,2), flush=True)
    sf.write(OUT/"narration.wav", np.concatenate(chunks), SR, subtype="PCM_16")
    (OUT/"timing.json").write_text(json.dumps(dict(voice=VOICE, engine="kokoro-onnx",
        language="hi", timing="measured whole phrases", fps=FPS, duration_s=cursor/SR,
        scenes=cues), ensure_ascii=False, indent=2))
    (OUT/"hindi.srt").write_text("\n".join(subtitles),encoding="utf-8")

if __name__ == "__main__":
    main()
