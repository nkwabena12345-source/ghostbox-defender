from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GHOSTBOX DEFENDER PRO</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Share Tech Mono',monospace}
body{background:#020602;color:#00ff88;min-height:100vh;overflow-x:hidden}
#bg{position:fixed;inset:0;background:radial-gradient(circle at 50% 50%, #003d1f11 0%, #000 70%);z-index:-1}
header{padding:15px;text-align:center;border-bottom:2px solid #00ff8844;box-shadow:0 0 20px #00ff8833;background:#000a}
h1{font-size:2.2em;text-shadow:0 0 15px #00ff88, 0 0 30px #00ff88;letter-spacing:3px}
.container{max-width:900px;margin:0 auto;padding:15px;display:grid;gap:15px}
.card{background:#000c;border:2px solid #00ff88; border-radius:15px; padding:15px; box-shadow:0 0 20px #00ff8822, inset 0 0 20px #00ff8808}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:15px}
@media(max-width:600px){.grid2{grid-template-columns:1fr} h1{font-size:1.5em}}
#radarWrap{position:relative;aspect-ratio:1;max-width:400px;margin:0 auto;width:100%;background:radial-gradient(#001a0a, #000);border-radius:50%;border:2px solid #00ff88;overflow:hidden;box-shadow:0 0 40px #00ff8844}
#radar{width:100%;height:100%;display:block}
#emf{height:20px;background:#111;border-radius:10px;overflow:hidden;border:1px solid #00ff88}
#emfFill{height:100%;width:10%;background:linear-gradient(90deg,#00ff88,#ffff00,#ff0000);transition:width 0.3s;box-shadow:0 0 10px #00ff88}
.btn{padding:14px;background:#00ff88;color:#000;border:none;border-radius:8px;font-weight:bold;font-size:1.1em;cursor:pointer;box-shadow:0 0 15px #00ff88;transition:0.2s;width:100%}
.btn:hover{transform:scale(1.03);box-shadow:0 0 25px #00ff88}
.btn.off{background:#111;color:#00ff88;border:2px solid #00ff88;box-shadow:none}
#log{height:160px;overflow-y:auto;background:#000a;padding:10px;border-radius:8px;font-size:0.85em;border:1px solid #00ff8822}
.logEntry{margin:3px 0;opacity:0.9;animation:fadeIn 0.3s}
@keyframes fadeIn{from{opacity:0;transform:translateX(-10px)}to{opacity:0.9;transform:translateX(0)}}
#ghostAlert{position:fixed;top:0;left:0;right:0;bottom:0;background:#ff0000aa;display:none;place-items:center;z-index:999;font-size:3em;color:#fff;animation:flash 0.2s infinite}
@keyframes flash{0%,100%{background:#ff0000cc}50%{background:#000}}
.evp{font-size:1.6em;text-align:center;min-height:40px;letter-spacing:2px;text-shadow:0 0 10px #00ff88}
.sweep{position:absolute;top:50%;left:50%;width:50%;height:2px;background:linear-gradient(90deg,transparent,#00ff88);transform-origin:left;animation:sweep 3s linear infinite}
@keyframes sweep{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div id="bg"></div>
<div id="ghostAlert">👻 GHOST DETECTED! 👻</div>
<header><h1>👻 GHOSTBOX DEFENDER <span style="font-size:0.6em;vertical-align:super;border:1px solid #00ff88;padding:2px 6px;border-radius:5px">PRO</span> 🛡️</h1></header>

<div class="container">
 <div class="grid2">
  <div class="card">
   <h3>📡 RADAR</h3>
   <div id="radarWrap"><canvas id="radar"></canvas><div class="sweep"></div></div>
   <div style="display:flex;gap:10px;margin-top:10px"><button class="btn" id="activateBtn" onclick="togglePower()">ACTIVATE DEFENDER</button><button class="btn off" onclick="scan()">SCAN [S]</button></div>
  </div>
  <div class="card">
   <h3>📟 EMF METER: <span id="emfVal">1.2</span> mG</h3>
   <div id="emf"><div id="emfFill"></div></div>
   <h3 style="margin-top:15px">🎙️ SPIRIT BOX</h3>
   <div class="evp" id="evp">---</div>
   <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px">
    <div class="card" style="padding:8px;text-align:center">SHIELD<br><span id="shield" style="font-size:1.8em">100%</span></div>
    <div class="card" style="padding:8px;text-align:center">GHOSTS<br><span id="count" style="font-size:1.8em">0</span></div>
   </div>
  </div>
 </div>
 <div class="card">
  <h3>📜 PARANORMAL LOG</h3>
  <div id="log"></div>
 </div>
</div>

<script>
let power=false,ghosts=0,shield=100,evpWords=["BEHIND YOU","HELP ME","LEAVE","COLD","DONT LOOK","HE IS HERE","RUN","WE SEE YOU","DEATH","MIRROR","BASEMENT","FOLLOW","LISTEN","IT HURTS","GET OUT","I AM HERE","TOUCH","NINE","OPEN","HIDE"];
let canvas=document.getElementById('radar'), ctx=canvas.getContext('2d'), dots=[];
function resize(){canvas.width=canvas.height=canvas.offsetWidth*2; ctx.scale(2,2)}; resize(); window.onresize=resize;
function addLog(t){let l=document.getElementById('log'); let d=document.createElement('div'); d.className='logEntry'; d.innerHTML=`[${new Date().toLocaleTimeString()}] ${t}`; l.prepend(d); if(l.children.length>30)l.lastChild.remove();}
function togglePower(){power=!power; let b=document.getElementById('activateBtn'); b.textContent=power?'DEFENDER ACTIVE ✓':'ACTIVATE DEFENDER'; b.className=power?'btn':'btn off'; addLog(power?'🟢 DEFENDER ACTIVATED - Shield online':'🔴 DEFENDER OFFLINE'); if(power)loop();}
function scan(){if(!power)return addLog('⚠️ Activate defender first!'); let e=(Math.random()*9+1).toFixed(1); document.getElementById('emfVal').innerText=e; document.getElementById('emfFill').style.width=e*10+'%'; if(e>7){ghostEvent()} else addLog(`🔍 Scan complete - EMF ${e} mG - No threats`); document.getElementById('evp').textContent=evpWords[Math.floor(Math.random()*evpWords.length)]; setTimeout(()=>document.getElementById('evp').textContent='---',3000);}
function ghostEvent(){ghosts++; document.getElementById('count').textContent=ghosts; shield=Math.max(0,shield-10); document.getElementById('shield').textContent=shield+'%'; addLog(`👻 GHOST DETECTED! EMF ${document.getElementById('emfVal').innerText} mG!`); let a=document.getElementById('ghostAlert'); a.style.display='grid'; setTimeout(()=>a.style.display='none',800); dots.push({x:Math.random()*180+10,y:Math.random()*180+10,life:100}); if(shield<=0){addLog('💀 SHIELD FAILED! Rebooting...'); shield=100;}}
function loop(){if(!power)return; ctx.clearRect(0,0,400,400); ctx.strokeStyle='#00ff8811'; for(let r=20;r<200;r+=40){ctx.beginPath();ctx.arc(100,100,r,0,Math.PI*2);ctx.stroke();} dots=dots.filter(d=>d.life>0); dots.forEach(d=>{ctx.fillStyle=`rgba(255,0,80,${d.life/100})`;ctx.shadowBlur=10;ctx.shadowColor='#ff0044';ctx.beginPath();ctx.arc(d.x,d.y,4,0,7);ctx.fill();d.life-=1;ctx.shadowBlur=0;}); if(Math.random()<0.03)document.getElementById('emfVal').innerText=(Math.random()*3+0.5).toFixed(1); requestAnimationFrame(loop);}
addLog('System Online - Waiting for activation...'); document.addEventListener('keydown',e=>{if(e.key.toLowerCase()=='s')scan();});
</script>
</body>
</html>
    """

if __name__ == "__main__":
    app.run()
