"""Original A/B/A-prime piano sketches with stereo reflections and separate pad beds."""
from pathlib import Path
from array import array
import math, wave, random, json, sys
ROOT=Path(__file__).resolve().parents[1]/'assets'/'audio'
SR=22050
rng=random.Random(713)
def write(file,left,right):
    file.parent.mkdir(parents=True,exist_ok=True)
    peak=max(max(map(abs,left)),max(map(abs,right)),.001);scale=min(1,.82/peak)
    data=array('h')
    for l,r in zip(left,right):data.extend((int(l*scale*32767),int(r*scale*32767)))
    if sys.byteorder!='little':data.byteswap()
    with wave.open(str(file),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(data.tobytes())
def note(left,right,start,midi,duration,amp,pan=0,soft=False):
    f=440*2**((midi-69)/12);offset=int(start*SR);n=len(left);decay=.72 if soft else 1.15
    for j in range(int(duration*SR)):
        t=j/SR;env=(1-math.exp(-t*(30 if soft else 100)))*math.exp(-t*decay);phase=2*math.pi*f*t
        v=(math.sin(phase)+.23*math.sin(phase*2.0008)*math.exp(-t)+.08*math.sin(phase*3.002)*math.exp(-2*t))*env*amp
        ix=(offset+j)%n;left[ix]+=v*(.72-pan*.22);right[ix]+=v*(.72+pan*.22)
        left[(ix+5975)%n]+=v*.12;right[(ix+8753)%n]+=v*.13
themes={
 'shallow':(60,1.05,[[0,4,7,11],[5,9,12,16],[9,12,16,19],[7,11,14,17]]),
 'garden':(62,.95,[[0,3,7,10],[5,9,12,16],[3,7,10,14],[7,10,14,17]]),
 'jelly':(57,1.2,[[0,3,7,10],[5,8,12,15],[3,7,10,14],[7,10,14,17]]),
 'canyon':(55,1.15,[[0,4,7,9],[5,9,12,16],[2,5,9,12],[7,11,14,16]]),
 'whale':(48,1.4,[[0,4,7,11],[9,12,16,19],[5,9,12,16],[7,11,14,17]]),
 'sunset':(53,1.25,[[0,4,7,11],[9,12,16,19],[5,9,12,16],[7,11,14,17]])}
manifest=[]
for name,(root,beat,chords) in themes.items():
    seconds=beat*96;n=round(SR*seconds);left=array('f',[0])*n;right=array('f',[0])*n
    for bar in range(12):
        chord=chords[bar%4];start=bar*8*beat;section=bar//4
        for k in [0,2]:note(left,right,start+.04*k,root+chord[k]-12,6,.085,(-1 if k==0 else 1)*.5,True)
        pattern=[(0,2),(1.5,1),(3,3),(5,2)] if section==0 else [(0,3),(1,2),(2.5,1),(4,0),(5.5,2)] if section==1 else [(0,1),(2,2),(4.5,3)]
        for pos,index in pattern:
            if bar in [3,7,11] and pos>2.5:continue
            note(left,right,start+pos*beat+rng.uniform(-.025,.025),root+chord[index]+(12 if section==1 else 0),5,.11+rng.uniform(-.018,.018),rng.uniform(-.65,.65))
        if section==1 and bar%2==0:note(left,right,start+6*beat,root+chord[3]+12,4,.045,.7,True)
    write(ROOT/'music'/f'{name}.wav',left,right)
    left=array('f',[0])*n;right=array('f',[0])*n
    for bar in range(12):
        chord=chords[bar%4];length=8*beat+3;start=bar*8*beat
        freqs=[440*2**((root+chord[k]-12-69)/12) for k in [0,1,2]]
        for j in range(int(length*SR)):
            t=j/SR;env=min(1,t/2)*min(1,(length-t)/2)*.024
            v=sum(math.sin(2*math.pi*f*t) for f in freqs)*env
            idx=(round(start*SR)+j)%n;left[idx]+=v*(.9+.1*math.sin(t*.32));right[idx]+=v*(.9-.1*math.sin(t*.32))
    write(ROOT/'beds'/f'{name}.wav',left,right)
    manifest.append({'region':name,'seconds':round(seconds,2),'form':'A / B / A-prime, phrase rests','layers':['music','beds'],'format':'22050 Hz 16bit stereo','source':'original procedural arrangement'})
    print(name,round(seconds,2),'seconds',flush=True)
(ROOT/'arrangement.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
