"""Validate delivered streams, full decoding and frame-accurate scene boundaries."""
import json
import re
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'output'
clip=out/'Meera_ki_23_Naavein.mp4'
def run(*cmd):
    return subprocess.run(cmd,capture_output=True,text=True,check=True)
info=json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',str(clip)).stdout)
v,a,s=info['streams']
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p' and v['r_frame_rate']=='30/1'
assert 16*v['width']==9*v['height'] and a['codec_name']=='aac' and s['codec_name']=='mov_text'
t=json.loads((out/'timing.json').read_text())
assert float(v['nb_frames'])==round(t['duration_s']*30)
assert abs(float(v['duration'])-float(a['duration']))<.1
end=0
for scene in t['scenes']:
    assert abs(scene['start_s']-end)<1e-8
    assert end<scene['speech_end_s']<=scene['end_s']
    end=scene['end_s']
assert abs(end-t['duration_s'])<1e-8
run('ffmpeg','-v','error','-xerror','-i',str(clip),'-map','0:v','-map','0:a','-f','null','-')
log=run('ffmpeg','-hide_banner','-i',str(clip),'-map','0:a','-af','ebur128=peak=true','-f','null','-').stderr.split('Summary:')[-1]
report=dict(size=[v['width'],v['height']],fps=30,frames=int(v['nb_frames']),seconds=float(info['format']['duration']),video='H.264 yuv420p',audio='AAC stereo',subtitle='Hindi, selectable',scenes=len(t['scenes']),integrated_lufs=float(re.search(r'I:\s*([-\d.]+) LUFS',log)[1]),true_peak_dbtp=float(re.search(r'Peak:\s*([-\d.]+)',log)[1]),decode='complete')
(out/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
