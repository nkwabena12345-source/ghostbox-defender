from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>GHOSTBOX DEFENDER ULTRA</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Share Tech Mono',monospace}
body{background:#000;color:#00ff88;overflow-x:hidden}
header{padding:12px;text-align:center;border-bottom:2px solid #00ff88;background:#000c;position:sticky;top:0;z-index:100}
h1{font-size:1.8em;text-shadow:0 0 15px #00ff88}
.container{max-width:1000px;margin:0 auto;padding:10px;display:grid;gap:10px}
.card{background:#000e;border:2px solid #00ff88;border-radius:12px;padding:12px;box-shadow:0 0 20px #00ff8833}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:700px){.grid2{grid-template-columns:1fr}}
#radarWrap{position:relative;aspect-ratio:1;width:100%;max-width:380px;margin:auto;background:radial-gradient(#001a0a,#000);border-radius:50%;border:2px solid #00ff88;overflow:hidden}
#radar{width:100%;height:100%}
.sweep{position:absolute;top:50%;left:50%;width:50%;height:2px;background:linear-gradient(90deg,transparent,#00ff88);transform-origin:left;animation:sweep 3s linear infinite}
@keyframes sweep{from{transform:rotate(0)}to{transform:rotate(360deg)}}
#camWrap{position:relative;width:100%;aspect-ratio:4/3;background:#111;border-radius:10px;overflow:hidden;display:none;border:2px solid #00ff88}
#cam{width:100%;height:100%;object-fit:cover}
#ghostOverlay{position:absolute;inset:0;display:none;place-items:center;background:radial-gradient(transparent 40%, #ff000044 100%)}
#ghostOverlay b{font-size:5em;filter:drop-shadow(0 0 20px #fff);animation:float 0.5s infinite alternate}
@keyframes float{from{transform:translateY(0) scale(1)}to{transform:translateY(-10px) scale(1.1)}}
.btn{padding:12px;background:#00ff88;color:#000;border:none;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;margin:4px 0}
.btn.off{background:#111;color:#00ff88;border:2px solid #00ff88}
#emf{height:18px;background:#111;border-radius:10px;overflow:hidden;border:1px solid #00ff88}
#emfFill{height:100%;width:5%;background:linear-gradient(90deg,#00ff88,#ff0,#f00);transition:0.3s}
#log{height:140px;overflow-y:auto;background:#000a;padding:8px;border-radius:8px;font-size:0.8em;border:1px solid #00ff8811}
#map{height:200px;border-radius:10px;border:2px solid #00ff88}
.evp{font-size:1.4em;text-align:center;min-height:35px;text-shadow:0 0 10px #00ff88}
</style>
</head>
<body>
<header><h1>👻 GHOSTBOX DEFENDER <span style="border:1px solid #00ff88;padding:2px 6px;border-radius:6px;font-size:0.6em">ULTRA</span> 🛡️</h1></header>
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
<h3 style="margin-top:10px">🎙️ SPIRIT BOX</h3><div class="evp" id="evp">---</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:8px">
<div style="text-align:center;border:1px solid #00ff88;padding:6px;border-radius:8px">SHIELD<br><span id="shield" style="font-size:1.6em">100%</span></div>
<div style="text-align:center;border:1px solid #00ff88;padding:6px;border-radius:8px">GHOSTS<br><span id="count" style="font-size:1.6em">0</span></div>
<div style="text-align:center;border:1px solid #00ff88;padding:6px;border-radius:8px">RANK<br><span id="rank" style="font-size:1.2em">NOVICE</span></div>
</div>
<h3 style="margin-top:10px">🌍 HAUNTED MAP - Accra</h3><div id="map"></div>
<button class="btn off" onclick="shareScore()" style="margin-top:8px">📸 SHARE SCORE</button>
</div>
</div>
<div class="card"><h3>📜 PARANORMAL LOG</h3><div id="log"></div></div>
</div>

<script>
let power=false,ghosts=0,shield=100,camOn=false,map,markers=[];
let words=["BEHIND YOU","HELP ME","LEAVE NOW","COLD","DONT LOOK","HE IS HERE","RUN","WE SEE YOU","DEATH","MIRROR","BASEMENT","FOLLOW","LISTEN","GET OUT","I AM HERE","TOUCH","NINE LIVES","ACCRA","OPEN THE DOOR","HIDE"];
let canvas=document.getElementById('radar'),ctx=canvas.getContext('2d'),dots=[];
function resize(){let w=canvas.parentElement.offsetWidth;canvas.width=canvas.height=w*2;ctx.setTransform(2,0,0,2,0,0)}resize();
function log(t){let l=document.getElementById('log');let d=document.createElement('div');d.textContent='['+new Date().toLocaleTimeString()+'] '+t;l.prepend(d)}
function togglePower(){power=!power;document.getElementById('pBtn').textContent=power?'ACTIVE ✓':'ACTIVATE';document.getElementById('pBtn').className=power?'btn':'btn off';log(power?'🟢 ULTRA ACTIVATED - All systems online':'🔴 OFFLINE');if(power)loop();speak(power?'Ghostbox Defender activated':'System offline')}
function scan(){if(!power)return log('⚠️ Activate first!');let e=(Math.random()*10).toFixed(1);document.getElementById('emfVal').innerText=e;document.getElementById('emfFill').style.width=e*10+'%';beep(e);let w=words[Math.floor(Math.random()*words.length)];document.getElementById('evp').textContent=w;speak(w);if(e>6.5){ghostEvent(e)}else{log('🔍 Scan EMF '+e+' mG - clear') }setTimeout(()=>document.getElementById('evp').textContent='---',2500)}
function ghostEvent(e){ghosts++;document.getElementById('count').textContent=ghosts;shield=Math.max(0,shield-12);document.getElementById('shield').textContent=shield+'%';let r=ghosts<3?'NOVICE':ghosts<6?'HUNTER':ghosts<10?'EXPERT':'GHOST KING';document.getElementById('rank').textContent=r;log('👻 GHOST #'+ghosts+' DETECTED! EMF '+e+' mG!');if(camOn){let o=document.getElementById('ghostOverlay');o.style.display='grid';setTimeout(()=>o.style.display='none',1200)}dots.push({x:Math.random()*160+20,y:Math.random()*160+20,life:120});addMapGhost();if(shield<=0){log('💀 SHIELD DOWN! Rebooting...');shield=100;document.getElementById('shield').textContent='100%';}}
function loop(){if(!power)return;ctx.clearRect(0,0,400,400);ctx.strokeStyle='#00ff8811';for(let r=20;r<180;r+=35){ctx.beginPath();ctx.arc(100,100,r,0,7);ctx.stroke()}dots=dots.filter(d=>d.life>0);dots.forEach(d=>{ctx.fillStyle='rgba(255,0,80,'+(d.life/120)+')';ctx.shadowBlur=10;ctx.shadowColor='#f00';ctx.beginPath();ctx.arc(d.x,d.y,5,0,7);ctx.fill();d.life--;});ctx.shadowBlur=0;requestAnimationFrame(loop)}
function beep(v){let a=new(window.AudioContext||window.webkitAudioContext)();let o=a.createOscillator();o.frequency.value=100+Number(v)*80;o.connect(a.destination);o.start();o.stop(a.currentTime+0.2)}
function speak(t){if('speechSynthesis' in window){let u=new SpeechSynthesisUtterance(t);u.pitch=0.3;u.rate=0.8;u.volume=0.9;speechSynthesis.speak(u)}}
async function toggleCam(){let w=document.getElementById('camWrap');if(!camOn){try{let s=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'}});document.getElementById('cam').srcObject=s;w.style.display='block';camOn=true;log('📷 Ghost Cam ON')}catch(e){log('❌ Cam blocked - allow camera permission');alert('Allow camera for Ghost Cam!')}}else{let v=document.getElementById('cam');let s=v.srcObject;if(s)s.getTracks().forEach(t=>t.stop());w.style.display='none';camOn=false;log('📷 Cam OFF')}}
function initMap(){map=L.map('map').setView([5.6037,-0.1870],12);L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);L.marker([5.6037,-0.1870]).addTo(map).bindPopup('📍 Accra Base - Ghost HQ').openPopup();if(navigator.geolocation){navigator.geolocation.getCurrentPosition(p=>{let la=p.coords.latitude,lo=p.coords.longitude;map.setView([la,lo],14);L.marker([la,lo]).addTo(map).bindPopup('🧍 YOU ARE HERE').openPopup();log('🌍 Located you at '+la.toFixed(3)+','+lo.toFixed(3))})}}
function addMapGhost(){if(!map)return;let lat=5.6037+(Math.random()-0.5)*0.2,lng=-0.1870+(Math.random()-0.5)*0.2;let m=L.marker([lat,lng],{icon:L.divIcon({html:'👻',className:'',iconSize:[25,25]})}).addTo(map).bindPopup('👻 Ghost #'+ghosts+' EMF '+(Math.random()*4+6).toFixed(1)+' mG');markers.push(m)}
function speakGhost(){let w=document.getElementById('evp').textContent;if(w!=='---')speak(w);else{let r=words[Math.floor(Math.random()*words.length)];document.getElementById('evp').textContent=r;speak(r);setTimeout(()=>document.getElementById('evp').textContent='---',2000)}}
function shareScore(){let t=`I caught ${ghosts} ghosts on GHOSTBOX DEFENDER ULTRA! 👻 Rank: ${document.getElementById('rank').textContent} - Can you beat me? https://ghostbox-defender.onrender.com`;if(navigator.share){navigator.share({title:'Ghostbox Ultra',text:t})}else{navigator.clipboard.writeText(t);alert('Score copied! Paste to WhatsApp/TikTok 🔥')}}
initMap();log('ULTRA System Online - Accra Ghost Network ready...');document.addEventListener('keydown',e=>{if(e.key.toLowerCase()=='s')scan()})
</script>
</body>
</html>
    """
if __name__=="__main__":
    app.run()
