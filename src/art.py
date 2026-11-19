"""Original cut-paper artwork. Everything uses a 360 by 640 design grid."""
from contextlib import contextmanager
from functools import lru_cache
import math
import random
import re
import cairo

INK = '#342f38'
TEAL = '#22776f'
RED = '#e65236'
SUN = '#edb84f'
CREAM = '#ffedbe'
SKIN = '#c77c54'
HAIR = '#342e35'


def rgb(h):
    return tuple(int(h[i:i+2], 16)/255 for i in (1,3,5))


def color(c, h, a=1):
    c.set_source_rgba(*rgb(h), a)


@contextmanager
def transform(c, x=0, y=0, scale=1, angle=0, flip=False):
    c.save()
    c.translate(x,y)
    c.rotate(math.radians(angle))
    c.scale(-scale if flip else scale, scale)
    try:
        yield
    finally:
        c.restore()


def finish(c, fill, edge=None, w=1):
    if fill:
        color(c,fill)
        c.fill_preserve()
    if edge:
        color(c,edge)
        c.set_line_width(w)
        c.stroke()
    else:
        c.new_path()


def rect(c,x,y,w,h,fill):
    c.rectangle(x,y,w,h)
    finish(c,fill)


def oval(c,x,y,rx,ry,fill,edge=None,w=1):
    if rx <= 0 or ry <= 0:
        return
    c.save()
    c.translate(x,y)
    c.scale(rx,ry)
    c.arc(0,0,1,0,2*math.pi)
    c.restore()
    finish(c,fill,edge,w)


