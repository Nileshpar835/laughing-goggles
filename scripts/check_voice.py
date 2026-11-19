"""Synthesize a short test to check model, language, voice and phonemizer together."""
from pathlib import Path
import numpy as np
import onnxruntime as ort
from kokoro_onnx import Kokoro
m=Path(__file__).resolve().parents[1]/'models'
o=ort.SessionOptions()
o.intra_op_num_threads=2
o.inter_op_num_threads=1
s=ort.InferenceSession(str(m/'kokoro-v1.0.int8.onnx'),sess_options=o,providers=['CPUExecutionProvider'])
k=Kokoro.from_session(s,str(m/'voices-v1.0.bin'))
y,sr=k.create('मेरी नाव।',voice='hm_omega',lang='hi',speed=1.)
assert sr==24000 and len(y)>sr*.2 and np.isfinite(y).all() and np.max(np.abs(y))>.01
print('Hindi voice test passed.')
