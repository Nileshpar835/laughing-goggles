"""Recover missing model files from their pinned release, checking SHA-256 first."""
import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from urllib.request import urlopen

m=Path(__file__).resolve().parents[1]/'models'
base='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
for record in (m/'SHA256SUMS').read_text().splitlines():
    digest,name=record.split()
    target=m/name
    if target.is_file():
        continue
    with tempfile.NamedTemporaryFile(dir=m,delete=False) as f: temp=Path(f.name)
    try:
        with urlopen(base+name,timeout=90) as src,temp.open('wb') as dst:
            shutil.copyfileobj(src,dst)
        if hashlib.sha256(temp.read_bytes()).hexdigest()!=digest:
            raise ValueError(f'Model checksum failed for {name}')
        os.replace(temp,target)
    finally:
        temp.unlink(missing_ok=True)
