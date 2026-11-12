(()=>{'use strict';
const C=window.AbyssContent,g=window.seaGame,$=s=>document.querySelector(s);
let saved={};try{saved=JSON.parse(localStorage.getItem('abyss.presentation.v05')||'{}')}catch{}
const settings={language:C.languages[saved.language]?saved.language:'zh-CN',voice:['male','female','matureMale','matureFemale'].includes(saved.voice)?saved.voice:'female',voiceEnabled:!!saved.voiceEnabled,replay:!!saved.replay,reduce:!!saved.reduce||matchMedia('(prefers-reduced-motion: reduce)').matches,subtitles:true};
const text=k=>C.ui[settings.language][k]||C.ui.en[k]||k;
function save(){try{localStorage.setItem('abyss.presentation.v05',JSON.stringify(settings))}catch{}apply();dispatchEvent(new CustomEvent('abyss-presentation-change'))}
function options(){return Object.entries(C.languages).map(([v,n])=>`<option value="${v}">${n}</option>`).join('')}
const entry=document.createElement('div');entry.className='entry-preferences';entry.innerHTML=`<label><span data-cine-text="language"></span><select id="entry-language">${options()}</select></label><button id="entry-settings" data-cine-text="settings"></button><button id="entry-music" data-cine-text="sound"></button>`;$('#welcome .intro').append(entry);
const d=document.createElement('dialog');d.id='presentation-settings';d.innerHTML=`<p class="eyebrow">DIALOGUE ABYSS · PRESENTATION</p><h2 data-cine-text="settings"></h2><label><span data-cine-text="language"></span><select id="presentation-language">${options()}</select></label><label><span data-cine-text="voice"></span><select id="presentation-voice">${['male','female','matureMale','matureFemale'].map(k=>`<option value="${k}" data-cine-text="${k}"></option>`).join('')}</select></label><p class="fine" data-cine-text="ageNote"></p><label><span data-cine-text="voiceEnable"></span><input id="presentation-voice-enable" type="checkbox"></label><button id="voice-preview" data-cine-text="preview"></button><p class="fine" data-cine-text="voiceNote"></p><p id="voice-status" role="status"></p><label><span data-cine-text="replay"></span><input id="presentation-replay" type="checkbox"></label><label><span data-cine-text="reduce"></span><input id="presentation-reduce" type="checkbox"></label><button id="presentation-close" class="primary" data-cine-text="back"></button>`;document.body.append(d);
const menu=document.createElement('button');menu.id='presentation-open';menu.dataset.cineText='settings';$('#pause .grid').append(menu);
let returnTo=null;function show(){returnTo=document.querySelector('dialog[open]')?.id||null;g.close();g.open('#presentation-settings')}
$('#entry-settings').onclick=show;menu.onclick=show;
function dismiss(){stopVoice();d.close();g.close();if(returnTo)g.open('#'+returnTo)}
$('#presentation-close').onclick=dismiss;d.addEventListener('cancel',e=>{e.preventDefault();dismiss()});
for(const id of ['entry-language','presentation-language'])$('#'+id).onchange=e=>{settings.language=e.target.value;stopVoice();save()};
$('#presentation-voice').onchange=e=>{settings.voice=e.target.value;stopVoice();save()};
for(const [id,key] of [['presentation-voice-enable','voiceEnabled'],['presentation-replay','replay'],['presentation-reduce','reduce']])$('#'+id).onchange=e=>{settings[key]=e.target.checked;stopVoice();save()};
let musicOn=false,lastHover=0;
async function unlockMusic(){await g.audio.start();g.audio.pause(false);g.audio.region(g.regions[g.region].music);musicOn=true;apply()}
$('#entry-music').onclick=()=>{if(musicOn){g.audio.pause(true);musicOn=false;apply()}else unlockMusic()};
document.addEventListener('pointerdown',e=>{if(!g.playing&&e.target.closest('button,select')&&e.target.id!=='entry-music'&&!musicOn)unlockMusic()},{passive:true});
function stopVoice(){window.speechSynthesis?.cancel()}
function speak(line,role='diver',force=false){stopVoice();if((!force&&!settings.voiceEnabled)||!window.speechSynthesis)return false;
 const lang=settings.language,voices=speechSynthesis.getVoices();const exact=voices.filter(v=>v.lang.replace('_','-').toLowerCase()===lang.toLowerCase());const pool=exact.length?exact:voices.filter(v=>v.lang.toLowerCase().split(/[-_]/)[0]===lang.split('-')[0]);
 if(!pool.length){$('#voice-status').textContent=text('unavailable');return false}
 const feminine=role==='diver'?/female/i.test(settings.voice):['jelly','octopus'].includes(role);
 const voice=pool.find(v=>(feminine?/female|zira|xiaoxiao|huihui|haruka|sunhi|hanhan/i:/male|david|yunxi|ichiro|injoon/i).test(v.name))||pool[0];
 const utterance=new SpeechSynthesisUtterance(line);utterance.lang=lang;utterance.voice=voice;
 const age=g.profile.active?.age;utterance.rate=role==='whale'?.78:role==='seahorse'?1.02:role==='shark'?.95:role==='diver'&&(age==='31+'||settings.voice.startsWith('mature'))?.87:.93;
 utterance.pitch=role==='whale'?.7:role==='seahorse'?1.15:role==='octopus'?.94:role==='shark'?.85:1;
 utterance.volume=.8;utterance.onerror=()=>{$('#voice-status').textContent=text('unavailable')};speechSynthesis.speak(utterance);$('#voice-status').textContent=voice.name;return true;
}
$('#voice-preview').onclick=()=>speak(text('test'),'diver',true);
function apply(){document.documentElement.lang=settings.language;document.body.classList.toggle('reduce-presentation',settings.reduce);for(const el of document.querySelectorAll('[data-cine-text]'))el.textContent=text(el.dataset.cineText);for(const id of ['entry-language','presentation-language'])$('#'+id).value=settings.language;$('#presentation-voice').value=settings.voice;$('#presentation-voice-enable').checked=settings.voiceEnabled;$('#presentation-replay').checked=settings.replay;$('#presentation-reduce').checked=settings.reduce;$('#entry-music').textContent=text(musicOn?'mute':'sound');$('#welcome h1').textContent=text('title');$('#welcome .eyebrow').textContent=text('tagline');$('#start').textContent=text('start')+' ↗';}
// Decorative water response stays out of the focus and accessibility trees.
const veil=document.createElement('div');veil.className='welcome-light';veil.setAttribute('aria-hidden','true');$('#welcome').prepend(veil);
for(let i=0;i<14;i++){const p=document.createElement('i');p.className='welcome-mote';p.style.cssText=`--x:${(i*37)%100}%;--delay:${-i*1.3}s;--duration:${13+i%7}s;`;veil.append(p)}
document.addEventListener('pointermove',e=>{if(settings.reduce||g.playing)return;$('#welcome').style.setProperty('--pointer-x',(e.clientX/innerWidth-.5)*14+'px');$('#welcome').style.setProperty('--pointer-y',(e.clientY/innerHeight-.5)*10+'px')},{passive:true});
document.addEventListener('pointerover',e=>{const b=e.target.closest('button,a');if(!b||b.contains(e.relatedTarget)||performance.now()-lastHover<180)return;lastHover=performance.now();if(!g.paused)g.audio.effect('bubble')},{passive:true});
document.addEventListener('pointerdown',e=>{if(!e.target.closest('button,a')||settings.reduce)return;const r=document.createElement('span');r.className='touch-ripple';r.style.left=e.clientX+'px';r.style.top=e.clientY+'px';r.setAttribute('aria-hidden','true');document.body.append(r);r.addEventListener('animationend',()=>r.remove(),{once:true});if(!g.paused)g.audio.effect('bell')},{passive:true});
document.addEventListener('visibilitychange',()=>{if(document.hidden){stopVoice();g.audio.pause(true)}else if(!g.paused&&(g.playing||musicOn))g.audio.pause(false)});
window.addEventListener('pagehide',stopVoice);
window.AbyssPresentation={settings,text,speak,stopVoice,apply,save};apply();
})();
