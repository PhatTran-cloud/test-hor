import {shotAt, PALETTE as C} from './board.mjs';

const W=1920,H=1080;
export const clamp=x=>Math.max(0,Math.min(1,x));
export const ease=x=>{const p=clamp(x);return p*p*(3-2*p);};
const lerp=(a,b,p)=>a+(b-a)*p;
const n=x=>Number(x.toFixed(3));
const group=(id,body,attrs='')=>`<g data-object-id="${id}" ${attrs}>${body}</g>`;
const rect=(x,y,w,h,fill,extra='')=>`<rect x="${n(x)}" y="${n(y)}" width="${n(w)}" height="${n(h)}" fill="${fill}" ${extra}/>`;
const circle=(x,y,r,fill,extra='')=>`<circle cx="${n(x)}" cy="${n(y)}" r="${n(r)}" fill="${fill}" ${extra}/>`;
const line=(x,y,a,b,color,width=3,extra='')=>`<path d="M${n(x)},${n(y)} L${n(a)},${n(b)}" fill="none" stroke="${color}" stroke-width="${width}" ${extra}/>`;
const text=(x,y,value,size=28,color=C.ice,extra='')=>`<text x="${x}" y="${y}" font-family="DejaVu Sans Mono,monospace" font-size="${size}" fill="${color}" ${extra}>${value}</text>`;
const path=(d,fill,stroke=C.ink,width=4,extra='')=>`<path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${width}" stroke-linejoin="round" stroke-linecap="round" ${extra}/>`;
const seed=i=>{const x=Math.sin(i*127.1+311.7)*43758.5453123;return x-Math.floor(x);};
const STAR_POSITIONS=Array.from({length:145},(_,i)=>({x:seed(i+9)*W,y:seed(i+150)*H,r:i%19===0?2.3:lerp(.5,1.5,seed(i+70)),a:lerp(.22,.8,seed(i+510))}));
const defs=`<defs>
<radialGradient id="space"><stop stop-color="#172c3a"/><stop offset=".55" stop-color="#0b1a2a"/><stop offset="1" stop-color="#050d19"/></radialGradient>
<radialGradient id="glass"><stop stop-color="#132a34"/><stop offset=".66" stop-color="#071522"/><stop offset="1" stop-color="#020a12"/></radialGradient>
<linearGradient id="hull" x1="0" y1="0" x2=".75" y2="1"><stop stop-color="#adc4be"/><stop offset=".43" stop-color="#607f87"/><stop offset="1" stop-color="#213a46"/></linearGradient>
<linearGradient id="rock"><stop stop-color="#879492"/><stop offset=".45" stop-color="#3f5661"/><stop offset="1" stop-color="#1b2a38"/></linearGradient>
<linearGradient id="panel" x2="0" y2="1"><stop stop-color="#192f41"/><stop offset="1" stop-color="#071629"/></linearGradient>
<linearGradient id="cuff"><stop stop-color="#a9bdb5"/><stop offset=".65" stop-color="#47616d"/><stop offset="1" stop-color="#203645"/></linearGradient>
<radialGradient id="vignette"><stop offset=".55" stop-color="#02050d" stop-opacity="0"/><stop offset="1" stop-color="#02050d" stop-opacity=".65"/></radialGradient>
<clipPath id="windowClip"><circle cx="1330" cy="420" r="304"/></clipPath>
<clipPath id="doorClip"><path d="M1090 254 L1390 254 L1480 345 L1480 622 L1390 710 L1090 710 L1000 622 L1000 345 Z"/></clipPath>
</defs>`;

function stars({warp=0,cx=1100,cy=430,scale=1,tx=0,ty=0}={}) {
  const warpPoint=(x,y)=>{const dx=x-cx,dy=y-cy,r=Math.hypot(dx,dy);const k=warp*58*Math.exp(-(((r-245)/180)**2));return [x+dx/(r||1)*k,y+dy/(r||1)*k];};
  let body=STAR_POSITIONS.map(p=>{const [x,y]=warpPoint(p.x,p.y);return circle(x,y,p.r,C.ice,`opacity="${n(p.a)}"`);}).join('');
  for(const [x,y] of [[1132,300],[1440,516]]) {const [px,py]=warpPoint(x,y);body+=line(px-9,py,px+9,py,C.ice,1.2)+line(px,py-9,px,py+9,C.ice,1.2)+circle(px,py,2.5,'#edf1df');}
  return group('starfield_01',body,`transform="translate(${tx},${ty}) scale(${scale})"`);
}

