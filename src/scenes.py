"""Shot blocking, camera and prop performance for the paper-boat fable."""
import io
from functools import lru_cache
from math import sin,cos,pi
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from art import (cairo, rgb, color, transform, gradient, oval, rect, path, poly,
                 line, boat, cabinet, city, plant, person, hand, photo_front, room,
                 lane, bridge, leaf, waves, rain, INK, CREAM)


def ease(x):
    x=min(1,max(0,x))
    return x*x*(3-2*x)


def part(p,a,b):
    return ease((p-a)/(b-a))


@lru_cache(maxsize=8)
def plate(name):
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,720,1280)
    c=cairo.Context(surface);c.scale(2,2)
    c.set_line_join(cairo.LINE_JOIN_ROUND);c.set_line_cap(cairo.LINE_CAP_ROUND)
    if name=='lane': lane(c)
    elif name=='water':
        gradient(c,'#688a88','#9cbcb0')
        for j in range(32):
            x=(53*j)%399-20;y=(77*j)%700-30
            path(c,f'M {x} {y} C {x+20} {y-6} {x+25} {y+5} {x+50} {y-1}',None,'#82a39a',1.2)
        # Soft reflections of buildings and awnings stretch towards the camera.
        for j in range(7):
            x=j*67-63
            poly(c,[(x,0),(x+37,0),(x+14,90),(x+25,130),(x+3,168),(x+8,112),(x-3,88)],'#809994')
        # Steps, floating blossom heads and water grass frame the close-up.
        for i,col in enumerate(('#c4997c','#b59480','#a18b7a')):
            poly(c,[(0,118+i*21),(52-i*8,88+i*21),(113-i*14,0),(85-i*16,0),(34-i*8,67+i*19),(0,84+i*19)],col)
        for j in range(11):
            x=355+19*sin(j*2);y=625+20*cos(j)
            path(c,f'M {x} {y} C {x-26} {y-15} {x-16-j*4} {y-42-j*2} {x-22-j*4} {y-57-j*2} C {x-10} {y-45} {x+2} {y-22} {x} {y} Z',('#536f65','#648074','#789080')[j%3])
        for x,y in [(37,512),(56,525),(292,136)]:
            for j in range(6):
                oval(c,x+3*cos(j*pi/3),y+3*sin(j*pi/3),2.8,2,'#e2b575')
            oval(c,x,y,2,2,'#b48358')
    else:
        room(c,name=='evening')
        if name in ('collection','photowall'):cabinet(c,name=='collection',name=='photowall')
    return surface


def paint(c,name):
    c.save();c.scale(.5,.5);c.set_source_surface(plate(name),0,0);c.paint();c.restore()


@lru_cache(maxsize=1)
def note():
    w,h=600,520
    im=Image.new('RGBA',(w,h))
    d=ImageDraw.Draw(im)
    font=ImageFont.truetype(os.getenv('DEVANAGARI_FONT','/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf'),61)
    for i,txt in enumerate(['आज मेरी बेटी ने','मुझे नाव चलाना','सिखाया।','— पापा']):
        d.text((w/2,54+i*97),txt,font=font,fill='#4a4945',anchor='mt',language='hi')
    buf=io.BytesIO();im.save(buf,format='PNG');buf.seek(0)
    return cairo.ImageSurface.create_from_png(buf)


@lru_cache(maxsize=1)
def paper_texture():
    rng=np.random.default_rng(315)
    tile=np.zeros((192,192,4),dtype=np.uint8)
    vals=rng.integers(0,2,(192,192),dtype=np.uint8)
    # ARGB32 is premultiplied, native-endian BGRA on little-endian hosts.
    alpha=rng.integers(1,14,(192,192),dtype=np.uint8)
    tile[:,:,3]=alpha
    tile[:,:,:3]=(alpha*vals)[:,:,None]
    surface=cairo.ImageSurface.create_for_data(tile,cairo.FORMAT_ARGB32,192,192)
    pattern=cairo.SurfacePattern(surface);pattern.set_extend(cairo.EXTEND_REPEAT)
    return pattern,tile


