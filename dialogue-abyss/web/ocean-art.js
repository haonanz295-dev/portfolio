/* Original runtime art: soft ocean shafts and moving floor caustics. No remote assets. */
(()=>{'use strict';const g=window.seaGame,T=window.THREE;if(!g)return;let region=-1,shader=null,beams=[];
function build(){region=g.region;shader=null;beams=[];const floor=g.world.children.find(o=>o.isMesh&&o.geometry.type==='PlaneGeometry');if(floor){floor.material.onBeforeCompile=s=>{s.uniforms.oceanTime={value:0};s.vertexShader='varying vec3 vOceanPosition;\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvOceanPosition=(modelMatrix*vec4(position,1.0)).xyz;');s.fragmentShader='uniform float oceanTime;varying vec3 vOceanPosition;\n'+s.fragmentShader;s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
vec2 p=vOceanPosition.xz*.55;
float wave=sin(p.x+sin(p.y*1.3+oceanTime*.17))*cos(p.y+sin(p.x*.8-oceanTime*.13));
float lace=pow(1.0-abs(wave),18.0);
float sand=.96+.035*sin(p.x*2.8+p.y*.3);
diffuseColor.rgb*=sand*(.86+.16*lace);
diffuseColor.rgb+=vec3(.13,.16,.10)*lace;`);shader=s};floor.material.needsUpdate=true}
const material=new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,blending:T.AdditiveBlending,uniforms:{t:{value:0},strength:{value:region===4?.025:.075}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'varying vec2 vUv;uniform float t;uniform float strength;void main(){float edge=pow(sin(vUv.x*3.14159),2.0);float fade=sin(vUv.y*3.14159);float drift=.85+.15*sin(t*.23+vUv.y*6.0);gl_FragColor=vec4(.72,.95,.80,edge*fade*drift*strength);}'});
for(let i=0;i<7;i++){const beam=new T.Mesh(new T.PlaneGeometry(2.5+i*.7,48),material);beam.position.set(-30+i*11,20,-15-i*8);beam.rotation.z=-.32;beam.rotation.y=.3;g.world.add(beam);beams.push(beam)}
}
function tick(ms){if(g.region!==region)build();if(!g.paused){if(shader)shader.uniforms.oceanTime.value=ms/1000;for(const b of beams)b.material.uniforms.t.value=ms/1000}requestAnimationFrame(tick)}requestAnimationFrame(tick);
})();
