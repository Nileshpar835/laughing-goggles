"""Render the vertical short, or request an excerpt using --start and --seconds."""
import argparse
import bisect
import json
import subprocess
from pathlib import Path
import cairo
from scenes import render

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--width',type=int,default=720)
    args.add_argument('--start',type=float,default=0)
    args.add_argument('--seconds',type=float)
    args.add_argument('--out',type=Path,default=OUT/'picture.mp4')
    opt=args.parse_args()
    width=opt.width
    if width%18: raise ValueError('Width must be divisible by 18 for an even 9:16 frame')
    height=width*16//9
    data=json.loads((OUT/'timing.json').read_text()); scenes=data['scenes']; fps=data['fps']
    starts=[s['start_s'] for s in scenes]
    start=round(opt.start*fps);last=round(data['duration_s']*fps)
    if opt.seconds is not None: last=min(last,start+round(opt.seconds*fps))
    if not 0<=start<last: raise ValueError('Invalid excerpt')
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','bgr0',
         '-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264',
         '-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p',
         '-movflags','+faststart',str(opt.out)]
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as enc:
        surface=cairo.ImageSurface(cairo.FORMAT_RGB24,width,height)
        for i in range(start,last):
            t=i/fps;scene=scenes[bisect.bisect_right(starts,t)-1]
            c=cairo.Context(surface);c.scale(width/360,height/640)
            render(c,scene,t,(t-scene['start_s'])/(scene['end_s']-scene['start_s']))
            surface.flush();enc.stdin.write(surface.get_data())
        enc.stdin.close()
        if enc.wait(): raise RuntimeError('Encoder failed')

if __name__=='__main__': main()