function station(x,y,s,aperture=1) {
  let panels='';
  for(const side of [-1,1]) {
    const px=side===-1?-324:154;
    panels+=path(`M${px} -75 L${px+158} -58 L${px+148} 118 L${px-13} 100 Z`,'url(#panel)',C.ink,6);
    for(let i=1;i<6;i++)panels+=line(px+i*26,-71+i*3,px+i*26-10,105+i*3,'#335668',2);
    for(let i=1;i<5;i++)panels+=line(px-3,-74+i*37,px+151,-55+i*37,'#335668',2);
    panels+=line(side*129,28,side*189,28,'#8aa19c',13)+line(side*129,25,side*189,25,C.ink,3);
  }
  const body=panels+path('M-111 -133 L81 -117 L135 -79 L135 127 L54 164 L-117 132 L-151 71 L-151 -71 Z','url(#hull)',C.ink,7)
  +path('M-111 -133 L81 -117 L135 -79 L-44 -74 L-151 -71 Z','#9eb4ad',C.ink,5)
  +path('M83 -114 L135 -79 L135 127 L80 91 Z','#2c4755',C.ink,5)
  +line(-95,118,83,145,'#152936',5)+line(-142,-58,-142,55,'#a3b8b0',4)
  +path('M-66 -191 L14 -178 L13 -116 L-43 -121 Z','#667e82',C.ink,5)
  +line(11,-177,66,-225,C.ice,7)+path('M46 -249 Q91 -260 98 -209 Q78 -190 57 -208 Z','#8aabaa',C.ink,4)
  +line(133,-14,229,-27,'#bac3b1',8)+path('M211 -53 Q251 -72 271 -12 Q247 19 221 4 Z','#6e9294',C.ink,5)
  +circle(-20,25,82,'#14303b',`stroke="${C.ink}" stroke-width="7"`)
  +circle(-20,25,69,C.ice,`opacity=".32"`)
  +`<ellipse cx="-20" cy="25" rx="64" ry="${n(Math.max(2,64*aperture))}" fill="#020911"/>`
  +path(`M-75 ${n(24-25*aperture)} Q-20 ${n(-25*aperture)} 31 ${n(15-22*aperture)}`,'none',C.teal,2,`opacity="${n(.6*aperture)}"`)
  +Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return circle(-20+76*Math.cos(a),25+76*Math.sin(a),3.5,'#839f9b');}).join('')
  +rect(-93,98,40,11,C.amber)+rect(37,124,27,7,'#cfbb82')
  +line(-120,-32,-76,-40,'#142b35',4)+line(-120,-8,-80,-13,'#142b35',4)
  +text(36,101,'47',17,C.ice)+path('M-101 129 L-45 143 L-46 182 L-91 177 Z','#2b4351',C.ink,5);
  return group('station_01',body,`transform="translate(${n(x)},${n(y)}) scale(${n(s)})"`);
}

function jupiter() {
  const x=1600,y=310,r=153;
  return group('jupiter_01',`<defs><clipPath id="jupiterClip">${circle(x,y,r,'white')}</clipPath></defs>`+circle(x,y,r,'#9e8772')+`<g clip-path="url(#jupiterClip)" transform="rotate(-13 ${x} ${y})">`+Array.from({length:10},(_,i)=>path(`M${x-r-5} ${y-r+i*33} Q${x} ${y-r+i*33+27} ${x+r+5} ${y-r+i*33-9} L${x+r+5} ${y-r+i*33+15} Q${x} ${y-r+i*33+55} ${x-r-5} ${y-r+i*33+24} Z`,['#c1a286','#715d54','#a7866d','#d1b694'][i%4],'none',0)).join('')+`<ellipse cx="${x+63}" cy="${y+42}" rx="29" ry="13" fill="#7f5147"/></g>`+circle(x,y,r,'none',`stroke="#1a1e25" stroke-width="4"`));
}

