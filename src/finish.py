"""Measure the mix, apply a two-pass loudness adjustment, mux the optional Hindi track."""
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'output'

def main():
    spec='loudnorm=I=-15:TP=-1.5:LRA=8'
    f=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(O/'mix.wav'),'-af',spec+':print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    stats=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',f.stderr)[-1])
    opts={'measured_I':'input_i','measured_TP':'input_tp','measured_LRA':'input_lra','measured_thresh':'input_thresh','offset':'target_offset'}
    filt=spec+''.join(':'+k+'='+stats[v] for k,v in opts.items())+':linear=true'
    subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(O/'picture.mp4'),'-i',str(O/'mix.wav'),'-i',str(O/'hindi.srt'),'-map','0:v','-map','1:a','-map','2:s','-af',filt,'-c:v','copy','-c:a','aac','-ar','48000','-b:a','160k','-c:s','mov_text','-metadata:s:a:0','language=hin','-metadata:s:s:0','language=hin','-disposition:s:0','0','-movflags','+faststart',str(O/'Meera_ki_23_Naavein.mp4')],check=True)

if __name__=='__main__':main()
