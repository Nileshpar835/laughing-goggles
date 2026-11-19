"""Produce timestamped thumbnails and media metadata for a user-supplied video."""
import argparse
import io
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def main():
    a=argparse.ArgumentParser()
    a.add_argument('input',type=Path);a.add_argument('output_dir',type=Path)
    opt=a.parse_args()
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(opt.input)]))
    d=float(next((s['duration'] for s in info['streams'] if s['codec_type']=='video' and 'duration' in s),info['format']['duration']))
    end=max(0,d-.12)
    times=sorted(set(round(min(end,max(0,t)),1) for t in [0,.8,2.3,4,7,12,16]+[d*i/10 for i in range(2,10)]+[end-4,end-2,end]))
    dest=opt.output_dir;dest.mkdir(parents=True,exist_ok=True)
    (dest/'probe.json').write_text(json.dumps(info,indent=2))
    sheet=Image.new('RGB',(6*140,((len(times)+5)//6)*244),'#eee4d4');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        image=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(opt.input),'-frames:v','1','-vf','scale=132:218:force_original_aspect_ratio=decrease','-c:v','png','-f','image2pipe','-'])
        frame=Image.open(io.BytesIO(image)).convert('RGB')
        x=(i%6)*140;y=(i//6)*244
        sheet.paste(frame,(x+(140-frame.width)//2,y));draw.text((x+9,y+220),f'{t:05.1f} s',fill='#3a3530')
    sheet.save(dest/'frames.jpg',quality=88)

if __name__=='__main__': main()