function rock(x,y,s,i) {
  let points='';for(let k=0;k<8;k++){const a=k*Math.PI/4,r=lerp(31,47,seed(i*9+k));points+=`${n(Math.cos(a)*r)},${n(Math.sin(a)*r)} `;}
  return `<g transform="translate(${n(x)},${n(y)}) rotate(${n(seed(i)*210)}) scale(${n(s)})"><polygon points="${points}" fill="url(#rock)" stroke="${C.ink}" stroke-width="3.5"/>`+path('M-29 -9 L-11 -24 L17 -18 L7 7 L-16 12 Z','#58737b','none',0)+path('M7 7 L17 -18 L31 11 L13 26 Z','#203341','none',0)+circle(-9,-4,7,'#304750',`stroke="#7a8d8c" stroke-width="2"`)+circle(15,17,3,'#223640')+'</g>';
}

function belt(cx,cy,rx,ry,contract=0,organic=0) {
  const c=lerp(1,.83,contract);let body='';
  if(organic>0) {
    for(let i=0;i<74;i++) {const a=i/74*Math.PI*2,inner=.40+seed(i+37)*.13;body+=path(`M${n(cx+rx*inner*Math.cos(a))} ${n(cy+ry*inner*Math.sin(a))} Q${n(cx+rx*.65*Math.cos(a+.018))} ${n(cy+ry*.65*Math.sin(a+.018))} ${n(cx+rx*.92*Math.cos(a))} ${n(cy+ry*.92*Math.sin(a))}`,'none',i%4===0?'#78968f':'#3b5d65',lerp(2,5,seed(i+89)),`opacity="${n(organic*.72)}"`);}
    body+=`<ellipse cx="${cx}" cy="${cy}" rx="${n(rx*.49)}" ry="${n(ry*.66)}" fill="#01060c" opacity="${n(organic)}"/>`;
  }
  for(let i=0;i<38;i++){const a=i/38*Math.PI*2,rr=lerp(.94,1.07,seed(i+123));body+=rock(cx+rx*c*rr*Math.cos(a),cy+ry*c*rr*Math.sin(a),lerp(.58,1.22,seed(i+92)),i+1);}
  return group('belt_01',body);
}

function lens(cx,cy,r,gaze=0,amount=1) {
  const shift=92*gaze;let body=`<ellipse cx="${n(cx+shift)}" cy="${cy}" rx="${n(r*.68)}" ry="${n(r*.90)}" fill="#02070e" opacity="${amount}"/>`;
  for(let i=0;i<3;i++)body+=path(`M${n(cx-r*(1+.085*i))} ${cy-80} Q${n(cx-r*.7+shift)} ${cy-r*1.28} ${n(cx+r*.3+shift)} ${cy-r*.87}`,'none',i===0?'#81b6bc':'#37525f',i===0?3:1.5,`opacity="${n(amount*(.45-i*.1))}"`);
  return group('lens_01',body);
}

function windowFrame() {
  let body=circle(1330,420,334,'none',`stroke="#182b38" stroke-width="57"`)+circle(1330,420,321,'none',`stroke="#607d85" stroke-width="23"`)+circle(1330,420,331,'none',`stroke="#b1beb2" stroke-width="4"`)+circle(1330,420,309,'none',`stroke="#132534" stroke-width="13"`);
  for(let i=0;i<12;i++){const a=i/12*Math.PI*2,x=1330+345*Math.cos(a),y=420+345*Math.sin(a);body+=circle(x,y,8,'#253c49',`stroke="#a1b3ac" stroke-width="2"`)+line(x-4,y+2,x+4,y-2,'#afbab0',1.5);}
  body+=path('M1088 201 Q1188 113 1336 126','none','#ccd5c4',3,`opacity=".35"`)+path('M1365 184 L1511 301 L1410 306 Z','#789f9f','none',0,`opacity=".08"`);
  body+=path('M1780 100 L1870 155 L1870 882 L1720 940','none','#253e4c',49)+path('M1780 100 L1870 155 L1870 882 L1720 940','none','#79908c',3,`opacity=".3"`);
  return group('porthole_01',body);
}