def sheen(c):
    c.save();c.rectangle(25,131,309,344);c.clip()
    for x,w in [(43,5),(51,16),(251,3),(261,24)]:
        c.move_to(x,109);c.line_to(x+w,109);c.line_to(x+w-75,486);c.line_to(x-75,486);c.close_path()
        color(c,'#fce1b5',.09);c.fill()
    c.restore()


def water_boat(c,x,y,s,a,t,bent=0):
    for i in range(3):
        q=(t*.64+i/3)%1
        c.save();c.translate(x-4*s,y+8*s);c.scale(1,.18)
        c.arc(0,0,(28+q*41)*s,0,2*pi)
        color(c,'#dce3c3',.55*(1-q));c.set_line_width(2.4);c.stroke();c.restore()
    oval(c,x+2*s,y+11*s,34*s,4*s,'#638983')
    boat(c,x,y,s,a,bent=bent)


def two_shot(c,t,p,offer=False):
    paint(c,'room')
    # Cabinet at the edge of frame anchors the actors in the room from the hook.
    with transform(c,229,53,.64): cabinet(c)
    oval(c,92,477,71,8,'#aa7b63')
    oval(c,248,477,47,6,'#aa7b63')
    person(c,95,288,1.55,True,t,'smile' if offer else 'think',
           .68+.30*part(p,.15,.66),holding=True,talking=offer and p>.53)
    person(c,250,363,.94,False,t,'ask',.62*part(p,.2,.56),True,gaze=1)


