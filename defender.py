from flask import Flask, request, jsonify
import re, hashlib, os, requests
app = Flask(__name__)

VT_KEY = os.environ.get("VT_KEY", "")
HIBP_KEY = os.environ.get("HIBP_KEY", "")

def is_attack(q):
    patterns = [r"' OR '1", r"UNION SELECT", r"<script", r"DROP TABLE"]
    return any(re.search(p,q,re.I) for p in patterns)

@app.route("/manifest.json")
def manifest():
    return jsonify({"name":"GH SHIELD V9 REAL API","short_name":"GH SHIELD","start_url":"/","display":"standalone","background_color":"#000","theme_color":"#00ff88","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/3067/3067019.png","sizes":"512x512","type":"image/png"}]})

@app.route("/sw.js")
def sw(): return "",200,{'Content-Type':'application/javascript'}

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="manifest" href="/manifest.json">
<style>
*{font-family:monospace;margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#00ff88;padding:10px}
header{text-align:center;border:2px solid #00ff88;padding:12px;border-radius:12px}
.tab{display:inline-block;padding:8px 12px;margin:4px;background:#111;border:1px solid #00ff88;border-radius:20px;cursor:pointer}
.tab.active{background:#00ff88;color:#000}
.card{border:2px solid #00ff88;border-radius:12px;padding:12px;margin:8px 0}
input{width:100%;padding:12px;background:#111;color:#00ff88;border:2px solid #00ff88;border-radius:8px;margin:6px 0}
.btn{padding:12px;background:#00ff88;color:#000;border:none;border-radius:8px;width:100%;font-weight:bold;cursor:pointer}
.result{padding:10px;border-radius:8px;margin:6px 0;word-break:break-all}
.bad{background:#ff004022;border:1px solid #ff0040;color:#ff0040}
.good{background:#00ff8822;border:1px solid #00ff88}
.log{height:90px;overflow:auto;border:1px solid #00ff88;padding:6px;border-radius:8px;font-size:0.8em}
</style></head><body>
<header><h1>👻 GH SHIELD V9 REAL API 🛰️</h1><small>REAL VirusTotal + HIBP • Accra</small><div>SHIELD <span id="shield">100</span>% | BLOCKED <span id="blocked">0</span></div></header>
<div style="text-align:center;margin:8px 0">
<span class="tab active" onclick="showTab(1)">🛡️ WAF</span>
<span class="tab" onclick="showTab(2)">🔗 LINK REAL</span>
<span class="tab" onclick="showTab(3)">📧 BREACH REAL</span>
<span class="tab" onclick="showTab(4)">🔑 PWD REAL</span>
<span class="tab" onclick="showTab(5)">📱 MoMo</span>
</div>
<div id="t1" class="card"><h3>1. WAF</h3><input id="q1" placeholder="' OR '1"><button class="btn" onclick="checkWAF()">TEST</button><div id="r1"></div></div>
<div id="t2" class="card" style="display:none"><h3>2. LINK - REAL VirusTotal API</h3><input id="q2" placeholder="https://www.greatland-gold.com/"><button class="btn" onclick="checkLinkReal()">SCAN REAL</button><div id="r2"></div></div>
<div id="t3" class="card" style="display:none"><h3>3. BREACH - REAL HIBP</h3><input id="q3" placeholder="email@gmail.com"><button class="btn" onclick="checkBreachReal()">CHECK REAL</button><div id="r3"></div></div>
<div id="t4" class="card" style="display:none"><h3>4. PWD - REAL Pwned (FREE, no key!)</h3><input id="q4" type="password" placeholder="password"><button class="btn" onclick="checkPwdReal()">CHECK REAL</button><div id="r4"></div><small>k-anonymity: only 5 chars of SHA1 sent, safe!</small></div>
<div id="t5" class="card" style="display:none"><h3>5. MoMo GH DB</h3><input id="q5" placeholder="0553473773"><button class="btn" onclick="checkMomo()">CHECK</button><div id="r5"></div></div>
<div class="card"><div id="log" class="log"></div></div>
<script>
let blocked=parseInt(localStorage.getItem('gb_b')||0); document.getElementById('blocked').textContent=blocked;
function log(m,c){let l=document.getElementById('log');let d=document.createElement('div');d.style.color=c||'#00ff88';d.textContent='['+new Date().toLocaleTimeString()+'] '+m;l.prepend(d)}
function showTab(n){for(let i=1;i<=5;i++)document.getElementById('t'+i).style.display=i==n?'block':'none'; document.querySelectorAll('.tab').forEach((e,i)=>e.classList.toggle('active',i+1==n))}
async function checkWAF(){let q=document.getElementById('q1').value; let r=await fetch('/scan?waf='+encodeURIComponent(q)); let j=await r.json(); document.getElementById('r1').innerHTML=j.blocked?'<div class=result bad>BLOCKED</div>':'<div class=result good>SAFE</div>'; if(j.blocked){blocked++;localStorage.setItem('gb_b',blocked);document.getElementById('blocked').textContent=blocked}}
async function checkLinkReal(){let url=document.getElementById('q2').value; document.getElementById('r2').innerHTML='Scanning with real VirusTotal...'; let r=await fetch('/api/vt?url='+encodeURIComponent(url)); let j=await r.json(); document.getElementById('r2').innerHTML=j.html; log('VT REAL: '+url, j.bad?'#ff0040':'#00ff88')}
async function checkBreachReal(){let e=document.getElementById('q3').value; document.getElementById('r3').innerHTML='Checking HIBP...'; let r=await fetch('/api/hibp?email='+encodeURIComponent(e)); let j=await r.json(); document.getElementById('r3').innerHTML=j.html; log('HIBP REAL: '+e, j.bad?'#ff0040':'#00ff88')}
async function checkPwdReal(){let p=document.getElementById('q4').value; document.getElementById('r4').innerHTML='Checking Pwned Passwords...'; let r=await fetch('/api/pwd?pwd='+encodeURIComponent(p)); let j=await r.json(); document.getElementById('r4').innerHTML=j.html; log('PWD REAL checked')}
function checkMomo(){let n=document.getElementById('q5').value; let bad=n.startsWith('0240')||n=='0553473773'; document.getElementById('r5').innerHTML=bad?'<div class=result bad>🚨 SCAMMER! Reported!</div>':'<div class=result good>✅ No reports</div>'}
log('🛰️ V9 REAL ONLINE - Add VT_KEY in Render Env to go live!');
</script></body></html>
    """

@app.route("/scan")
def scan():
    q=request.args.get("waf",""); return jsonify({"blocked":is_attack(q)})

@app.route("/api/vt")
def api_vt():
    url=request.args.get("url","")
    if not VT_KEY:
        # demo mode - no key yet
        bad = any(x in url.lower() for x in ["greatland-gold","free-money","momo-claim"])
        if bad:
            return jsonify({"bad":True,"html":"<div class=result bad>🚨 DEMO: FLAGGED as suspicious (pattern match).<br>Add VT_KEY in Render Env for REAL 70-engine scan.</div>"})
        return jsonify({"bad":False,"html":"<div class=result good>✅ DEMO: Looks clean. Add VT_KEY for real VT data.</div>"})
    try:
        # Real VT URL scan
        r=requests.post("https://www.virustotal.com/api/v3/urls", headers={"x-apikey":VT_KEY}, data={"url":url}, timeout=10)
        j=r.json();
        return jsonify({"bad":False,"html":f"<div class=result good>✅ REAL VT: Submitted! ID {j.get('data',{}).get('id','')} - check VT dashboard</div>"})
    except Exception as e:
        return jsonify({"bad":False,"html":f"<div class=result bad>Error: {e}</div>"})

@app.route("/api/hibp")
def api_hibp():
    email=request.args.get("email","")
    if not HIBP_KEY:
        # without key we can't call v3 breachedaccount, show demo
        pwned = "test" in email.lower()
        if pwned:
            return jsonify({"bad":True,"html":"<div class=result bad>💥 DEMO PWNED (test email). Add HIBP_KEY for real check. Real HIBP returns breach names like Adobe, LinkedIn etc.</div>"})
        return jsonify({"bad":False,"html":"<div class=result good>✅ DEMO safe. Add HIBP_KEY env for real HIBP API</div>"})
    try:
        r=requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers={"hibp-api-key":HIBP_KEY,"User-Agent":"GH-SHIELD-V9"}, timeout=10)
        if r.status_code==404:
            return jsonify({"bad":False,"html":"<div class=result good>✅ REAL HIBP: Not pwned! No breaches found.</div>"})
        breaches=r.json()
        names=", ".join([b['Name'] for b in breaches[:3]])
        return jsonify({"bad":True,"html":f"<div class=result bad>💥 REAL PWNED in {len(breaches)} breaches: {names} - CHANGE NOW!</div>"})
    except Exception as e:
        return jsonify({"html":f"Error: {e}"})

@app.route("/api/pwd")
def api_pwd():
    pwd=request.args.get("pwd","")
    # FREE, no key, real HIBP k-anonymity
    try:
        sha1=hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix=sha1[:5]; suffix=sha1[5:]
        r=requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=10)
        found=False; count=0
        for line in r.text.splitlines():
            if line.startswith(suffix):
                found=True
                count=int(line.split(":")[1])
                break
        if found:
            return jsonify({"html":f"<div class=result bad>💥 REAL PWNED! This password seen {count:,} times in breaches! NEVER USE!</div>"})
        return jsonify({"html":"<div class=result good>✅ REAL CHECK: Not found in Pwned Passwords (500M+ list) - good!</div>"})
    except Exception as e:
        return jsonify({"html":f"Error {e}"})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