function glove(x,y,s,rotation=0,color='blue',id='glove_01',knuckle=false) {
  const light=color==='blue'?'#aac2be':'#c0aa8d',middle=color==='blue'?'#527685':'#806c56',dark=color==='blue'?'#293f50':'#423a35';
  const shape=knuckle?'M-78 140 L-89 22 Q-91 -18 -48 -42 L-23 -58 Q1 -76 20 -53 Q41 -69 58 -42 Q87 -41 91 -10 L88 48 Q82 70 61 75 L50 137 Z':'M-68 131 L-80 42 Q-103 24 -111 2 Q-117 -28 -90 -38 Q-74 -41 -53 -16 L-50 -86 Q-48 -118 -21 -119 Q2 -122 8 -90 L14 -138 Q22 -162 44 -152 Q69 -145 66 -118 L59 -54 Q88 -72 107 -48 Q122 -33 108 -11 L76 63 L63 137 Z';
  let body=path(shape,middle,C.ink,6)+path(knuckle?'M-69 121 L-67 26 Q-65 -16 -27 -31 L-11 -40 L-2 10 L47 11 L38 125 Z':'M-62 115 L-65 46 Q-88 24 -97 5 L-86 -20 L-39 26 L-31 -98 L-12 -104 L-2 17 L24 22 L43 -140 L52 -133 L38 41 L71 10 L83 -34 L99 -33 L61 70 L43 123 Z',light,'none',0);
  body+=path('M-78 116 L62 124 L68 169 L-83 166 Z',dark,C.ink,5)+path('M-79 129 L64 136 L64 147 L-82 142 Z',color==='blue'?C.amber:'#d4d9c1',C.ink,2)+path('M-81 167 L68 170 L102 380 L-127 375 Z','url(#cuff)',C.ink,6);
  const joints=knuckle?[[-47,-18],[-2,-29],[44,-17]]:[[-24,-57],[44,-75],[72,20]];
  for(const [a,b]of joints)body+=rect(a-14,b-8,28,18,dark,'rx="6"')+line(a-9,b-3,a+9,b-3,light,2);
  body+=line(-66,91,48,98,dark,4)+path('M-37 31 Q-17 50 17 41','none',dark,3);
  return group(id,body,`transform="translate(${n(x)},${n(y)}) rotate(${n(rotation)}) scale(${n(s)})"`);
}

function consoleView({day=47,range=false,received=false,send=false,insert=false}={}) {
  let body='';
  const x=insert?178:177,y=insert?102:623,s=insert?1.80:1;
  body+=path('M-39 -21 L865 -21 L910 455 L-102 455 Z','#243945',C.ink,7)+path('M-39 -21 L865 -21 L829 7 L-57 7 Z','#6e8e93',C.ink,5);
  body+=rect(17,24,736,309,'#0a111c',`rx="27" stroke="#688887" stroke-width="5"`)+rect(38,43,695,270,'#0a2028','rx="15"');
  body+=text(61,89,`LOG / DAY ${String(day).padStart(2,'0')}`,25,C.teal)+line(59,103,711,103,'#2f615f',2);
  body+=text(66,142,'TX',24,C.teal)+text(66,218,'RX',24,received?C.ice:'#3b6667');
  body+=line(120,151,680,151,'#29484f',2)+line(120,229,680,229,'#29484f',2);
  if(send)body+=text(150,146,'HELLO  HELLO  HELLO',25,C.teal);
  if(received){for(let i=0;i<3;i++)body+=path(`M${153+i*110} 229 L${167+i*110} 229 L${177+i*110} 190 L${189+i*110} 244 L${201+i*110} 229 L${230+i*110} 229`,'none',C.ice,3);}
  if(range)body+=text(125,286,'EST. 600 000 km',34,C.ice);
  else body+=text(68,283,'RX / MONITOR',21,'#376766');
  body+=rect(55,359,165,57,'#0d1b27',`rx="9" stroke="#577577" stroke-width="3"`)+text(76,396,'TRANSMIT',22,C.ice);
  for(let i=0;i<5;i++)body+=circle(286+i*83,386,23,'#151f2c',`stroke="#668086" stroke-width="4"`)+line(286+i*83,386,298+i*83,376,'#aec2b4',2);
  body+=rect(753,72,94,99,'#14202d',`rx="10" stroke="#738a85" stroke-width="3"`)+text(765,108,'RTT',20,C.teal)+text(764,143,received?'4.0s':'---',21,C.ice);
  for(let i=0;i<6;i++)body+=line(768,197+i*15,839,197+i*15,'#12212e',4);
  return group('console_01',body,`transform="translate(${x},${y}) scale(${s})"`);
}