@lru_cache(maxsize=1024)
def commands(s):
    return [(cmd,tuple(map(float,re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',values))))
            for cmd,values in re.findall(r'([MLCZ])([^MLCZ]*)',s)]


def path(c,s,fill=None,edge=None,w=1):
    for cmd,vals in commands(s):
        if cmd=='M': c.move_to(*vals)
        elif cmd=='L': c.line_to(*vals)
        elif cmd=='C': c.curve_to(*vals)
        else: c.close_path()
    finish(c,fill,edge,w)


def poly(c,points,fill,edge=None,w=1):
    c.move_to(*points[0])
    for pt in points[1:]: c.line_to(*pt)
    c.close_path()
    finish(c,fill,edge,w)


def line(c,points,ink,w):
    c.move_to(*points[0])
    for pt in points[1:]: c.line_to(*pt)
    finish(c,None,ink,w)


def gradient(c,top,bottom,y1=0,y2=640):
    g=cairo.LinearGradient(0,y1,0,y2)
    g.add_color_stop_rgb(0,*rgb(top))
    g.add_color_stop_rgb(1,*rgb(bottom))
    c.rectangle(-700,-600,1900,1900)
    c.set_source(g)
    c.fill()


def boat(c,x,y,size=1,angle=0,palette=None,bent=0):
    a,b,d,light=palette or ('#ef6846','#b63e36','#872f35','#ffcb86')
    with transform(c,x,y,size,angle):
        poly(c,[(-46,-8),(-23,-13),(-3,-6),(37,-14),(45,-13+bent),(27,9),(-25,11)],b,INK,1.25)
        poly(c,[(-27,-5),(3,-30),(11,-4),(-3,2)],light,INK,1.15)
        poly(c,[(3,-30),(20,-10),(11,-4)],a,INK,1)
        poly(c,[(-46,-8),(-9,1),(45,-13+bent),(25,11),(-25,11)],a,INK,1.25)
        poly(c,[(-9,1),(45,-13+bent),(25,11)],d)
        line(c,[(-40,-6),(-9,3),(38,-10+bent)],light,.9)
        line(c,[(-10,1),(-23,9)],b,1)


def leaf(c,x,y,scale=1,a=0):
    with transform(c,x,y,scale,a):
        path(c,'M -13 1 C -8 -10 6 -10 15 -3 C 9 7 -3 11 -13 1 Z','#db9d38','#775b38',1)
        path(c,'M -17 4 C -5 1 6 -4 12 -3',None,'#855a30',1)


def city(c, night=False):
    rng=random.Random(14)
    for j in range(2):
        x=-20
        while x<381:
            w=rng.randrange(22,55)
            y=rng.randrange(180,245)+j*40
            col=('#a7a69d','#c49d88','#a5a698','#bd9f91')[rng.randrange(4)]
            if night: col=('#747d91','#85869a','#87889a','#727f88')[rng.randrange(4)]
            rect(c,x,y,w,365-y,col)
            rect(c,x-1,y,w+2,3,'#6c7b7b' if night else '#b69582')
            for yy in range(y+11,322,18):
                for xx in range(x+5,x+w-3,10):
                    rect(c,xx,yy,4,8,'#b9a17d' if night else '#858e89')
            if rng.random()<.6:
                rect(c,x+w/3,y-11,9,11,col)
                line(c,[(x+w*.65,y),(x+w*.65,y-22)],'#85877f',1)
            x+=w+1


def plant(c,x,y,sc=1):
    with transform(c,x,y,sc):
        for i,(dx,dy) in enumerate([(-42,-73),(24,-99),(-20,-120),(45,-52),(4,-72)]):
            path(c,f'M 0 0 C -5 -20 {dx} {dy+12} {dx} {dy}',None,'#435a47',2.2)
            for k in (0,1):
                with transform(c,dx*(1-.25*k),dy*(1-.25*k),.8 if k else 1,(-50 if i%2 else 44)+k*20):
                    path(c,'M 0 0 C -17 -2 -18 -17 -16 -25 C -4 -21 3 -10 0 0 Z',
                         '#456759' if i%2 else '#668466')
                    line(c,[(0,0),(-13,-20)],'#96a178',.7)
        path(c,'M -21 -10 L 22 -10 L 15 24 L -14 24 Z','#b75e3f',INK,1.4)
        rect(c,-23,-14,47,7,'#df9161')


def room(c,night=False):
    gradient(c,'#d3b497' if not night else '#a5999a','#f6d69e' if not night else '#c7b2a6')
    # Sunlit plaster, high picture rail, tile floor and an arched window.
    rect(c,0,71,360,3,'#c69f78' if not night else '#988b91')
    rect(c,0,77,360,1,'#f1cf9e')
    rect(c,0,418,360,222,'#bf8063' if not night else '#8d7679')
    rect(c,0,412,360,9,'#916b58')
    for i in range(-400,701,68):
        line(c,[(180+(i-180)*.5,421),(i,640)],'#a67661',1)
    for yy in (438,465,508,568,637):
        line(c,[(0,yy),(360,yy)],'#a67661',1)
    c.save()
    pathdef='M 10 365 L 10 161 C 10 85 128 85 128 161 L 128 365 Z'
    path(c,pathdef,'#796454',INK,2)
    c.move_to(18,357);c.line_to(18,162);c.curve_to(18,97,120,97,120,162);c.line_to(120,357);c.close_path();c.clip()
    gradient(c,'#92b5b2' if not night else '#858da7','#f1cb99' if not night else '#c3b2b0',105,360)
    oval(c,80,175,23,23,'#f7dda2' if not night else '#d2c6b6')
    city(c,night)
    c.restore()
    rect(c,65,109,5,255,'#726556');rect(c,15,231,110,4,'#726556')
    rect(c,4,361,131,7,'#705147');rect(c,1,361,137,3,'#e5b77f')
    plant(c,22,414,.75)
    for x in (145,331):
        line(c,[(x,90),(x,395)],'#dbb995',1)
    wallart(c,251,168)


def wallart(c,x,y):
    with transform(c,x,y):
        rect(c,0,0,64,78,'#9e775d');rect(c,-3,-4,64,77,'#685247');rect(c,1,0,56,69,'#f4d9aa')
        oval(c,34,24,11,11,'#ce7152')
        poly(c,[(6,58),(25,27),(43,58)],'#809984')
        poly(c,[(23,58),(40,37),(51,58)],'#4e756a')


def cabinet(c,red=True,photo=False):
    # Four rows. Leave exactly one of the twenty-four places empty.
    rect(c,18,124,330,388,'#aa8062')
    rect(c,11,115,338,386,'#573e36')
    rect(c,14,118,332,377,'#a25f43')
    rect(c,23,130,314,346,'#594239')
    for row in range(4):
        y=193+row*81
        rect(c,26,y-60,308,58,('#996c52','#a97756','#90634c','#91664b')[row])
        for i in range(6):
            if (row,i)==(3,5): continue
            x=53+50.5*i
            if (row,i)==(2,3):
                if red: boat(c,x,y-6,.51)
                elif photo: photo_front(c,x,y-19,.23,-5)
            else:
                palettes=[('#f0d39b','#b69b73','#b49467','#fae9bf'),('#b7c7ad','#91a98f','#809781','#e2dfb3'),('#e8b77f','#c58b61','#ad795b','#f1d3a0')]
                boat(c,x,y-6,.47,((i+row)%3-1)*2,palettes[(i+2*row)%3])
        rect(c,23,y+1,314,5,'#da9a68');rect(c,23,y+6,314,6,'#704637')
    # Fine end-grain etching and a brass finger pull on the bottom rail.
    for yy in (124,201,282,363,444,489):
        for i in range(4):
            x=35+79*i
            path(c,f'M {x} {yy} C {x+14} {yy-1.5} {x+33} {yy+2} {x+47} {yy}',None,'#ae7554',.65)
    rect(c,15,476,330,9,'#dd9a69')
    rect(c,164,477,32,3,'#87623e')
    oval(c,180,480,9,2,'#e6b963','#7f5c3c',.7)
    for x in [30,314]: rect(c,x,496,12,23,'#654b40')
    for x in [20,334]: rect(c,x,125,4,351,'#d99665')
    for x in (34,324):
        oval(c,x,483,1.6,1.6,'#f4d49d')


def photo_front(c,x,y,s=1,a=0):
    with transform(c,x,y,s,a):
        rect(c,-68,-76,140,157,'#795b49')
        rect(c,-72,-80,140,156,'#fff0ca')
        c.save();c.rectangle(-63,-70,122,119);c.clip()
        rect(c,-63,-70,122,119,'#87a9a3')
        path(c,'M -65 -62 L 60 -64 L 60 -15 C 25 -16 15 -44 -10 -30 C -40 -10 -48 -23 -65 -13 Z','#526c71')
        for yy in (0,13,30): line(c,[(-52,yy),(44,yy-5)],'#add0b7',1.5)
        boat(c,2,15,.77,-6)
        c.restore()
        line(c,[(-13,62),(22,62)],'#c7b595',1)


def bridge(c,close=False):
    with transform(c,202,303,1.30 if close else 1):
        path(c,'M -85 -19 L 97 -28 L 103 32 L 61 34 C 59 -6 -5 -7 -16 37 L -80 43 Z','#ad7866','#655a58',2)
        path(c,'M -82 -21 L 98 -29 L 98 -21 L -83 -13 Z','#e2b089','#76615e',1)
        for xx in range(-70,95,17):
            line(c,[(xx,-21-(xx+70)*.043),(xx,-37-(xx+70)*.043)],'#675d5a',2)
        line(c,[(-84,-38),(99,-46)],'#6c6260',3)
        for xx,yy in [(-66,4),(-42,20),(70,0),(84,17),(-53,-5)]:
            line(c,[(xx,yy),(xx+8,yy)],'#8d695e',1.5)


def lane(c):
    gradient(c,'#7b93a5','#dbb5a3',0,340)
    oval(c,230,144,35,35,'#d4beb1')
    city(c,True)
    rect(c,0,328,360,312,'#729998')
    poly(c,[(0,260),(41,287),(123,309),(204,321),(72,349),(0,409)],'#aa7e6c')
    poly(c,[(0,343),(78,321),(136,314),(201,321),(63,355),(0,401)],'#dfb08e')
    poly(c,[(360,261),(279,301),(245,323),(360,389)],'#91776c')
    for x,y,s in [(39,287,.24),(0,311,.48),(322,287,.18)]:
        plant(c,x,y,s)
    for j in range(52):
        r=random.Random(j+20);x=r.uniform(0,360);y=r.uniform(349,640)
        path(c,f'M {x} {y} C {x+5} {y-2} {x+15} {y-2} {x+24} {y-4}',None,'#88aaa3',.8)
    bridge(c)


def rain(c,t,strength=1):
    rng=random.Random(33)
    for j in range(int(75*strength)):
        x,y=rng.random()*390,rng.random()*660
        speed=rng.uniform(110,230)
        xx=(x-t*speed*.28)%380-7; yy=(y+t*speed)%670-15
        c.move_to(xx,yy);c.line_to(xx-2,yy+8)
    color(c,'#eff2d4',.44);c.set_line_width(.8);c.stroke()


def waves(c,t,base=0):
    rng=random.Random(17)
    for j in range(22):
        x=(rng.random()*400 + t*(3+j%4))%400-20
        y=base+rng.uniform(255,590)
        length=rng.uniform(4,26)
        path(c,f'M {x} {y} C {x+6} {y-1.5} {x+length*.6} {y+1.5} {x+length} {y-1}',None,'#b1c7b4',.9)

def arm(c,x,y,angle,bend,sleeve,skin=SKIN):
    """Two connected rigid bones, returning the palm in character coordinates."""
    length=25
    with transform(c,x,y,1,angle):
        path(c,'M -8 -2 C -8 -9 7 -10 8 -2 L 7 23 L -7 23 Z',sleeve,INK,1.4)
        with transform(c,0,23,1,bend):
            path(c,'M -5 -1 L 5 -1 L 5 21 C 11 24 7 32 1 32 C -5 32 -7 28 -5 21 Z',skin,INK,1.3)
            line(c,[(3,24),(5,22)],'#94583e',.8)
    a,b=map(math.radians,(angle,angle+bend))
    return (x-23*math.sin(a)-length*math.sin(b),y+23*math.cos(a)+length*math.cos(b))


def face(c,dad,t,mood,gaze,talking,tilt):
    with transform(c,0,-14,1,tilt):
        if not dad:
            oval(c,-19,-22,17,22,HAIR,INK,1.6)
            oval(c,-25,-35,13,14,HAIR,INK,1.3)
            path(c,'M -35 -32 C -32 -48 -18 -48 -15 -37',None,'#75605a',1.3)
            path(c,'M -29 -21 C -24 -28 -17 -28 -13 -23',None,'#e7a741',3)
        path(c,'M -24 -16 C -25 -33 -7 -44 10 -38 C 25 -34 30 -20 28 -5 C 28 3 33 6 28 8 L 25 9 C 24 25 10 31 -5 28 C -17 26 -25 11 -24 -16 Z',
             '#d79368' if not dad else '#bf7a54',INK,1.7)
        oval(c,-23,2,5,7,'#cd8763',INK,1.3)
        path(c,'M -24 3 C -22 -1 -20 0 -20 4',None,'#92573e',1)
        if dad:
            path(c,'M -23 6 C -27 -7 -32 -26 -18 -37 C -5 -48 7 -39 19 -45 C 17 -39 27 -39 30 -32 C 31 -25 23 -21 16 -22 C 8 -27 3 -25 -8 -22 C -12 -14 -16 -13 -19 -15 L -19 4 Z',HAIR,INK,1.7)
            path(c,'M -20 -29 C -10 -40 7 -31 16 -38',None,'#796457',1.6)
        else:
            path(c,'M -24 1 C -31 -13 -27 -32 -13 -39 C 3 -48 30 -36 30 -18 C 20 -15 13 -21 7 -28 C 1 -20 -8 -14 -16 -14 L -19 1 Z',HAIR,INK,1.5)
            path(c,'M -20 -23 C -16 -30 -6 -35 1 -35',None,'#78605b',1.2)
            oval(c,-23,10,2.5,3,'#f7bf50',INK,.7)
        blink=(t+(.73 if dad else .16))%3.58
        shut=abs(blink-.13)<.085
        for i,xx in enumerate((-3,17)):
            eye_y=-6+i*.5
            if shut:
                path(c,f'M {xx-4} {eye_y} C {xx-1} {eye_y+2} {xx+2} {eye_y+2} {xx+4} {eye_y}',None,INK,1.4)
            else:
                oval(c,xx,eye_y,4.2,4.8 if mood!='think' else 3.6,'#ffefd1',INK,.9)
                oval(c,xx+gaze*1.7,eye_y+.8,2,2.7,INK)
                oval(c,xx+gaze*1.7+.65,eye_y-.2,.65,.65,'#fff2d3')
            brow=-15-(2.1 if mood=='ask' and i else 0)
            path(c,f'M {xx-5} {brow+1} C {xx-1} {brow-2} {xx+2} {brow-2} {xx+5} {brow}',None,HAIR,1.8)
        if dad:
            for xx in (-3,17):
                oval(c,xx,-6,8,7,None,'#564442',1.35)
            line(c,[(5,-7),(9,-7)],'#564442',1.3)
            line(c,[(-11,-7),(-20,-11)],'#564442',1.35)
            path(c,'M 3 11 C 8 4 11 8 13 8 C 16 6 21 8 23 10 C 20 14 16 14 12 11 C 8 15 4 14 3 11 Z',HAIR)
        path(c,'M 9 -4 C 9 1 13 3 12 5 L 9 6',None,'#995f44',1)
        oval(c,-10,7,4.5,2.7,'#c47e62')
        if talking and math.sin(t*18)>.05:
            oval(c,12,17,4,1.8+1.1*math.sin(t*18),'#63473e')
        else:
            path(c,'M 7 17 C 11 19 16 19 19 15' if mood in ('smile','ask') else 'M 9 18 C 11 17 14 17 17 18',None,INK,1.2)


def person(c,x,y,s,dad,t,mood='smile',gesture=0,flip=False,holding=False,talking=False,gaze=1):
    """Origin is the shoulder center. Planted feet remain fixed during upper-body acting."""
    with transform(c,x,y,s,flip=flip):
        pants='#3c5053' if dad else '#7b4941'
        for xx in (-13,12):
            rect(c,xx-5,73,11,40,pants)
            path(c,f'M {xx-7} 111 L {xx+6} 111 C {xx+9} 116 {xx+14} 113 {xx+16} 119 L {xx-8} 119 Z','#4b3e39',INK,1.4)
        breathe=.7*math.sin(t*2.2)
        with transform(c,0,breathe):
            sleeve='#5e998d' if dad else '#e4a840'
            arm(c,-19,20,15+2*math.sin(t*1.7),-13,sleeve)
            if dad:
                path(c,'M -12 10 C -22 13 -26 22 -25 32 L -21 84 C -7 90 12 88 24 83 L 22 27 C 22 14 11 9 7 9 Z','#599184',INK,1.7)
                path(c,'M -15 13 L -4 23 L 2 16 L 9 24 L 15 13','#b0c2a6',INK,1)
                line(c,[(2,19),(3,50)],'#316a63',1)
                for yy in (28,36,44):oval(c,4,yy,1,1,'#f2cf8e')
                path(c,'M -15 40 L -5 40 L -6 48 L -12 50 Z',None,'#3f766c',1)
                line(c,[(-19,80),(19,80)],'#99b299',1.4)
            else:
                path(c,'M -11 11 C -17 12 -22 17 -24 26 L -14 34 L -20 53 L -30 83 C -14 91 14 93 30 84 L 19 48 L 19 29 L 24 23 C 20 15 9 10 7 10 Z','#ecb34c',INK,1.6)
                path(c,'M -11 12 C -8 24 7 25 12 13',None,'#f6d88e',3)
                path(c,'M -24 80 C -8 88 13 89 25 81',None,'#b56840',3)
                for xx,yy in [(-5,38),(9,48),(-11,58),(1,72),(14,67)]:
                    poly(c,[(xx,yy-2),(xx+2,yy),(xx,yy+3),(xx-2,yy)],'#d18a42')
            wrist=arm(c,14,22,-10-62*gesture,-12-18*gesture,sleeve)
            if holding:
                boat(c,wrist[0]+10,wrist[1]-7,.49 if dad else .44,-4)
            face(c,dad,t,mood,gaze,talking,(-3 if mood=='ask' else 2)+math.sin(t*1.5)*1.1)


def hand(c,x,y,s=1,a=0,child=False):
    """Hand reaching diagonally from screen left; origin is the fingertips."""
    with transform(c,x,y,s,a):
        path(c,'M -127 -1 L -63 -6 L -48 -11 C -40 -18 -31 -22 -23 -24 C -17 -24 -17 -20 -23 -16 L -33 -8 L -9 -9 C -1 -10 3 -6 -2 -3 L -18 1 C -11 2 -12 7 -18 8 L -29 13 C -36 16 -49 16 -57 12 L -126 23 Z',
             '#da966e' if child else '#be7956',INK,1.7)
        path(c,'M -450 -10 L -72 -8 L -68 18 L -450 31 Z','#e5aa46' if child else '#60978d',INK,1.6)
        line(c,[(-76,-6),(-73,19)],'#ebcc92',2)
        path(c,'M -30 6 C -22 5 -18 3 -16 3',None,'#a36a4f',.9)
