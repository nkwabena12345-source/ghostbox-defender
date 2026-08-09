from flask import Flask, request, jsonify
import re
app = Flask(__name__)

def is_attack(q):
    patterns = [r"' OR '1", r"UNION SELECT", r"<script", r"\.\./", r"DROP TABLE"]
    for p in patterns:
        if re.search(p, q, re.I):
            return True, p
    return False, None

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "name":"GHOSTBOX SHIELD V5",
        "short_name":"GHOSTBOX",
        "start_url":"/",
        "display":"standalone",
        "background_color":"#000000",
        "theme_color":"#00ff88",
        "icons":[
            {"src":"https://cdn-icons-png.flaticon.com/512/3067/3067019.png","sizes":"512x512","type":"image/png"}
        ]
    })

@app.route("/sw.js")
def sw():
    return """
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('fetch',e=>e.respondWith(fetch(e.request).catch(()=>caches.match(e.request))));
""", 200, {'Content-Type':'application/javascript'}

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#00ff88">
<title>GHOSTBOX SHIELD V5 - PWA</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Share Tech Mono',monospace}
body{background:#000;color:#00ff88;padding:10px}
header{text-align:center;border:2px solid #00ff88;padding:10px;border-radius:12px}
.card{background:#000a;border:2px solid #00ff88;border-radius:12px;padding:12px;margin:10px 0}
#radar{width:280px;height:280px;margin:auto;background:radial-gradient(#001a0a,#000);border-radius:50%;border:2px solid #00ff88;position:relative}
.sweep{position:absolute;top:50%;left:50%;width:50%;height:2px;background:#00ff88;transform-origin:left;animation:sweep 3s linear infinite}
@keyframes sweep{from{transform:rotate(0)}to{transform:rotate(360deg)}}
input{width:100%;padding:12px;background:#111;color:#00ff88;border:2px solid #00ff88;border-radius:8px;margin:6px 0}
.btn{padding:12px;background:#00ff88;color:#000;border:none;border-radius:8px;font-weight:bold;width:100%;cursor:pointer;margin:4px 0}
.log{height:150px;overflow:auto;background:#000;border:1px solid #00ff88;border-radius:8px;padding:8px;font-size:0.8em}
.install{background:#00ff88;color:#000;padding:10px;border-radius:8px;text-align:center;display:none;margin:10px 0}
</style>
</head>
<body>
<div id="installBox" class="install">📲 <b>INSTALL APP?</b> Tap to add GHOSTBOX to home screen <button onclick="installPWA()" style="padding:6px 12px;background:#000;color:#00ff88;border:none;border-radius:6px;margin-left:8px">INSTALL</button></div>
<header><h1>👻 SHIELD V5 PWA 🛡️</h1><small>GH ULTRA • Installable App • Accra</small><div>SHIELD <span id="shield">100%</span>% | BLOCKED <span id="blocked">0</span></div></header>
<div style="max-width:700px;margin:auto">
<div class="card"><h3>📡 RADAR</h3><div id="radar"><div class="sweep"></div></div>
<input id="q" placeholder="Try: ' OR '1"><button class="btn" onclick="test()">🛡️ TEST SHIELD</button></div>
<div class="card"><h3>📜 LOG</h3><div id="log" class="log"></div></div>
<div class="card" style="text-align:center">📱 <b>How to Install:</b><br>Android: ⋮ menu > Add to Home screen<br>iPhone: Share button > Add to Home Screen<br>Then opens like WhatsApp, no browser bar!</div>
</div>
<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}
let blocked=parseInt(localStorage.getItem('gb_blocked')||0),deferredPrompt;
document.getElementById('blocked').textContent=blocked;
function log(m,c='#00ff88'){let l=document.getElementById('log');let d=document.createElement('div');d.style.color=c;d.textContent='['+new Date().toLocaleTimeString()+'] '+m;l.prepend(d)}
async function test(){
 let q=document.getElementById('q').value; if(!q) return;
 let r=await fetch('/scan?q='+encodeURIComponent(q)); let j=await r.json();
 if(j.blocked){blocked++; localStorage.setItem('gb_blocked',blocked); document.getElementById('blocked').textContent=blocked; log('🛡️ BLOCKED: '+q,'#ff0040')} else {log('✅ SAFE: '+q)}
}
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredPrompt=e;document.getElementById('installBox').style.display='block'});
function installPWA(){if(deferredPrompt){deferredPrompt.prompt();deferredPrompt.userChoice.then(c=>{if(c.outcome==='accepted')log('📲 APP INSTALLED!')});} else {log('📲 Use browser menu > Add to Home Screen')}}
log('🟢 PWA ONLINE - Ready to install');
</script>
</body>
</html>
    """

@app.route("/scan")
def scan():
    q=request.args.get("q",""); b,p=is_attack(q)
    return jsonify({"blocked":b,"pattern":p})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