function interior(board,f,view,progress) {
  const e=board.events, u=board.sections[0].speech.utterances, range=f>=u[1].start_frame;
  const late=['lens','look','blink'].includes(view), gaze=late?ease((f-e.gaze_start)/(e.gaze_end-e.gaze_start)):0;
  let body=rect(0,0,W,H,'#0c1825')+rect(0,789,W,291,'#0b1421');
  body+=`<g clip-path="url(#windowClip)">`+rect(989,90,681,661,'url(#space)')+stars({warp:late?1:0,cx:1308+gaze*70,cy:420});
  if(late)body+=lens(1330,418,195,gaze,.95);
  body+='</g>'+windowFrame();
  if(!late)body+=consoleView({day:view==='answer'||view==='memory'?0:47,range:range&&view!=='memory',received:view!=='memory',send:view==='answer'});
  if(['receive','listen','answer','memory','lens','look'].includes(view)){
    const stopped=view==='answer'?ease(progress*.9):0;
    body+=glove(view==='memory'?326:361,view==='memory'?811:880+stopped*20,view==='lens'||view==='look'?.63:.77,view==='memory'?-20:-36);
  }
  return body;
}

function radioWaves(e,f,mount) {
  const origin={x:mount.x+271*mount.scale,y:mount.y-12*mount.scale};
  let body='';for(const send of e.send_frames){const p=(f-send)/60;if(p>=0&&p<1.55){const x=origin.x+p*570,y=origin.y-p*110;body+=path(`M${n(x-13)} ${n(y-23)} Q${n(x+16)} ${n(y)} ${n(x-13)} ${n(y+23)}`,'none',C.teal,4,`opacity="${n(clamp(1-p/1.55))}"`);}}
  return body;
}

function exterior(board,f,view,p) {
  const e=board.events, contracted=ease((f-e.contraction_start)/(e.contraction_end-e.contraction_start));
  let body=rect(0,0,W,H,'url(#space)')+stars();
  if(view==='behind')return body+station(1370,575,lerp(1.35,1.21,ease(p)))+rect(0,0,835,H,C.void,'opacity=".17"');
  if(view==='send')return body+jupiter()+station(503,592,.70)+radioWaves(e,f,{x:503,y:592,scale:.70});
  if(view==='stone')return body+group('belt_01',rock(955,548,5.4,4)+rock(1523,224,1.7,7)+rock(320,748,1.2,8));
  if(view==='contract') {
    const scale=lerp(1.1,.92,ease(p));
    return body+`<g transform="translate(${n(960*(1-scale))},${n(515*(1-scale))}) scale(${n(scale)})">`+belt(910,450,876,346,contracted,0)+station(1030,570,.26)+'</g>';
  }
  if(view==='eye') {
    const reveal=ease(p*1.8), scale=lerp(.92,.84,ease(p));
    return body+`<g transform="translate(${n(960*(1-scale))},${n(515*(1-scale))}) scale(${n(scale)})">`+belt(910,450,876,346,1,reveal)+lens(910,450,285,0,reveal*.45)+station(1030,570,.26)+'</g>';
  }
  if(view==='station-blink') {
    const opening=ease((f-e.blink_peak)/(e.blink_open-e.blink_peak));
    return body+belt(780,423,950,368,1,1)+lens(838,423,285,.8,.4)+station(1030,611,1.35,opening);
  }
  return body;
}

function receiverConsole() {
  const body=path('M48 715 L595 705 L649 1098 L-68 1098 Z','#3b3933',C.ink,7)+rect(63,747,458,175,'#0b161d',`rx="17" stroke="#857a60" stroke-width="5"`)+text(91,790,'INCOMING / LOG 47',25,C.amber)+line(88,809,488,809,'#6a5745',2)
    +path('M89 864 L121 864 L134 837 L145 883 L157 858 L184 864 L201 849 L218 870 L244 864 L268 836 L285 885 L302 864 L355 864 L369 844 L385 879 L400 864 L483 864','none',C.amber,3)
    +rect(169,957,172,76,'#6e5940',`rx="9" stroke="#bc9b72" stroke-width="3"`)+text(193,1006,'REPLY',29,'#e6cfa1');
  return group('console_02',body);
}

