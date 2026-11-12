/* Ocean motion system: presentation-only; does not delay game input or dialog lifecycle. */
(()=>{'use strict';const $=s=>document.querySelector(s),ns='http://www.w3.org/2000/svg';
const shapes={
 compass:'<circle cx="12" cy="12" r="9"/><path class="needle" d="m16 8-3 5-5 3 3-5Z"/>',
 camera:'<path d="M3 7h5l2-3h4l2 3h5v13H3Z"/><circle class="lens" cx="12" cy="13" r="4"/><path d="M17 10h1"/>',
 sonar:'<circle cx="12" cy="12" r="2"/><circle class="sonar-wave" cx="12" cy="12" r="6"/><circle class="sonar-wave outer" cx="12" cy="12" r="10"/>',
 journal:'<path class="page-left" d="M12 6C8 3 4 4 2 5v14c4-2 7-1 10 1"/><path class="page-right" d="M12 6c4-3 8-2 10-1v14c-4-2-7-1-10 1Z"/><path d="M12 6v14"/>',
 gear:'<path class="gear-body" d="M8 3 3 7l3 4 2-2v12h8V9l2 2 3-4-5-4c-1 4-7 4-8 0Z"/><path d="M10 13h4m-4 3h4"/>',
 bubble:'<circle class="bubble-one" cx="9" cy="15" r="5"/><circle class="bubble-two" cx="17" cy="7" r="3"/>',
 music:'<path class="music-note" d="M9 17V5l11-2v12M9 7l11-2"/><ellipse cx="6" cy="18" rx="3" ry="2"/><ellipse cx="17" cy="16" rx="3" ry="2"/>',
 menu:'<path class="menu-top" d="M4 6h16"/><path d="M4 12h12"/><path class="menu-bottom" d="M4 18h16"/>',
 wave:'<path class="greeting" d="M7 14V7c0-2 3-2 3 0v4-6c0-2 3-2 3 0v6-5c0-2 3-2 3 0v6-3c0-2 3-2 3 0v7c0 6-9 8-12 3l-4-5c-1-2 1-3 3-1Z"/>',
 follow:'<path class="fish-one" d="M2 8c4-6 8-6 12 0-4 6-8 6-12 0Zm12 0 5-4v8Z"/><path d="M4 18c4-4 8-4 12 0m-2-2 3 2-3 2"/>',
 rest:'<path d="M3 15c3-4 6 4 9 0s6 4 9 0M3 20c3-4 6 4 9 0s6 4 9 0"/><path class="rest-sun" d="M7 10a5 5 0 0 1 10 0"/>',
 spin:'<path class="spin-arc" d="M19 7a8 8 0 1 0 1 9M19 2v6h-6"/>',
 heart:'<path class="heart-line" d="M2 12h5l2-6 4 12 3-6h6"/>',
 chat:'<path class="chat-body" d="M21 11a9 8 0 0 1-9 8H7l-5 3 1-6a8 8 0 1 1 18-5Z"/><path class="chat-dots" d="M7 11h.1m4.9 0h.1m4.9 0h.1"/>',
 back:'<path class="back-arrow" d="m10 5-7 7 7 7M3 12h18"/>',
 play:'<path class="play-arrow" d="m8 4 12 8-12 8Z"/>',
 save:'<path d="M4 3h13l4 4v14H3V3Z"/><path class="save-mark" d="M7 3v6h10V3M7 21v-8h10v8"/>',
 profile:'<circle class="profile-head" cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>',
 shell:'<path class="shell-body" d="M12 21C7 15 2 15 2 9a10 8 0 0 1 20 0c0 6-5 6-10 12Zm0 0V3M5 5l7 16 7-16"/>',
 flower:'<path d="M12 21v-9m0 7c-5 0-7-2-7-4 5 0 7 2 7 4Z"/><path class="petals" d="M12 12C0 15 4 3 9 7c-2-9 8-9 6 0 5-4 9 8-3 5Z"/>',
 moon:'<path class="moon-body" d="M20 16A9 9 0 0 1 8 3a9 9 0 1 0 12 13Z"/>'
};
const ids={menu:'menu',start:'play',resume:'play','wardrobe-open':'gear','journal-open':'journal',homewater:'compass','profile-manage':'profile','moment-open':'heart','photo-open':'camera','photo-save':'camera','photo-exit':'back','photo-collapse':'menu','ocean-play-open':'follow','presentation-open':'bubble','entry-settings':'bubble','entry-music':'music','voice-preview':'music','presentation-close':'back','save-look':'gear',send:'chat','save-line':'journal',export:'save','moment-save':'save','profile-export':'save','activity-stop':'back','invite-yes':'follow','invite-later':'moon','invite-off':'moon','pulse-play':'wave','pulse-rest':'rest','pulse-sound':'heart','pulse-close':'back','cinema-pause':'rest','cinema-skip':'play'};
const actions={wave:'wave',raise:'wave',spin:'spin',bubbles:'bubble',bow:'wave',stretch:'wave',follow:'follow',listen:'shell',rest:'rest',bye:'back',talk:'chat'};
const games={race:'follow',hide:'sonar',resonance:'shell',garden:'flower',guide:'compass',photo:'camera'};
const fine=matchMedia('(hover:hover) and (pointer:fine)'),systemReduce=matchMedia('(prefers-reduced-motion:reduce)');let recent=null,closed=0,opened=0,feedbackCount=0;
function reduced(){return systemReduce.matches||!!window.AbyssPresentation?.settings.reduce||!!$('#reduce')?.checked}
function policy(){document.body.classList.toggle('motion-reduced',reduced());document.body.classList.toggle('ocean-pointer',fine.matches&&!reduced());if(reduced()){for(const ghost of document.querySelectorAll('.motion-ghost,.cursor-bubble'))ghost.remove();for(const el of document.querySelectorAll('.motion-enter,.motion-feedback'))el.classList.remove('motion-enter','motion-feedback')}}
const processed=new WeakMap(),dialogs=new WeakSet();
function kind(b){return ids[b.id]||actions[b.dataset.action]||games[b.dataset.play]||(b.hasAttribute('data-close')||b.hasAttribute('data-exit')?'back':b.dataset.region!==undefined?'compass':null)}
function icon(b,k){const existing=b.querySelector(':scope > .ocean-icon');if(existing?.dataset.icon===k)return;existing?.remove();const svg=document.createElementNS(ns,'svg');svg.classList.add('ocean-icon');svg.dataset.icon=k;svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');svg.innerHTML=shapes[k];b.prepend(svg)}
function enter(el){if(el.id==='cinema'||el.classList.contains('motion-ghost')||reduced())return;el.classList.remove('motion-enter');void el.offsetWidth;el.classList.add('motion-enter');opened++}
function snapshot(d){if(!recent||recent.el!==d||performance.now()-recent.at>500||reduced()||d.id==='cinema')return;const {rect}=recent;if(!rect.width||!rect.height)return;const ghost=d.cloneNode(true);ghost.removeAttribute('id');ghost.querySelectorAll('[id]').forEach(n=>n.removeAttribute('id'));ghost.removeAttribute('aria-labelledby');ghost.setAttribute('aria-hidden','true');ghost.inert=true;ghost.className='motion-ghost';ghost.setAttribute('open','');ghost.style.cssText=`position:fixed;left:${rect.left}px;top:${rect.top}px;width:${rect.width}px;height:${rect.height}px;margin:0;pointer-events:none;z-index:10000;`;document.body.append(ghost);setTimeout(()=>ghost.remove(),180);closed++}
function scan(){for(const b of document.querySelectorAll('button')){if(b.closest('.motion-ghost'))continue;const k=kind(b);if(k)icon(b,k)}for(const d of document.querySelectorAll('dialog')){if(dialogs.has(d)||d.classList.contains('motion-ghost'))continue;dialogs.add(d);processed.set(d,d.open);d.addEventListener('close',()=>snapshot(d))}for(const el of document.querySelectorAll('dialog,#invitation,#activity-bar,#photo-bar,#nearby,#toast')){if(el.classList.contains('motion-ghost'))continue;const visible=el.tagName==='DIALOG'?el.open:!el.hidden&&(el.id!=='toast'||el.classList.contains('show'));const before=processed.get(el);if(visible&&!before)enter(el);processed.set(el,visible)}}
let scheduled=false;const observer=new MutationObserver(records=>{const relevant=records.some(r=>{const el=r.target;if(el.closest?.('.motion-ghost'))return false;if(r.type==='attributes')return el.matches('dialog,#invitation,#activity-bar,#photo-bar,#nearby,#toast');return el.closest?.('button,dialog')||[...r.addedNodes].some(n=>n.nodeType===1&&!n.classList.contains('motion-ghost')&&(n.matches('button,dialog')||n.querySelector('button,dialog')))});if(!relevant||scheduled)return;scheduled=true;queueMicrotask(()=>{scheduled=false;scan()})});observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['open','hidden','class']});
// Capture an exiting dialog before game code synchronously closes it. Input/focus remains game-owned.
function remember(){const el=document.querySelector('dialog[open]:not(#cinema):not(.motion-ghost)');if(el)recent={el,rect:el.getBoundingClientRect(),at:performance.now()}}
document.addEventListener('pointerdown',remember,true);document.addEventListener('keydown',e=>{if(['Escape','Enter','Space'].includes(e.code))remember()},true);
document.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse')return;document.body.classList.add('pointer-pressed')},true);addEventListener('pointerup',()=>document.body.classList.remove('pointer-pressed'));addEventListener('blur',()=>document.body.classList.remove('pointer-pressed'));
let trailAt=0;document.addEventListener('pointermove',e=>{if(e.pointerType!=='mouse'||!fine.matches||reduced()||e.target.closest('dialog,input,textarea,select')||performance.now()-trailAt<85||document.querySelectorAll('.cursor-bubble').length>=8)return;trailAt=performance.now();const dot=document.createElement('i');dot.className='cursor-bubble';dot.setAttribute('aria-hidden','true');dot.style.left=e.clientX+'px';dot.style.top=e.clientY+'px';document.body.append(dot);setTimeout(()=>dot.remove(),650)},{passive:true});
function feedback(b){if(!b||b.disabled||reduced())return;feedbackCount++;b.classList.remove('motion-feedback');void b.offsetWidth;b.classList.add('motion-feedback');setTimeout(()=>b.classList.remove('motion-feedback'),420);if(b.id==='photo-save'){const flash=document.createElement('div');flash.className='camera-exposure';flash.setAttribute('aria-hidden','true');document.body.append(flash);setTimeout(()=>flash.remove(),260)}}
document.addEventListener('click',e=>feedback(e.target.closest('button')),true);
document.addEventListener('change',e=>{if(e.target.id==='reduce')policy()});addEventListener('abyss-presentation-change',policy);fine.addEventListener('change',policy);systemReduce.addEventListener('change',policy);
scan();policy();window.AbyssMotion={diagnostics:()=>({reduced:reduced(),customCursor:document.body.classList.contains('ocean-pointer'),icons:document.querySelectorAll('.ocean-icon').length,opened,closed,feedbackCount,ghosts:document.querySelectorAll('.motion-ghost').length})};
})();
