from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math,numpy as np,wave,subprocess,json,concurrent.futures
B=Path(__file__).resolve().parent;O=B.parent/'videos';T=B/'render-temp';SRC=B.parent/'screenshots';T.mkdir(exist_ok=True)
W,H=1920,1080;FPS=24
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fonts={}
def font(s,b=False):
 k=(s,b)
 if k not in fonts:fonts[k]=ImageFont.truetype(BOLD if b else FONT,s)
 return fonts[k]
def ease(t):t=max(0,min(1,t));return 1-(1-t)**3
def text(d,s,x,y,size=34,col='#FFFFFF',b=False):d.text((int(x),int(y)),s,font=font(size,b),fill=col)
def wrap(d,s,x,y,width,size=32,col='#FFFFFF',b=False):
 line=''
 for w in s.split():
  q=(line+' '+w).strip()
  if d.textlength(q,font=font(size,b))>width and line:text(d,line,x,y,size,col,b);y+=size*1.35;line=w
  else:line=q
 text(d,line,x,y,size,col,b)
def rr(d,b,fill,r=24,outline=None,width=2):d.rounded_rectangle(tuple(map(int,b)),r,fill=fill,outline=outline,width=width)
shots={n:Image.open(str(SRC/n)).convert('RGB') for n in ['EncoreOps_Real_Overview.jpg','Encore_01_Selection.jpg','Encore_03_Held.jpg','Encore_06_Resolved.jpg','ReUseCloud_Real_Overview.jpg'] if (SRC/n).exists()}
def fit(im,source,box,zoom=1):
 x,y,w,h=box;s=min(w/source.width,h/source.height)*zoom;a=source.resize((int(source.width*s),int(source.height*s)),Image.Resampling.BICUBIC)
 pane=Image.new('RGB',(w,h),'#F8FAFC');pane.paste(a,((w-a.width)//2,(h-a.height)//2));im.paste(pane,(int(x),int(y)))
def crop(name,rect):return shots[name].crop(rect)
def laptop(d,x,y,s,ac):
 rr(d,(x,y,x+s,y+s*.6),'#F7FAF4',18);rr(d,(x+12,y+12,x+s-12,y+s*.6-12),'#183F36',12)
 d.line((x-25,y+s*.64,x+s+25,y+s*.64),fill=ac,width=13);d.line((x+s*.3,y+s*.22,x+s*.72,y+s*.22),fill=ac,width=8);d.line((x+s*.3,y+s*.32,x+s*.57,y+s*.32),fill='#FFFFFF',width=6)
def ticket(d,x,y,s,ac):
 rr(d,(x,y,x+s,y+s*.48),'#FBEEE8',18);d.line((x+s*.73,y+10,x+s*.73,y+s*.48-10),fill=ac,width=5)
 text(d,'ADMIT ONE',x+25,y+20,int(s*.08),'#22263D',True)
 for i in range(13):d.line((x+25+i*9,y+s*.28,x+25+i*9,y+s*.4),fill='#22263D',width=3+(i%3))
def soundtrack(key,duration):
 sr=44100;t=np.arange(int(duration*sr))/sr;sig=np.zeros(len(t));bpm=104 if key=='EncoreOps' else 92;beat=60/bpm
 for k in range(int(duration/beat)+1):
  st=k*beat;u=t-st;mask=(u>=0)&(u<.25);v=u[mask];sig[mask]+=.11*np.sin(2*np.pi*(60*v+45*.018*(1-np.exp(-v/.018))))*np.exp(-v*23)
  st+=beat*.5;u=t-st;mask=(u>=0)&(u<.07);v=u[mask];sig[mask]+=.013*np.sin(2*np.pi*6000*v)*np.exp(-v*65)
 notes=[220,261.63,329.63,392] if key=='EncoreOps' else [196,246.94,293.66,369.99]
 for k in range(int(duration/(beat*.5))+1):
  u=t-k*beat*.5;mask=(u>=0)&(u<.55);v=u[mask];freq=notes[k%4];sig[mask]+=.04*np.sin(2*np.pi*freq*v)*np.exp(-v*8)
 sig*=np.minimum(t/1.5,1)*np.minimum((duration-t)/2,1);sig=np.clip(sig,-.8,.8)
 p=T/(key+'_music.wav')
 with wave.open(str(p),'w') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes((sig*32767).astype('<i2').tobytes())
 return p
specs=[('EncoreOps_01_Overview','EncoreOps',False),('EncoreOps_02_Workflow','EncoreOps',True),('ReUseCloud_01_Overview','ReUseCloud',False),('ReUseCloud_02_DecisionFlow','ReUseCloud',True)]
def render(spec):
 name,key,flow=spec;reuse=key=='ReUseCloud';project='ReUse Cloud' if reuse else 'EncoreOps';dark='#123A32' if reuse else '#20253C';ac='#C9E58B' if reuse else '#FFA18A';durations=[4,6,7,7,5];duration=sum(durations);audio=soundtrack(key,duration);out=O/(name+'.mp4')
 cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','pipe:0','-i',str(audio),'-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 if reuse:
  titles=['A second life.','See the decision.','Why this route?','Review before approval.','Native. Explainable.'] if not flow else ['Recovery, explained.','Read the asset.','Eligibility comes first.','A review flag has a reason.','Built in Apex.']
 else:
  titles=['When the event changes.','Control the recovery.','Hold. Resolve. Release.','The outcome is visible.','Native. Testable.'] if not flow else ['Three requests. One session.','Select the requests.','Create temporary holds.','Resolve each request.','Inventory stays consistent.']
 for fi in range(duration*FPS):
  t=fi/FPS;stage=0;local=t
  while local>=durations[stage] and stage<4:local-=durations[stage];stage+=1
  ent=ease(local/.7);im=Image.new('RGB',(W,H),dark);d=ImageDraw.Draw(im)
  # Brand-specific moving background: stage rails or circular recovery rings.
  if reuse:
   for j in range(3):
    r=270+j*100+math.sin(t*.35+j)*15;cx=1620;cy=230;d.arc((cx-r,cy-r,cx+r,cy+r),20+t*7,280+t*7,fill='#285347',width=3)
  else:
   for j in range(9):
    xx=int(1100+j*130+math.sin(t*.3+j)*12);d.line((xx,0,xx-350,1080),fill='#30374E',width=2)
  text(d,'ANA GOMES  /  SALESFORCE APPLICATION',70,40,22,'#CBD5D8',True);text(d,project,70,82,40,ac,True)
  text(d,'APEX  +  LWC',1560,66,25,ac,True)
  text(d,titles[stage],70,166+int((1-ent)*40),64,'#FFFFFF',True)
  if stage==0:
   wrap(d,'Equipment recovery with business rules you can inspect.' if reuse else 'Inventory-safe recovery for live-event bookings.',75,335,960,45,'#FFFFFF')
   text(d,'DECISION ENGINE' if reuse else 'LIVE EVENT OPERATIONS',75,555,25,ac,True)
   if reuse:
    for i in range(3):laptop(d,1120+i*150,350+i*100-int(ent*30),300,ac)
    text(d,'RESALE  /  REPAIR  /  RECYCLE',1070,800,25,ac,True)
   else:
    for i in range(3):ticket(d,1120+i*120,350+i*110-int(ent*30),370,ac)
    text(d,'CONFIRM  /  CREDIT  /  REFUND',1090,810,25,ac,True)
   text(d,'Motion graphic introduction / authentic application screens follow',75,940,22,'#BBC8CD')
  elif stage==1:
   source=shots['ReUseCloud_Real_Overview.jpg' if reuse else ('Encore_01_Selection.jpg' if flow else 'EncoreOps_Real_Overview.jpg')]
   if flow:source=source.crop((40,730,1295,915)) if reuse else source.crop((35,210,1300,570))
   x=int(65+(1-ent)*100);rr(d,(x-6,292,x+1236,907),'#FFFFFF');fit(im,source,(x,298,1230,603),1+.018*local/durations[stage]);d=ImageDraw.Draw(im)
   text(d,'01  /  '+('ASSET INPUTS' if reuse else 'REQUESTS'),1370,345,26,ac,True)
   wrap(d,'Three assets. Three recommendations.' if reuse else ('Three New requests selected for Grove Stage.' if flow else '300 demo requests. Capacity across three alternative sessions.'),1370,420,465,36)
   wrap(d,'Real Salesforce capture. Fictional portfolio data.',1370,730,460,24,'#BCCACF')
  elif stage==2:
   if reuse:
    labs=['RESALE','REPAIR','RECYCLE'];vals=['Condition >= 70','Condition >= 30','Always eligible']
    text(d,'Policy graphic / native Apex rules',75,275,23,'#BFCAC9')
    for i in range(3):
     delay=i*.35;en=ease((local-delay)/.65);x=70+i*590;y=350+int((1-en)*85);rr(d,(x,y,x+555,y+395),'#F3F6ED');laptop(d,x+185,y+35,185,'#467012');text(d,labs[i],x+35,y+215,36,dark,True);text(d,vals[i],x+35,y+286,29,dark)
    text(d,'Compare expected contribution after costs and repair risk.',75,830,36,ac,True)
   else:
    source=shots['Encore_03_Held.jpg'].crop((35,440,1300,925))
    rr(d,(65,295,1305,805),'#FFFFFF');fit(im,source,(72,302,1226,496),1+.025*local/7);d=ImageDraw.Draw(im)
    text(d,'03 REQUESTS',1370,335,31,ac,True);text(d,'HELD',1370,395,72,'#FFFFFF',True)
    # Annotated numerical explanation kept outside the unchanged platform crop.
    text(d,'GROVE CAPACITY',1370,555,26,ac,True);text(d,'120 -> 117',1370,610,49,'#FFFFFF',True)
    text(d,'10-minute expiry',1370,750,29,'#FFFFFF')
    text(d,'Asynchronous Apex processing / seats allocated while the hold is active',75,885,30,ac)
  elif stage==3:
   source=shots['ReUseCloud_Real_Overview.jpg'].crop((40,730,1295,915)) if reuse else shots['Encore_06_Resolved.jpg'].crop((35,210,1300,555))
   rr(d,(65,300,1855,805),'#FFFFFF');fit(im,source,(72,307,1776,491),1+.015*local/7);d=ImageDraw.Draw(im)
   if reuse:
    wrap(d,'Orion 15: -520 expected contribution -> manager review required.',75,843,1690,37,ac,True)
    text(d,'Existing states inspected / this is not a recording of a new approval sequence',75,932,23,'#BBC8CD')
   else:
    text(d,'CONFIRMED',75,850,30,ac,True);text(d,'CREDIT 132',690,850,30,ac,True);text(d,'REFUND 120',1325,850,30,ac,True)
    text(d,'Compensation decisions release seats. No payment was executed.',75,930,25,'#BBC8CD')
  else:
   text(d,'15' if reuse else '10',75,335,170,ac,True);text(d,'APEX TESTS PASSED',340,416,38,'#FFFFFF',True)
   for i,lab in enumerate(['Native Salesforce app','Business rules + permissions','Source + tests + real captures']):
    yy=625+i*84;rr(d,(75,yy,120,yy+44),ac,12);text(d,'+',86,yy-1,34,dark,True);text(d,lab,150,yy,34,'#FFFFFF')
   wrap(d,'A second life. A defensible decision.' if reuse else 'When the headline changes, the recovery needs a plan.',1160,350,660,52,ac,True)
   text(d,'Salesforce / Apex / Lightning',1160,660,29,'#FFFFFF')
   text(d,'Edited authentic captures + explanatory motion graphics',75,957,23,'#BBC8CD')
  # Deliberate progress strip and scene index; animation stays outside real screenshot pixels.
  d.rectangle((0,1069,int(W*t/duration),1079),fill=ac);text(d,f'{stage+1:02d} / 05',1740,993,22,'#BBC8CD')
  # Fade the first and last few frames of the film, not every slide.
  fade=min(1,t/.35,(duration-t)/.5)
  if fade<1:im=Image.blend(Image.new('RGB',(W,H),dark),im,max(0,fade))
  if fi in [FPS*2,FPS*7,FPS*13,FPS*20,FPS*26]:im.save(T/(name+f'_{fi//FPS:02d}.jpg'),quality=92)
  p.stdin.write(im.tobytes())
 p.stdin.close();assert p.wait()==0;print(name+' rendered',flush=True)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,specs))
 print('Four motion edits complete',flush=True)
