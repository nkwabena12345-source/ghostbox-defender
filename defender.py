from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GHOSTBOX DEFENDER ULTRA+</title>
<link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiR0hPU1RCT1ggREVGQ09EIEVMVFJBK1MiLCJzaG9ydF9uYW1lIjoiR2hvc3Rib3giLCJzdGFydF91cmwiOiIvIiwiZGlzcGxheSI6InN0YW5kYWxvbmUiLCJiYWNrZ3JvdW5kX2NvbG9yIjoiIzAwMDAwMCIsInRoZW1lX2NvbG9yIjoiIzAwZmY4OCJ9">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Share Tech Mono',monospace}
body{background:#000;color:#00ff88}
header{padding:12px;text-align:center;border-bottom:2px solid #00ff88;position:sticky;top:0;background:#000;z-index:99}
.container{max-width:1000px;margin:0 auto;padding:10px;display:grid;gap:10px}
.card{background:#000e;border:2px solid #00ff88;border-radius:12px;padding:12px;box-shadow:0 0 20px #00ff8833}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:700px){.grid2{grid-template-columns:1fr}}
#radarWrap{position:relative;aspect-ratio:1;max-width:380px;margin:auto;background:radial-gradient(#001a0a,#000);border-radius:50%;border:2px solid #00ff88;overflow:hidden}
.sweep{position:absolute;top:50%;left:50%;width:50%;height:2px;background:linear-gradient(90deg,transparent,#00ff88);transform-origin:left;animation:sweep 3s linear infinite}
@keyframes sweep{from{transform:rotate(0)}to{transform:rotate(360deg)}}
#camWrap{position:relative;aspect-ratio:4/3;background:#111;border-radius:10px;overflow:hidden;display:none;border:2px solid #00ff88}
#cam{width:100%;height:100%;object-fit:cover}
#ghostOverlay{position:absolute;inset:0;display:none;place-items:center;background:radial-gradient(transparent,#ff000044)}
#ghostOverlay b{font-size:5em;animation:float 0.5s infinite alternate}
@keyframes float{from{transform:translateY(0)}to{transform:translateY(-10px)}}
.btn{padding:12px;background:#00ff88;color:#000;border:none;border-radius:8px;font-weight:bold;width:100%;margin:4px 0;cursor:pointer}
.btn.off{background:#111;color:#00ff88;border:2px solid #00ff88}
#emf{height:18px;background:#111;border-radius:10px;overflow:hidden;border:1px solid #00ff88}
#emfFill{height:100%;width:5%;background:linear-gradient(90deg,#00ff88,#ff0,#f00);transition:0.3s}
#log{height:140px;overflow-y:auto;background:#000a;padding:8px;border-radius:8px;font-size:0.8em;border:1px solid #00ff8811}
#map{height:220px;border-radius:10px;border:2px solid #00ff88}
.evp{text-align:center;min-height:35px;font-size:1.4em;text-shadow:0 0 10px #00ff88}
</style>
</head>
<body>
<header><h1>👻 GHOSTBOX ULTRA+ 💾 PRO</h1><small>SAVES FOREVER • INSTALLABLE APP</small></header>
<div class="container">
<div class="grid2">
<div class="card">
<h3>📡 RADAR + 👁️ GHOST CAM</h3>
<div id="radarWrap"><canvas id="radar"></canvas><div class="sweep"></div></div>
<div id="camWrap"><video id="cam" autoplay playsinline muted></video><div id="ghostOverlay"><b>👻</b></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
<button class="btn" id="pBtn" onclick="togglePower()">ACTIVATE</button>
<button class="btn off" onclick="scan()">SCAN [S]</button>
<button class="btn off" onclick="toggleCam()">📷 CAM</button>
<button class="btn off" onclick="speakGhost()">🗣️ TALK</button>
</div>
</div>
<div class="card">
<h3>📟 EMF: <span id="emfVal">0.4</span> mG</h3><div id="emf"><div id="emfFill"></div></div>
<h3>🎙️ SPIRIT BOX</h3><div class="evp" id="evp">---</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:8px">
<div style="text-align:center;border:1px solid #00ff88;padding:6px;border-radius:8px">SHIELD<br><span id="shield" style="font-size:1.6em">100%</span></div>
<div style="text-align:center;border:1px solid #00ff88;padding:6px;border-radius:8px">GHOSTS<br><span id="count" style="font-size:1.6em">0</span></div>
<div style="text-align:center;border:1px solid #00ff88;padding:6px;border-radius:8px">RANK<br><span id="rank" style="font-size:1.1em">NOVICE</span></div>
</div>
<h3 style="margin-top:10px">🌍 HAUNTED MAP - Accra</h3><div id="map"></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
<button class="btn off" onclick="shareScore()">📸 SHARE</button>
<button class="btn off" onclick="resetData()">🗑️ RESET</button>
</div>
</div>
</div>
<div class="card"><h3>📜 PARANORMAL LOG - SAVED</h3><div id="log"></div></div>
</div>
<script>
let power=false,ghosts=0,shield=100,camOn=false,map,dots=[],markers=[];
let words=["BEHIND YOU","HELP ME","LEAVE NOW","COLD","DONT LOOK","HE IS HERE","RUN","WE SEE YOU","DEATH","MIRROR","BASEMENT","FOLLOW","LISTEN","GET OUT","I AM HERE","TOUCH","NINE LIVES","ACCRA","OPEN THE DOOR","HIDE"];
let canvas=document.getElementById('radar'),ctx=canvas.getContext('2d');
function resize(){let w=canvas.parentElement.offsetWidth;canvas.width=w*2;canvas.height=w*2;ctx.setTransform(2,0,0,2,0,0)}resize();
function save(){localStorage.setItem('gb_ghosts',ghosts);localStorage.setItem('gb_shield',shield);localStorage.setItem('gb_pins',JSON.stringify(markers.map(m=>m.getLatLng())));localStorage.setItem('gb_log',document.getElementById('log').innerHTML)}
function load(){ghosts=parseInt(localStorage.getItem('gb_ghosts')||0);shield=parseInt(localStorage.getItem('gb_shield')||100);document.getElementById('count').textContent=ghosts;document.getElementById('shield').textContent=shield+'%';document.getElementById('rank').textContent=ghosts<3?'NOVICE':ghosts<6?'HUNTER':ghosts<10?'EXPERT':'GHOST KING';let l=localStorage.getItem('gb_log');if(l)document.getElementById('log').innerHTML=l;let pins=JSON.parse(localStorage.getItem('gb_pins')||'[]');setTimeout(()=>pins.forEach(p=>{if(map){let m=L.marker([p.lat,p.lng],{icon:L.divIcon({html:'👻',className:'',iconSize:[25,25]})}).addTo(map);markers.push(m)}}),1000)}
function log(t){let el=document.getElementById('log');let d=document.createElement('div');d.textContent='['+new Date().toLocaleTimeString()+'] '+t;el.prepend(d);save()}
function togglePower(){power=!power;document.getElementById('pBtn').textContent=power?'ACTIVE ✓':'ACTIVATE';document.getElementById('pBtn').className=power?'btn':'btn off';log(power?'🟢 ULTRA+ DATABASE LOADED - '+ghosts+' ghosts saved':'🔴 OFFLINE');if(power)loop();speak(power?'Welcome back hunter, '+ghosts+' ghosts captured':'Offline')}
function scan(){if(!power)return log('⚠️ Activate!');let e=(Math.random()*10).toFixed(1);document.getElementById('emfVal').innerText=e;document.getElementById('emfFill').style.width=e*10+'%';beep(e);let w=words[Math.floor(Math.random()*words.length)];document.getElementById('evp').textContent=w;speak(w);if(e>6.5){ghostEvent(e)}else{log('🔍 EMF '+e+' mG - clear')}setTimeout(()=>document.getElementById('evp').textContent='---',2500)}
function ghostEvent(e){ghosts++;document.getElementById('count').textContent=ghosts;shield=Math.max(0,shield-12);document.getElementById('shield').textContent=shield+'%';let r=ghosts<3?'NOVICE':ghosts<6?'HUNTER':ghosts<10?'EXPERT':'GHOST KING';document.getElementById('rank').textContent=r;log('👻 GHOST #'+ghosts+' CAPTURED! EMF '+e+' mG!');if(camOn){let o=document.getElementById('ghostOverlay');o.style.display='grid';setTimeout(()=>o.style.display='none',1200)}dots.push({x:Math.random()*160+20,y:Math.random()*160+20,life:120});addMapGhost();save();if(shield<=0){log('💀 SHIELD DOWN!');shield=100;document.getElementById('shield').textContent='100%';save()}}
function loop(){if(!power)return;ctx.clearRect(0,0,400,400);ctx.strokeStyle='#00ff8811';for(let r=20;r<180;r+=35){ctx.beginPath();ctx.arc(100,100,r,0,7);ctx.stroke()}dots=dots.filter(d=>d.life>0);dots.forEach(d=>{ctx.fillStyle='rgba(255,0,80,'+(d.life/120)+')';ctx.shadowBlur=10;ctx.shadowColor='#f00';ctx.beginPath();ctx.arc(d.x,d.y,5,0,7);ctx.fill();d.life--;});ctx.shadowBlur=0;requestAnimationFrame(loop)}
function beep(v){let a=new(window.AudioContext||window.webkitAudioContext)();let o=a.createOscillator();o.frequency.value=100+Number(v)*80;o.connect(a.destination);o.start();o.stop(a.currentTime+0.2)}
function speak(t){if('speechSynthesis' in window){let u=new SpeechSynthesisUtterance(t);u.pitch=0.3;u.rate=0.8;speechSynthesis.speak(u)}}
async function toggleCam(){let w=document.getElementById('camWrap');if(!camOn){try{let s=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'}});document.getElementById('cam').srcObject=s;w.style.display='block';camOn=true;log('📷 Ghost Cam ON')}catch(e){log('❌ Allow camera')}}else{let v=document.getElementById('cam');let s=v.srcObject;if(s)s.getTracks().forEach(t=>t.stop());w.style.display='none';camOn=false;log('📷 Cam OFF')}}
function initMap(){map=L.map('map').setView([5.6037,-0.1870],12);L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);L.marker([5.6037,-0.1870]).addTo(map).bindPopup('📍 Accra Base');if(navigator.geolocation){navigator.geolocation.getCurrentPosition(p=>{map.setView([p.coords.latitude,p.coords.longitude],14);L.marker([p.coords.latitude,p.coords.longitude]).addTo(map).bindPopup('🧍 YOU').openPopup()})}load()}
function addMapGhost(){if(!map)return;let lat=5.6037+(Math.random()-0.5)*0.2,lng=-0.1870+(Math.random()-0.5)*0.2;let m=L.marker([lat,lng],{icon:L.divIcon({html:'👻',className:'',iconSize:[25,25]})}).addTo(map).bindPopup('👻 Ghost #'+ghosts);markers.push(m);save()}
function speakGhost(){let w=document.getElementById('evp').textContent;if(w!=='---')speak(w);else{let r=words[Math.floor(Math.random()*words.length)];document.getElementById('evp').textContent=r;speak(r);setTimeout(()=>document.getElementById('evp').textContent='---',2000)}}
function shareScore(){let t=`I caught ${ghosts} ghosts! Rank ${document.getElementById('rank').textContent} on GHOSTBOX ULTRA+ 👻 https://ghostbox-defender.onrender.com`;if(navigator.share){navigator.share({text:t})}else{navigator.clipboard.writeText(t);alert('Copied!')}}
function resetData(){if(confirm('Reset all '+ghosts+' ghosts?')){localStorage.clear();ghosts=0;shield=100;markers.forEach(m=>map.removeLayer(m));markers=[];document.getElementById('count').textContent=0;document.getElementById('shield').textContent='100%';document.getElementById('rank').textContent='NOVICE';document.getElementById('log').innerHTML='';log('🗑️ Database wiped - fresh start')}}
initMap();log('💾 ULTRA+ Database System Online - '+ghosts+' ghosts loaded from storage');
</script>
</body>
</html>
    """
if __name__=="__main__":
    app.run()
