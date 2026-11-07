"""Original deterministic modal piano sketches and synthesized ocean effects, no samples."""
import math, random, wave, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'assets'/'audio'
SR=22050
random.seed(20261107)
def write(path, samples):
    path.parent.mkdir(parents=True,exist_ok=True)
    peak=max(abs(v) for v in samples) or 1
    scale=.68/max(.68,peak)
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,v*scale))*32767)) for v in samples))
def note(out,start,midi,duration=4,amp=.17):
    f=440*2**((midi-69)/12)
    for j in range(int(duration*SR)):
        t=j/SR; idx=int(start*SR)+j
        # Wrapped tails make the loop continuous.
        envelope=(1-math.exp(-t*95))*math.exp(-t*1.4)
        v=sum(math.sin(2*math.pi*f*k*(1+.00015*k*k)*t)*math.exp(-t*k*.19)/(k*k) for k in range(1,5))
        out[idx%len(out)]+=v*envelope*amp
themes={'shallow':([60,64,67,71,74,67,64,62],1.5),'garden':([62,69,74,77,76,69,65,72],1.25),'jelly':([57,64,69,71,76,71,64,59],1.75),'canyon':([50,57,62,65,69,65,62,57],1.75),'whale':([45,52,57,64,62,57,52,47],2.25),'sunset':([53,60,65,69,72,69,67,60],1.75)}
for name,(notes,beat) in themes.items():
    duration=beat*32;out=[0.0]*int(duration*SR)
    for i in range(32):
        if i%8 not in (6,7):note(out,i*beat,notes[i%8]+(12 if i%16>=8 else 0),5,.16 if i%4 else .2)
        if i%8==0:
            for m in [notes[0]-12,notes[0]-5]:note(out,i*beat,m,7,.1)
    write(ROOT/'music'/f'{name}.wav',out)
def tone(kind,d):
    out=[]
    for i in range(int(d*SR)):
        t=i/SR;env=math.sin(math.pi*t/d)**2
        if kind=='whale': v=math.sin(2*math.pi*(95*t+18*math.sin(t*.8)))+.25*math.sin(2*math.pi*210*t)
        elif kind=='bubble':v=math.sin(2*math.pi*(500*t+650*t*t))*math.exp(-t*9)
        elif kind=='ray':v=math.sin(2*math.pi*(420*t+95*t*t))*.5+math.sin(2*math.pi*630*t)*.2
        elif kind=='sonar':v=math.sin(2*math.pi*510*t)*math.exp(-t*2)
        else:v=(math.sin(2*math.pi*660*t)+.4*math.sin(2*math.pi*990*t))*math.exp(-t*3)
        out.append(v*env*.35)
    return out
for name,d in [('whale',4),('bubble',.6),('ray',1.3),('sonar',1.8),('bell',1.6)]:write(ROOT/'effects'/f'{name}.wav',tone(name,d))
print('Generated six original piano sketches and five synthesized effects.')
