from pathlib import Path
import json, subprocess, shutil
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
BASE=Path(__file__).resolve().parent
SRC=BASE.parent/'screenshots';OUT=BASE.parent/'videos';TMP=BASE/'render-temp'
OUT.mkdir(exist_ok=True);TMP.mkdir(exist_ok=True)
W,H=1440,900
NAVY='#101B2C';WHITE='#F2F6FC';MUTED='#A7B6CC';CORAL='#F28B6D';LIME='#C6DC7D'
fontroot=Path('/usr/share/fonts/truetype/dejavu')
if not fontroot.exists():raise RuntimeError('Install DejaVu Sans fonts, ffmpeg and Poppler before rendering.')
pdfmetrics.registerFont(TTFont('Sans',str(fontroot/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('Bold',str(fontroot/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('Mono',str(fontroot/'DejaVuSansMono.ttf')))
def text(c,s,x,y,width,size=20,color=WHITE,font='Sans',leading=None):
    c.setFillColor(HexColor(color));c.setFont(font,size)
    lead=leading or size*1.42
    for para in s.split('\n'):
        line=''
        for word in para.split():
            trial=(line+' '+word).strip()
            if pdfmetrics.stringWidth(trial,font,size)>width and line:
                c.drawString(x,y,line);y-=lead;line=word
            else:line=trial
        c.drawString(x,y,line);y-=lead
    return y

def box(c,x,y,w,h,fill,radius=18):
    c.setFillColor(HexColor(fill));c.roundRect(x,y,w,h,radius,fill=1,stroke=0)

def img(c,path,x,y,w,h):
    im=ImageReader(str(path));iw,ih=im.getSize();scale=min(w/iw,h/ih)
    dw,dh=iw*scale,ih*scale
    c.drawImage(im,x+(w-dw)/2,y+(h-dh)/2,dw,dh)

def start(c,project,title,n,accent):
    c.setFillColor(HexColor(NAVY));c.rect(0,0,W,H,fill=1,stroke=0)
    box(c,42,H-68,6,30,accent,3)
    text(c,'ANA GOMES / SALESFORCE + APEX + LWC',64,H-55,1200,18,MUTED,'Bold')
    text(c,title,42,H-130,1350,38,WHITE,'Bold')
    text(c,project,42,34,1150,14,MUTED)
    text(c,f'{n:02d}',W-86,34,45,16,accent,'Bold')

def screenshot_page(c,project,title,shot,heading,body,n,accent):
    start(c,project,title,n,accent)
    box(c,42,104,960,640,'#FFFFFF',14);img(c,shot,42,104,960,640)
    text(c,heading,1040,715,350,25,accent,'Bold')
    text(c,body,1040,630,350,20)
    text(c,'Real authenticated Salesforce capture. Fictional demo data. Screens are unaltered.',44,75,1300,14,MUTED)
    c.showPage()

def flow(c,labels,accent,y=645):
    for i,label in enumerate(labels):
        box(c,50+i*278,y,252,100,'#223149')
        text(c,f'0{i+1}',70+i*278,y+67,220,18,accent,'Bold')
        text(c,label,70+i*278,y+36,220,18,WHITE,'Bold')
        if i<len(labels)-1:
            c.setStrokeColor(HexColor(accent));c.setLineWidth(2);c.line(306+i*278,y+50,323+i*278,y+50)

def detail(c,title,body,x,y,w=620,accent=CORAL):
    text(c,title,x,y,w,25,accent,'Bold')
    return text(c,body,x,y-50,w,19)

def video_frame(path,scene,project,accent,step,total):
    global W,H
    W,H=1920,1080;c=canvas.Canvas(str(path),pagesize=(W,H));shot,title,body,dur=scene
    c.setFillColor(HexColor(NAVY));c.rect(0,0,W,H,fill=1,stroke=0)
    box(c,30,1010,6,38,accent,3);text(c,f'{project} / ANA GOMES / SALESFORCE + APEX',60,1020,1700,27,WHITE,'Bold')
    box(c,28,100,1290,886,'#FFFFFF',16);img(c,SRC/shot,28,100,1290,886)
    text(c,title,1350,928,520,36,accent,'Bold')
    text(c,body,1350,748,520,28)
    box(c,1350,188,510,3,'#334762',1);text(c,f'STEP {step} / {total}',1350,142,500,21,MUTED,'Bold')
    text(c,'EDITED WALKTHROUGH / REAL SALESFORCE CAPTURES / FICTIONAL PORTFOLIO DATA / NO AUDIO',30,35,1840,21,MUTED)
    c.showPage();c.save();W,H=1440,900

def make_videos(scenes):
    for video in scenes:
        clips=[];name=video['name']
        for i,scene in enumerate(video['frames']):
            pdf=TMP/f'{name}_{i}.pdf';video_frame(pdf,scene,video['project'],video['accent'],i+1,len(video['frames']))
            prefix=TMP/f'{name}_{i}'
            subprocess.run(['pdftoppm','-scale-to-x','1920','-scale-to-y','1080','-singlefile','-png',str(pdf),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            clip=TMP/f'{name}_{i}.mp4';dur=scene[3]
            subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',str(prefix)+'.png','-t',str(dur),'-vf',f'fade=t=in:st=0:d=0.25,fade=t=out:st={dur-0.25}:d=0.25,format=yuv420p','-r','24','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2',str(clip)],check=True)
            clips.append(clip)
        listing=TMP/f'{name}_concat.txt';listing.write_text('\n'.join("file '"+str(p)+"'" for p in clips))
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(OUT/(name+'.mp4'))],check=True)
        print('VIDEO_DONE',name,flush=True)
    shutil.copy2(BASE/'scenes.json',OUT/'scene-manifest.json')


if __name__=='__main__':make_videos(json.loads((BASE/'scenes.json').read_text()))
