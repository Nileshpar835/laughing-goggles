"""Compose the original score and Foley at the measured action cues. No audio stock."""
import json
import wave
from pathlib import Path
import subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
R=24000


def main():
    data=json.loads((OUT/'timing.json').read_text())
    with wave.open(str(OUT/'narration.wav'),'rb') as f:
        assert f.getframerate()==R and f.getnchannels()==1
        y=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
    rng=np.random.default_rng(124)
    bed=np.zeros((len(y),2))
    cues={s['shot']:s for s in data['scenes']}
    def place(start,signal,pan=0):
        k=round(start*R)
        if k>=len(y): return
        sound=signal[:len(y)-k]
        bed[k:k+len(sound)]+=sound[:,None]*np.sqrt([(1-pan)/2,(1+pan)/2])
    def note(start,freq,seconds,level,pan=0):
        t=np.arange(round(seconds*R))/R
        signal=sum(a*np.sin(2*np.pi*freq*h*t)*np.exp(-t*(1.5+h*.7)) for h,a in [(1,1),(2,.42),(3.01,.17)])
        env=np.minimum(1,t/.009)*np.minimum(1,(seconds-t)/.07)
        place(start,signal*env*level,pan)
        place(start+.115,signal*env*level*.16,-pan)
    def when(shot,u):
        s=cues[shot];return s['start_s']+u*(s['end_s']-s['start_s'])
    motif=[(0,293.66),(.66,349.23),(1.57,440),(2.50,392)]
    for cycle,start in enumerate(np.arange(.18,len(y)/R-1,5.65)):
        if when('silence',0)<start<when('offer',0): continue
        shift=[1,.89,.75,1.125][cycle%4]
        for j,(delay,freq) in enumerate(motif):
            note(start+delay,freq*shift,1.6,.029,(-1)**j*.37)
        note(start,146.83*shift,2.7,.034,-.16)
    # A narrow rain bed grows as the lane fills and recedes before the photograph.
    start=when('rain',.03);finish=when('photo',0)
    rt=np.arange(round((finish-start)*R))/R
    noise=rng.normal(size=len(rt))
    soft=np.convolve(noise,np.ones(16)/16,'same')
    envelope=np.clip(rt/1.8,0,1)*np.clip((finish-start-rt)/1.8,0,1)
    place(start,soft*envelope*.029,.15)
    for shot,u,f in [('glass',.85,830),('launch',.5,410),('leaf',.55,290),('fix',.61,560),('sail',.78,740)]:
        ts=when(shot,u); tt=np.arange(round(.23*R))/R
        drop=np.sin(2*np.pi*(f*tt-160*tt**2))*np.exp(-25*tt)*np.minimum(1,tt/.004)
        place(ts,drop*.047,.15)
    for shot,u in [('shelf',.61),('offer',.28),('fix',.4),('last',.20)]:
        tt=np.arange(round(.21*R))/R
        paper=rng.normal(size=len(tt));paper=np.diff(paper,prepend=0)
        place(when(shot,u),paper*.008*np.sin(np.pi*tt/.21)**2,-.23)
    # Conservative sidechain leaves words clear. Fade the instrumental tail.
    rms=np.sqrt(np.convolve(y*y,np.ones(1200)/1200,'same'))
    bed*=np.clip(1-rms*4,.49,1)[:,None]
    bed*=np.minimum(1,np.arange(len(y))[::-1]/(R*.55))[:,None]
    mix=y[:,None]*.9+bed
    buf=np.round(mix*(28000/max(1,np.max(np.abs(mix))))).astype('<i2')
    with wave.open(str(OUT/'mix.wav'),'wb') as f:
        f.setparams((2,2,R,0,'NONE','not compressed'));f.writeframes(buf.tobytes())

if __name__=='__main__':main()