function door(board,f,view) {
  const e=board.events, hit=f-e.knock_frame;
  const impulse=hit>=0&&hit<65?Math.sin(hit*.48)*Math.exp(-hit/17)*3.5:0;
  let frame=path('M819 80 L1622 80 L1704 164 L1704 1080 L739 1080 L739 164 Z','#273c46',C.ink,10)+path('M842 122 L1594 122 L1658 188 L1658 1080 L784 1080 L784 188 Z','url(#hull)',C.ink,7)
    +path('M842 122 L1594 122 L1594 184 L842 184 Z','#adc1b5',C.ink,4)+path('M1537 197 L1658 188 L1658 1080 L1557 1080 Z','#2c434d',C.ink,5);
  frame+=path('M1074 228 L1407 228 L1504 325 L1504 638 L1407 737 L1074 737 L975 638 L975 325 Z','#294855',C.ink,8)+path('M1090 254 L1390 254 L1480 345 L1480 622 L1390 710 L1090 710 L1000 622 L1000 345 Z','url(#glass)',C.ink,6);
  const rise=ease((f-(e.knock_frame-90))/80),contact=ease((f-e.knock_frame)/12);
  if(view==='knock') {
    frame+=`<g clip-path="url(#doorClip)">`+glove(1243,lerp(815,518,rise)+impulse,.98,lerp(-13,4,rise),'blue','glove_01',true)+rect(993,244,505,475,'#7da6a7',`opacity="${n(.07+contact*.045)}"`);
    if(hit>=0)frame+=path('M1176 473 Q1190 446 1212 465 M1235 448 Q1257 438 1273 460 M1294 465 Q1321 453 1337 475','none','#b7d5cf',3,`opacity="${n(.34*contact)}"`);
    frame+='</g>';
  }
  frame+=path('M1041 331 L1075 304 L1308 692 L1287 709 Z','#d0ded0','none',0,'opacity=".07"')+path('M1187 385 L1214 414 L1242 380','none','#bdd5c8',2,'opacity=".35"');
  const bolts=[[998,304],[1042,253],[1440,281],[1480,332],[1481,653],[1432,703],[1050,706],[992,649]];
  for(const [x,y]of bolts)frame+=circle(x,y,9,'#1d3440',`stroke="#a8bbb0" stroke-width="2"`);
  frame+=rect(1531,798,74,137,'#192c37',`rx="15" stroke="#668382" stroke-width="4"`)+rect(1548,817,39,28,C.amber,'rx="4"')+path('M1548 879 L1589 879 L1589 949 L1548 949 Z','#7d9690',C.ink,4);
  frame+=line(846,960,949,960,'#1d3340',5)+line(846,982,924,982,'#1d3340',5);
  return group('door_02',frame);
}

function receiver(board,f,view,p) {
  let body=rect(0,0,W,H,'#101c28')+door(board,f,view)+receiverConsole();
  if(view==='warning') {
    const retreat=ease(p*1.6);
    body+=glove(lerp(289,89,retreat),lerp(1062,1218,retreat),.66,-24,'earth','glove_02');
  }
  return body;
}

export function renderFrame(board,frame) {
  const f=Math.max(0,Math.min(board.duration_frames-1,Math.floor(frame))), shot=shotAt(board,f);
  if(!shot)throw new Error(`No storyboard shot at ${f}`);
  const p=clamp((f-shot.start_frame)/Math.max(1,shot.duration_frames-1)),v=shot.view;
  let body;
  if(shot.scene_id==='space_01')body=exterior(board,f,v,p);
  else if(shot.scene_id==='receiver_02')body=receiver(board,f,v,p);
  else if(v==='distance')body=rect(0,0,W,H,'#0b1520')+consoleView({day:0,range:true,received:true,send:true,insert:true});
  else body=interior(board,f,v,p);
  const cameraScale=['receive','look','knock'].includes(v)?1+(v==='look'?.03:.04)*ease(p):1;
  if(cameraScale!==1)body=`<g transform="translate(${n(960*(1-cameraScale))},${n(540*(1-cameraScale))}) scale(${n(cameraScale)})">${body}</g>`;
  body+=rect(0,0,W,H,'url(#vignette)');
  if(v==='blink') {
    const closed=ease((f-board.events.blink_close)/(board.events.blink_peak-board.events.blink_close));
    body+=path(`M0 0 L1920 0 L1920 ${n(closed*570)} Q960 ${n(closed*590)} 0 ${n(closed*570)} Z`,C.void,'none',0)
      +path(`M0 1080 L1920 1080 L1920 ${n(1080-closed*570)} Q960 ${n(1080-closed*590)} 0 ${n(1080-closed*570)} Z`,C.void,'none',0);
  }
  if(v==='station-blink')body+=rect(0,0,W,H,C.void,`opacity="${n(clamp(1-(f-board.events.blink_peak)/12))}"`);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" data-shot="${shot.id}" data-frame="${f}" style="display:block;background:${C.night}">${defs}${body}</svg>`;
}