def render(c,scene,t,p):
    shot=scene['shot']
    c.set_line_cap(cairo.LINE_CAP_ROUND);c.set_line_join(cairo.LINE_JOIN_ROUND)
    if shot in ('cabinet','photo'):
        zoom=(2.95-1.90*part(p,.05,.9)) if shot=='cabinet' else (1.03+2.05*part(p,.1,.94))
        tight=min(1,(zoom-1.03)/1.65)
        fx,fy=180+24*tight,320+27*tight
        c.save();c.translate(180,317);c.scale(zoom,zoom);c.translate(-fx,-fy)
        paint(c,'collection' if shot=='cabinet' else 'photowall');sheen(c);c.restore()
    elif shot=='glass':
        # A large reflection drop in front of the boat sells the glass barrier.
        c.save();c.translate(184,325);c.scale(3.65+.27*p,3.65+.27*p);c.translate(-204,-350)
        paint(c,'collection');sheen(c)
        x=196+sin(p*pi)*1.3;y=314+43*part(p,.08,.91)
        path(c,f'M {x} {y-6} C {x+1} {y-1} {x+4} {y+2} {x+1} {y+4} C {x-3} {y+6} {x-5} {y+2} {x} {y-6} Z','#b7c5b2','#768c87',.45)
        oval(c,x-1,y+1,.65,1.3,'#f4edd3');c.restore()
    elif shot=='shelf':
        paint(c,'room')
        # A closer cabinet shot makes the repeated protective ritual legible.
        c.save();c.translate(166,297);c.scale(2.15,2.15);c.translate(-204,-350)
        paint(c,'photowall')
        rect(c,181,314,48,40,'#90634c')
        q=part(p,.08,.66);back=part(p,.70,.99)
        bx=176+28*q;by=372-24*q
        boat(c,bx,by,.51,-5*(1-q))
        hand(c,bx-10-55*back,by+3+20*back,.46,9)
        c.restore()
    elif shot=='offer':
        two_shot(c,t,p,True)
    elif shot in ('dad','silence','ask'):
        paint(c,'evening' if shot=='silence' else 'room')
        if shot=='ask':
            with transform(c,210,10,.8): cabinet(c)
            person(c,153,322,2.28,False,t,'ask',.2+.8*part(p,.20,.65),flip=True,talking=p>.24)
        else:
            with transform(c,220,80,.62):cabinet(c)
            gaze=1-2*part(p,.2,.7) if shot=='silence' else 1
            person(c,165,312,2.21,True,t,'think' if shot=='silence' else 'smile',
                   .18+.55*(1-part(p,.2,.68)),holding=shot=='dad',talking=shot=='dad',gaze=gaze)
    elif shot=='rain':
        paint(c,'lane');waves(c,t);rain(c,t,1)
        for i in range(5):
            q=(t*.9+.2*i)%1
            c.save();c.translate(65+51*i,430+22*(i%3));c.scale(1,.24);c.arc(0,0,2+q*11,0,2*pi)
            color(c,'#e3e3c5',.63*(1-q));c.set_line_width(1);c.stroke();c.restore()
    elif shot in ('launch','leaf','help','fix'):
        paint(c,'water');waves(c,t)
        if shot=='launch':
            q=part(p,.08,.49);drift=part(p,.50,1)
            x=104+43*q+76*drift;y=243+94*q+5*sin(p*7)*drift
            water_boat(c,x,y,1.28,-5+4*q+2*sin(t*3)*drift,t)
            hand(c,x-20-160*drift,y-5-78*drift,.89,12,True)
        else:
            x=181+9*sin(p*pi);y=341+sin(t*2)*2
            if shot=='leaf':
                q=part(p,.12,.56);tilt=part(p,.45,.80)
                theta=2+16*tilt
                water_boat(c,x,y,1.51,theta,t,bent=8*tilt)
                leaf(c,x+123-72*q,y-27+35*q,1.15,17+48*q)
            elif shot=='help':
                water_boat(c,x,y,1.51,18+sin(t*2),t,bent=8)
                leaf(c,x+51,y+7,1.15,65)
                q=part(p,.03,.45)-.30*part(p,.64,1)
                hand(c,-35+201*q,279+28*q,1.12,9)
            else:
                q=part(p,.04,.40);release=part(p,.48,.91)
                theta=18*(1-release)
                water_boat(c,x,y,1.51,theta,t,bent=8-14*release)
                leaf(c,x+51+66*release,y+7+31*release,1.15,65+83*release)
                with transform(c,360,0,1,flip=True):
                    hand(c,17+101*q-68*release,276+61*q-41*release,.86,11,True)
    elif shot=='sail':
        if p<.60:
            paint(c,'lane');waves(c,t)
            q=part(p,.01,.60)
            water_boat(c,84+146*q,443-135*q,1.0-.78*q,-3+4*sin(t*2.3),t)
            bridge(c)
        else:
            # Match the bow under the arch, then see it emerge from the reverse side.
            paint(c,'water');waves(c,t)
            q=part(p,.60,.98)
            water_boat(c,160+33*q,269+163*q,.36+.93*q,3*sin(t*2),t)
            path(c,'M 0 0 L 360 0 L 360 289 L 310 302 C 299 149 65 149 46 327 L 0 338 Z','#9f7465','#594f4b',2.3)
            path(c,'M 45 325 C 65 150 298 148 310 301',None,'#cf9c7e',9)
            for xx,yy in [(26,258),(16,196),(53,99),(118,130),(144,76),(241,150),(286,170),(331,229)]:
                line(c,[(xx,yy),(xx+17,yy-1)],'#876858',1.5)
    elif shot=='last':
        paint(c,'room')
        c.save();color(c,'#403e42',.32);c.paint();c.restore()
        flip=part(p,.06,.32)
        with transform(c,180,310,1.63,-6+8*flip):
            c.scale(max(.02,abs(cos(pi*flip))),1)
            if flip<.5:
                photo_front(c,0,0)
            else:
                rect(c,-76,-90,155,187,'#775e51');rect(c,-79,-93,155,187,'#f9e8ba')
                for y in range(-67,73,20):line(c,[(-68,y),(65,y)],'#dcccab',.55)
                c.save();c.translate(-72,-73);c.scale(.24,.24);c.set_source_surface(note(),0,0);c.paint();c.restore()
                boat(c,35,68,.29,-8)
    else:
        raise ValueError(f'Unknown shot {shot}')
    # Printed paper texture stays in screen space; no noisy flicker.
    c.set_source(paper_texture()[0]);c.paint()
