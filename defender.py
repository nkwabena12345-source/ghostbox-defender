from flask import Flask, request, jsonify
import re
app = Flask(__name__)

# Fake users DB - for demo only
USERS = [{"id":1,"name":"Kwame - Defender"}]

def is_attack(q):
    patterns = [r"' OR '1", r"' OR 1=1", r"UNION SELECT", r"<script", r"../", r"DROP TABLE"]
    for p in patterns:
        if re.search(p, q, re.I):
            return True, p
    return False, None

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GHOSTBOX SHIELD V5</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Share Tech Mono',monospace}
body{background:#000;color:#00ff88;padding:10px}
header{text-align:center;border:2px solid #00ff88;padding:10px;border-radius:12px;margin-bottom:10px}
.card{background:#000a;border:2px solid #00ff88;border-radius:12px;padding:12px;margin:10px 0}
#radar{width:300px;height:300px;margin:10px auto;background:radial-gradient(#001a0a,#000);border-radius:50%;border:2px solid #00ff88;position:relative;overflow:hidden}
.sweep{position:absolute;top:50%;left:50%;width:50%;height:2px;background:#00ff88;transform-origin:left;animation:sweep 3s linear infinite}
@keyframes sweep{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.dot{position:absolute;width:10px;height:10px;border-radius:50%;animation:blink 0.5s infinite alternate}
@keyframes blink{from{transform:scale(1)}to{transform:scale(1.5)}}
input{width:100%;padding:12px;background:#111;color:#00ff88;border:2px solid #00ff88;border-radius:8px;margin:6px 0}
.btn{padding:12px;background:#00ff88;color:#000;border:none;border-radius:8px;font-weight:bold;width:100%;cursor:pointer}
.log{height:180px;overflow:auto;background:#000;border:1px solid #00ff88;border-radius:8px;padding:8px;font-size:0.8em}
.shield-ok{color:#00ff88} .shield-bad{color:#ff0040;text-shadow:0 0 10px #ff0040}
</style>
</head>
<body>
<header><h1>👻 GHOSTBOX SHIELD V5 🛡️</h1><small>GH ULTRA DEFENDER • ACCRA</small><div>SHIELD: <span id="shield">100%</span> | BLOCKED: <span id="blocked">0</span> | GHOSTS: <span id="ghosts">0</span></div></header>

<div style="max-width:900px;margin:auto;display:grid;grid-template-columns:1fr 1fr;gap:10px">
<div class="card">
<h3>📡 THREAT RADAR</h3>
<div id="radar"><div class="sweep"></div></div>
<input id="attackInput" placeholder="Try: ' OR '1  or  <script>alert(1)</script>">
<button class="btn" onclick="testAttack()">🛡️ TEST SHIELD</button>
<button class="btn" style="background:#111;color:#00ff88;border:2px solid #00ff88;margin-top:6px" onclick="safeSearch()">🔍 SAFE SEARCH (Param Query)</button>
</div>
<div class="card">
<h3>📜 SECURITY LOG</h3>
<div id="log" class="log"></div>
<h3 style="margin-top:10px">💻 How Defender Works</h3>
<pre style="font-size:0.7em;background:#111;padding:8px;border-radius:8px;white-space:pre-wrap">
// BAD (Vulnerable):
query = "SELECT * FROM users WHERE name = '" + userInput + "'"

// GOOD (Defender):
cursor.execute("SELECT * FROM users WHERE name = ?", (userInput,))
</pre>
</div>
</div>

<script>
let blocked=parseInt(localStorage.getItem('gb_blocked')||0), ghosts=parseInt(localStorage.getItem('gb_ghosts')||0), shield=100;
document.getElementById('blocked').textContent=blocked; document.getElementById('ghosts').textContent=ghosts;
function log(m,c='shield-ok'){let l=document.getElementById('log');let d=document.createElement('div');d.className=c;d.textContent='['+new Date().toLocaleTimeString()+'] '+m;l.prepend(d)}
async function testAttack(){
 let q=document.getElementById('attackInput').value;
 if(!q) return log('⚠️ Enter payload to test','shield-bad');
 let res=await fetch('/scan?q='+encodeURIComponent(q));
 let data=await res.json();
 if(data.blocked){
   blocked++; localStorage.setItem('gb_blocked',blocked);
   document.getElementById('blocked').textContent=blocked;
   shield=Math.max(0,shield-5); document.getElementById('shield').textContent=shield+'%';
   log('🛡️ BLOCKED: '+q+' | Pattern: '+data.pattern,'shield-bad');
   showDot('#ff0040');
   if(navigator.vibrate) navigator.vibrate([100,50,100]);
 } else {
   ghosts++; localStorage.setItem('gb_ghosts',ghosts);
   document.getElementById('ghosts').textContent=ghosts;
   log('✅ SAFE: '+q+' | Result: '+data.result,'shield-ok');
   showDot('#00ff88');
 }
}
async function safeSearch(){
 let q=document.getElementById('attackInput').value||'Kwame';
 let res=await fetch('/safe?q='+encodeURIComponent(q));
 let data=await res.json();
 log('🔒 SAFE QUERY EXECUTED: param='+q+' => '+JSON.stringify(data),'shield-ok');
 showDot('#00ff88');
}
function showDot(color){
 let r=document.getElementById('radar');
 let d=document.createElement('div');d.className='dot';
 d.style.background=color; d.style.boxShadow='0 0 10px '+color;
 d.style.left=(20+Math.random()*60)+'%'; d.style.top=(20+Math.random()*60)+'%';
 r.appendChild(d); setTimeout(()=>d.remove(),3000);
}
log('🟢 GH ULTRA SHIELD V5 ONLINE - Ready to defend Accra');
</script>
</body>
</html>
    """

@app.route("/scan")
def scan():
    q=request.args.get("q","")
    blocked, pattern = is_attack(q)
    if blocked:
        return jsonify({"blocked":True,"pattern":pattern})
    return jsonify({"blocked":False,"result":"No threat found - ghost captured!"})

@app.route("/safe")
def safe():
    # This is the DEFENDER way - parameterized, always safe
    q=request.args.get("q","")
    # Simulating param query - never executes q as code
    return jsonify({"mode":"PARAMETERIZED QUERY","input_treated_as_data":q,"users":USERS})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
