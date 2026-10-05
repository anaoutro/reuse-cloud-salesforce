from pathlib import Path
import sys,math,subprocess,concurrent.futures
from PIL import Image,ImageDraw,ImageFont
import threading
sys.path.insert(0,str(Path(__file__).resolve().parent))
from motion_edit import font,text,wrap,rr,ease,fit,crop,shots,laptop,ticket,soundtrack,FPS
B=Path(__file__).resolve().parent;O=B.parent/'videos';T=B/'render-temp';T.mkdir(exist_ok=True)
ART={'ReUseCloud':Image.open(B.parent/'illustrations/story-art.png').convert('RGB')}
DURS=[5,8,7,8,8,6];DURATION=sum(DURS);W,H=1920,1080
SPECS=[('EncoreOps_01_Overview','EncoreOps',False),('EncoreOps_02_Workflow','EncoreOps',True),('ReUseCloud_01_Overview','ReUseCloud',False),('ReUseCloud_02_DecisionFlow','ReUseCloud',True)]
BRAND=B.parent/'brand-assets'
CTX=threading.local()
FONT_CACHE={}
def font(size,b=False):
 key=getattr(CTX,'key','EncoreOps')
 ck=(key,size,b)
 if ck in FONT_CACHE:return FONT_CACHE[ck]
 name=('Anton.ttf' if key=='EncoreOps' else 'Fraunces.ttf') if b else 'Manrope.ttf'
 path=BRAND/'fonts'/name
 if not path.exists():path=Path('/usr/share/fonts/opentype/urw-base35/URWBookman-Demi.otf' if b else '/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
 f=ImageFont.truetype(str(path),size);FONT_CACHE[ck]=f;return f
def text(d,s,x,y,size=34,col='#FFFFFF',b=False):d.text((int(x),int(y)),s,font=font(size,b),fill=col)
def wrap(d,s,x,y,width,size=32,col='#FFFFFF',b=False):
 for para in s.split('\n'):
  line=''
  for w in para.split():
   q=(line+' '+w).strip()
   if d.textlength(q,font=font(size,b))>width and line:text(d,line,x,y,size,col,b);y+=size*1.35;line=w
   else:line=q
  text(d,line,x,y,size,col,b);y+=size*1.35
ASSETS={}
def asset(im,key,n,x,y,w,t,rotate=True):
 a=ASSETS[key][n];scale=w/a.width*(1+.035*math.sin(t*2+n));a=a.resize((int(a.width*scale),int(a.height*scale)),Image.Resampling.BICUBIC)
 if rotate:a=a.rotate(5*math.sin(t*1.4+n),Image.Resampling.BICUBIC,expand=True)
 im.paste(a,(int(x-a.width/2),int(y-a.height/2+12*math.sin(t*2+n))),a)
def paper(d,x,y,w,h,col,angle=0):d.rectangle((x,y,x+w,y+h),fill=col)
def hero(t,key):
 im=Image.new('RGB',(W,H),'#FFF5DD')
 asset(im,key,1,1190,650,690,t)
 asset(im,key,2,1680,745,480,t+1)
 asset(im,key,0,1530,175,305,t,False)
 return im

def render(spec):
 name,key,flow=spec;CTX.key=key;reuse=key=='ReUseCloud';dark='#163F36' if reuse else '#22263D';ac='#C9E58B' if reuse else '#FF9F83';title='ReUse Cloud' if reuse else 'EncoreOps';audio=Path(soundtrack_paths[key])
 p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','pipe:0','-i',str(audio),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(O/(name+'.mp4'))],stdin=subprocess.PIPE)
 for fi in range(DURATION*FPS):
  t=fi/FPS;local=t;stage=0
  while stage<5 and local>=DURS[stage]:local-=DURS[stage];stage+=1
  en=ease(local/.6);im=hero(t,key) if stage in [0,5] else Image.new('RGB',(W,H),'#F4EFDF');d=ImageDraw.Draw(im)
  if stage in [0,5]:
   # Hero artwork carries the original project wordmark; animation captions occupy the blank paper margin.
   if stage==0:
    head=('A laptop\ncomes back.' if reuse else 'The show\nhas changed.') if not flow else ('Sell, repair\nor recycle?' if reuse else 'Help three\npeople move.')
    x=64-int((1-en)*55);y=445 if reuse else 230
    for i,line in enumerate(head.split('\n')):text(d,line,x,y+i*90,72,dark,True)
    wrap(d,'What happens next?' if reuse else 'The audience needs a plan.',64,y+205,470,33,ac,True)
    paper(d,65,910,530,88,'#FFF5DD');text(d,'A REAL SALESFORCE APP',88,934,28,dark,True)
   else:
    y=460 if reuse else 255
    wrap(d,'A second life.\nA defensible decision.' if reuse else 'Recover the event.\nKeep the record.',65,y,520,58,dark,True)
    paper(d,65,855,540,130,'#FFF4DA');text(d,'15 APEX TESTS PASSED' if reuse else '10 APEX TESTS PASSED',86,881,29,dark,True);text(d,'Built by Ana Gomes',86,934,25,dark)
   text(d,'Explanatory artwork / fictional portfolio lab',65,1030,20,dark)
  else:
   d.rectangle((0,0,W,145),fill=dark);text(d,title,65,34,52,ac,True);text(d,'ANA GOMES  /  APEX + LIGHTNING',1190,66,24,'#FFFFFF',True)
   # Editorial fragments and animated tape; decoration never changes screenshot data.
   for j in range(8):
    x=1520+j*45;y=180+int(math.sin(t*.7+j)*14);d.line((x,y,x+22,y+34),fill=ac,width=5)
   if stage==1:
    text(d,'Give the event a second chance.' if not reuse else 'Give equipment a second life.',65,190,62,dark,True)
    progress=ease(local/1.1)
    asset(im,key,1,550-int((1-progress)*450),570,590 if reuse else 690,t)
    asset(im,key,2,1450+int((1-progress)*450),570,550 if reuse else 640,t+1)
    d=ImageDraw.Draw(im)
    wrap(d,'A changed show. Limited seats. Every customer needs a clear next step.' if not reuse else 'Returned equipment deserves a decision based on condition, cost and risk.',70,845,1680,43,dark,True)
    text(d,'Animated brand artwork / fictional portfolio lab',70,1005,23,dark)
   elif stage==2:
    heading='Inspect the equipment.' if reuse else ('Select three requests.' if flow else 'Meet the recovery workbench.')
    text(d,heading,65,185,57,dark,True)
    source=shots['ReUseCloud_Real_Overview.jpg' if reuse else ('Encore_01_Selection.jpg' if flow else 'EncoreOps_Real_Overview.jpg')]
    if flow:source=source.crop((40,730,1295,915)) if reuse else source.crop((35,210,1300,570))
    paper(d,55,305,1290,600,'#FFFFFF');fit(im,source,(72,318,1256,572),1+.018*local/7);d=ImageDraw.Draw(im)
    wrap(d,'Three assets. A visible recommendation and state for each.' if reuse else ('DEMO-002 / 005 / 008. Same session. One seat each.' if flow else '300 demo requests. Alternative sessions. Controlled reservations.'),1390,385,430,40,dark,True)
    text(d,'AUTHENTIC CAPTURE',1390,760,25,dark,True);wrap(d,'Original Salesforce pixels; explanatory crop and motion.',1390,813,440,25,dark)
   elif stage==3:
    if reuse:
     text(d,'Sell, repair or recycle?',65,185,64,dark,True)
     asset(im,key,1,450,590,650,t)
    
     d=ImageDraw.Draw(im)
     wrap(d,'CONDITION 65',900,365,500,36,dark,True)
     wrap(d,'Resale is ineligible. Recycling is the better eligible route.',900,445,760,43,dark,True)
     wrap(d,'Orion 15: -520 contribution. Manager review required.',900,720,760,35,dark)
     text(d,'Explanatory animation / verified values from the captured record',65,990,25,dark)
    else:
     text(d,'A hold buys time to decide.',65,185,57,dark,True)
     source=shots['Encore_03_Held.jpg'].crop((35,440,1300,925));paper(d,55,305,1310,585,'#FFFFFF');fit(im,source,(70,320,1280,555),1+.02*local/8);d=ImageDraw.Draw(im)
     text(d,'GROVE SEATS',1420,370,29,dark,True);count=120-round(3*ease((local-.4)/1.6));text(d,str(count),1420,430,132,dark,True);text(d,'120 -> 117',1420,620,43,dark,True);text(d,'10-MINUTE HOLD',1420,730,29,dark,True)
     text(d,'Explainer counter / the held-state capture is real',65,945,27,dark)
   else:
    text(d,'The recommendation is visible.' if reuse else 'One confirmed. Two compensation decisions.',65,185,52,dark,True)
    source=shots['ReUseCloud_Real_Overview.jpg'].crop((40,730,1295,915)) if reuse else shots['Encore_06_Resolved.jpg'].crop((35,210,1300,555))
    paper(d,55,310,1805,490,'#FFFFFF');fit(im,source,(72,327,1771,456),1+.018*local/8);d=ImageDraw.Draw(im)
    if reuse:
     paper(d,70,835,1175,130,'#D2E49E');wrap(d,'Orion 15: Recycle / -520 / manager review required.',95,866,1100,35,dark,True);wrap(d,'Existing state inspected. No new approval click sequence is claimed.',1290,862,525,25,dark)
    else:
     for i,label in enumerate(['CONFIRMED','CREDIT 132','REFUND 120']):
      x=70+i*600;paper(d,x,835,560,90,'#FFC5B1');text(d,label,x+25,858,35,dark,True)
     text(d,'Real resolved-state capture / compensation ledger decisions, not payments',75,965,26,dark)
  # Fast paper wipe on chapter change; the UI stays unobscured after the entry transition.
  if stage not in [0,5] and local<.28:
   width=int(W*(1-local/.28));d.rectangle((W-width,0,W,H),fill=ac)
  d.rectangle((0,1068,int(W*t/DURATION),1079),fill=ac)
  if fi in [FPS*2,FPS*9,FPS*16,FPS*25,FPS*33,FPS*39]:im.save(T/(name+f'_{fi//FPS:02d}.jpg'),quality=93)
  p.stdin.write(im.tobytes())
 p.stdin.close();assert p.wait()==0;print(name+' narrative edit complete',flush=True)
soundtrack_paths={}
if __name__=='__main__':
 for key in ['ReUseCloud']:soundtrack_paths[key]=str(soundtrack(key,DURATION))
 for key in ['ReUseCloud']:
  ASSETS[key]=[Image.open(BRAND/(key+'_'+str(n)+'.png')).convert('RGBA') for n in range(3)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,[x for x in SPECS if x[1]=='ReUseCloud']))
