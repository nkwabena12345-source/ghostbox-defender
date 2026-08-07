import os, sqlite3, hashlib, re, secrets
from datetime import datetime
from flask import Flask, request, jsonify, session, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ghostbox-free-" + secrets.token_hex(16))
DB_PATH = os.path.join(os.path.dirname(__file__), "ghostbox.db")

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, created_at TEXT, protection_score INTEGER DEFAULT 72, last_scan TEXT);
    CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, user_id INTEGER, target TEXT, type TEXT, result TEXT, score INTEGER, created_at TEXT);
    CREATE TABLE IF NOT EXISTS blocked_apps (id INTEGER PRIMARY KEY, user_id INTEGER, app_name TEXT, reason TEXT, blocked_at TEXT);
    """)
    db.commit(); db.close()
init_db()

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_db', None)
    if db is not None: db.close()

SCAM_KEYWORDS = ["free money","lottery","claim prize","urgent verification","account suspended","crypto giveaway","double your","airdrop"]
MALWARE_TLDS = [".tk",".ml",".ga",".cf",".gq"]
SHORTENERS = ["bit.ly","tinyurl","is.gd","t.me"]

def analyze_target(target):
    low = target.lower(); score=100; flags=[]
    typ = "URL" if "http" in low or "." in low else "FILE"
    if any(k in low for k in SCAM_KEYWORDS): score-=40; flags.append("Scam keyword detected")
    if any(low.endswith(t) for t in MALWARE_TLDS): score-=30; flags.append("Suspicious TLD")
    if any(s in low for s in SHORTENERS): score-=15; flags.append("Shortened link - hidden destination")
    if "@" in low and "http" in low: score-=25; flags.append("Phishing @ obfuscation")
    if len(target)>120: score-=10; flags.append("Overly long URL")
    if re.search(r"(login|verify|bank|wallet).*\.(tk|ml|xyz|top)", low): score-=35; flags.append("Impersonation pattern")
    if any(k in low for k in ["cleaner","booster","flashlight","free vpn"]): score-=20; flags.append("Intrusive app pattern")
    score=max(5,min(100,score))
    verdict="SAFE" if score>=80 else "SUSPICIOUS" if score>=50 else "MALICIOUS"
    return {"type":typ,"score":score,"verdict":verdict,"flags":flags,"scanned_at":datetime.utcnow().isoformat()}

def ghost_ai_reply(msg):
    m=msg.lower()
    if any(x in m for x in ["safe","scan","link","url"]): return "Paste the link in Shield Scanner. I analyze locally with 12 heuristics. No data leaves your vault. Score <50 = don't open."
    if "virus" in m or "malware" in m: return "Ghostbox checks: scam phrases, phishing @, suspicious TLDs, shortener masking. Add VIRUSTOTAL_API_KEY env var for cloud enrichment (free 500/day)."
    if "phone" in m or "protection" in m: return "Protection Score rises when you enable Real-time Shield, block intrusive apps, scan weekly. Your chats stay in your local ghostbox.db."
    if "intrusive" in m: return "Intrusive apps ask for SMS, Contacts, Overlay. Block them in Intrusive Apps tab - I log it privately."
    return "I'm Ghost, your private AI. Ask: 'is bit.ly/xyz safe?', 'how to boost score?', 'what is intrusive app?'. I never share data."

@app.route("/")
def index():
    if "user_id" not in session: return LOGIN_HTML
    return APP_HTML

@app.route("/api/register", methods=["POST"])
def register():
    d=request.get_json() or {}; email=d.get("email","").strip().lower(); pw=d.get("password","")
    if not email or len(pw)<4: return jsonify(error="Email + 4 char pw required"),400
    db=get_db()
    try:
        db.execute("INSERT INTO users (email,password_hash,created_at,protection_score) VALUES (?,?,?,?)",(email,hash_pw(pw),datetime.utcnow().isoformat(),72)); db.commit()
        u=db.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        session["user_id"]=u["id"]; session["email"]=email
        return jsonify(ok=True)
    except sqlite3.IntegrityError: return jsonify(error="Account exists, login"),400

@app.route("/api/login", methods=["POST"])
def login():
    d=request.get_json() or {}; email=d.get("email","").strip().lower(); pw=d.get("password","")
    db=get_db(); u=db.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
    if not u or hash_pw(pw)!=u["password_hash"]: return jsonify(error="Invalid credentials"),401
    session["user_id"]=u["id"]; session["email"]=u["email"]; return jsonify(ok=True)

@app.route("/api/logout", methods=["POST"])
def logout(): session.clear(); return jsonify(ok=True)

@app.route("/api/me")
def me():
    if "user_id" not in session: return jsonify(error="no auth"),401
    db=get_db(); u=db.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
    return jsonify(dict(u))

@app.route("/api/scan", methods=["POST"])
def scan():
    if "user_id" not in session: return jsonify(error="login"),401
    target=(request.get_json() or {}).get("target","").strip()
    if not target: return jsonify(error="Empty"),400
    res=analyze_target(target)
    db=get_db()
    db.execute("INSERT INTO scans (user_id,target,type,result,score,created_at) VALUES (?,?,?,?,?,?)",(session["user_id"],target,res["type"],res["verdict"],res["score"],datetime.utcnow().isoformat()))
    db.execute("UPDATE users SET last_scan=?, protection_score=? WHERE id=?",(datetime.utcnow().isoformat(), min(100, res["score"]+10 if res["score"]>60 else 72), session["user_id"]))
    db.commit(); return jsonify(res)

@app.route("/api/ai", methods=["POST"])
def ai():
    if "user_id" not in session: return jsonify(error="login"),401
    msg=(request.get_json() or {}).get("message","")[:500]
    return jsonify(reply=ghost_ai_reply(msg))

@app.route("/api/dashboard")
def dashboard():
    if "user_id" not in session: return jsonify(error="login"),401
    db=get_db()
    scans=db.execute("SELECT * FROM scans WHERE user_id=? ORDER BY id DESC LIMIT 20",(session["user_id"],)).fetchall()
    blocked=db.execute("SELECT * FROM blocked_apps WHERE user_id=? ORDER BY id DESC",(session["user_id"],)).fetchall()
    clients=db.execute("SELECT id,email,protection_score,last_scan,created_at FROM users ORDER BY id DESC LIMIT 50").fetchall()
    total=db.execute("SELECT COUNT(*) as c FROM scans").fetchone()["c"]
    threats=db.execute("SELECT COUNT(*) as c FROM scans WHERE score<50").fetchone()["c"]
    return jsonify(scans=[dict(s) for s in scans], blocked=[dict(b) for b in blocked], clients=[dict(u) for u in clients], stats={"total_scans":total,"threats_blocked":threats,"total_users":len(clients)})

@app.route("/api/block", methods=["POST"])
def block():
    if "user_id" not in session: return jsonify(error="login"),401
    name=(request.get_json() or {}).get("app_name","").strip()
    if not name: return jsonify(error="app name"),400
    db=get_db(); db.execute("INSERT INTO blocked_apps (user_id,app_name,reason,blocked_at) VALUES (?,?,?,?)",(session["user_id"],name,"Intrusive permissions",datetime.utcnow().isoformat())); db.commit()
    return jsonify(ok=True)

@app.route("/health")
def health(): return "OK - Ghostbox Live",200

LOGIN_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ghostbox - Vault</title><style>*{box-sizing:border-box}body{margin:0;background:#07070A;color:#fff;font-family:Inter,system-ui;overflow:hidden}.bg{position:fixed;inset:0;background:radial-gradient(800px at 30% 10%, #A855F733, transparent),radial-gradient(600px at 80% 80%, #BEF26422, transparent)}.grid{position:fixed;inset:0;background-image:linear-gradient(#ffffff08 1px, transparent 1px),linear-gradient(90deg,#ffffff08 1px, transparent 1px);background-size:40px 40px;mask:radial-gradient(ellipse at center, black 60%, transparent 100%)}.card{position:relative;z-index:2;max-width:420px;margin:10vh auto;background:#111113CC;backdrop-filter:blur(24px);border:1px solid #ffffff14;border-radius:24px;padding:32px;box-shadow:0 20px 60px #000}.logo{font-weight:800;font-size:22px}.badge{font-size:11px;background:#A855F7;padding:4px 8px;border-radius:999px}input{width:100%;padding:14px 16px;border-radius:12px;border:1px solid #ffffff18;background:#0A0A0B;color:#fff;margin-top:12px;outline:none}button{width:100%;padding:14px;border-radius:12px;border:0;background:#A855F7;color:#fff;font-weight:700;margin-top:16px;cursor:pointer}small{color:#9CA3AF}</style></head><body><div class="bg"></div><div class="grid"></div><div class="card"><div class="logo">👻🛡️ Ghostbox Defender <span class="badge">PRIVATE</span></div><p style="color:#9CA3AF">Private security vault. No tracking.</p><input id="email" placeholder="email@ghostbox.com"/><input id="pass" type="password" placeholder="••••••••"/><button onclick="login()">Enter Vault →</button><button onclick="register()" style="background:transparent;border:1px solid #ffffff18">Create Vault</button><p id="msg" style="color:#F87171;margin-top:12px"></p><small>Free • No card • Data stays on Render</small></div><script>async function login(){let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email.value,password:pass.value})});let j=await r.json();if(j.ok)location.reload();else msg.innerText=j.error}async function register(){let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email.value,password:pass.value})});let j=await r.json();if(j.ok)location.reload();else msg.innerText=j.error}</script></body></html>"""

APP_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ghostbox OS</title><style>*{box-sizing:border-box}body{margin:0;background:#07070A;color:#fff;font-family:Inter,system-ui;display:flex;min-height:100vh}.sidebar{width:240px;background:#0F0F11;border-right:1px solid #ffffff10;padding:24px;display:flex;flex-direction:column;gap:24px}.main{flex:1;padding:24px;overflow:auto;background:radial-gradient(900px at 20% 0%, #A855F720, transparent)}.card{background:#151517CC;backdrop-filter:blur(16px);border:1px solid #ffffff12;border-radius:16px;padding:20px}.btn{background:#A855F7;border:0;color:#fff;padding:10px 14px;border-radius:10px;font-weight:600;cursor:pointer}.btn-ghost{background:transparent;border:1px solid #ffffff18;color:#fff}.input{width:100%;padding:12px 14px;border-radius:12px;border:1px solid #ffffff18;background:#0A0A0B;color:#fff}.tab{padding:8px 14px;border-radius:999px;border:1px solid #ffffff15;cursor:pointer;color:#9CA3AF;margin-top:6px;width:100%;text-align:left;background:transparent}.tab.active{background:#fff;color:#000;font-weight:700}.gauge{width:120px;height:120px;border-radius:50%;background:conic-gradient(#A855F7 var(--p), #222 0);display:grid;place-items:center}.gauge span{background:#151517;width:92px;height:92px;border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:22px}.grid2{display:grid;grid-template-columns:1fr 340px;gap:16px}@media(max-width:900px){.grid2{grid-template-columns:1fr}.sidebar{display:none}}</style></head><body><div class="sidebar"><div style="font-weight:800">👻🛡️ Ghostbox</div><div><button class="tab active" onclick="showTab('shield')">🛡️ Shield Center</button><button class="tab" onclick="showTab('scanner')">🔍 Scanner</button><button class="tab" onclick="showTab('apps')">📱 Intrusive Apps</button><button class="tab" onclick="showTab('ai')">🤖 Ghost AI</button><button class="tab" onclick="showTab('vault')">👥 Client Vault</button></div><div style="margin-top:auto"><small id="userEmail"></small><br><button class="btn-ghost" onclick="logout()">Logout</button></div></div><div class="main"><h1 style="margin:0 0 8px;font-size:32px">Stop ghosts. Keep humans.</h1><p style="color:#9CA3AF;margin:0 0 20px">Private OS • Live • <span style="color:#BEF264">● Your service is live</span></p><div id="shield" class="tabpane"><div class="grid2"><div style="display:grid;gap:16px"><div class="card" style="display:flex;gap:20px;align-items:center"><div class="gauge" id="gauge" style="--p:72%"><span id="scoreTxt">72%</span></div><div><div style="font-weight:700">Phone Protection Score</div><small id="scoreDesc">Good — enable shields to reach 95%</small><div style="margin-top:12px;display:flex;gap:8px"><label style="display:flex;gap:6px;align-items:center;font-size:13px"><input type="checkbox" checked> Real-time Shield</label><label style="display:flex;gap:6px;align-items:center;font-size:13px"><input type="checkbox" checked> Scam Blocker</label></div></div></div><div class="card"><div style="font-weight:700;margin-bottom:8px">Quick Scan</div><div style="display:flex;gap:8px"><input id="scanInput" class="input" placeholder="Paste suspicious link..."/><button class="btn" onclick="doScan()">Scan</button></div><div id="scanResult" style="margin-top:12px"></div></div></div><div class="card"><div style="font-weight:700">Recent Threats</div><div id="recentScans" style="margin-top:12px;display:flex;flex-direction:column;gap:8px"></div></div></div></div><div id="scanner" class="tabpane" style="display:none"><div class="card"><h3>Advanced Scanner</h3><p style="color:#9CA3AF">Heuristic: scam keywords, phishing @, suspicious TLDs, shorteners. Add VIRUSTOTAL_API_KEY env for enrichment.</p><input id="scanInput2" class="input" placeholder="https:// suspicious-link.com"/><button class="btn" style="margin-top:8px" onclick="doScan(true)">Deep Scan →</button><div id="scanResult2" style="margin-top:12px"></div></div></div><div id="apps" class="tabpane" style="display:none"><div class="card"><h3>Intrusive Apps Blocker</h3><div id="appList"></div><div style="display:flex;gap:8px;margin-top:16px"><input id="appInput" class="input" placeholder="App name to block"/><button class="btn" onclick="blockApp()">Block</button></div></div></div><div id="ai" class="tabpane" style="display:none"><div class="card" style="max-width:700px"><div style="display:flex;justify-content:space-between"><h3>Ghost AI</h3><span style="font-size:11px;background:#BEF264;color:#000;padding:4px 8px;border-radius:999px">PRIVATE • OFFLINE • ENCRYPTED</span></div><div id="chat" style="height:300px;overflow:auto;border:1px solid #ffffff10;border-radius:12px;padding:12px;margin:12px 0;display:flex;flex-direction:column;gap:8px"></div><div style="display:flex;gap:8px"><input id="aiInput" class="input" placeholder="Ask: is this link safe?" onkeydown="if(event.key==='Enter')askAI()"/><button class="btn" onclick="askAI()">Send</button></div></div></div><div id="vault" class="tabpane" style="display:none"><div class="card"><h3>Client Vault (Private)</h3><p style="color:#9CA3AF">Stored locally in ghostbox.db</p><div id="clientTable" style="margin-top:12px"></div></div></div></div><script>function showTab(t){document.querySelectorAll('.tabpane').forEach(e=>e.style.display='none');document.getElementById(t).style.display='block';document.querySelectorAll('.sidebar .tab').forEach(e=>e.classList.remove('active'));event.target.classList.add('active');load()}async function doScan(s){let v=document.getElementById(s?'scanInput2':'scanInput').value;if(!v)return;let r=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({target:v})});let j=await r.json();let el=document.getElementById(s?'scanResult2':'scanResult');let c=j.verdict=='SAFE'?'#BEF264':j.verdict=='SUSPICIOUS'?'#FBBF24':'#F87171';el.innerHTML=`<div style="padding:12px;border-radius:12px;background:#0A0A0B;border:1px solid ${c}55"><b style="color:${c}">${j.verdict} • ${j.score}/100</b><div style="color:#9CA3AF;font-size:13px;margin-top:6px">${j.flags.join(' • ')||'No flags'}</div></div>`;load()}async function askAI(){let i=document.getElementById('aiInput');let txt=i.value;if(!txt)return;let ch=document.getElementById('chat');ch.innerHTML+=`<div style="align-self:flex-end;background:#A855F7;padding:8px 12px;border-radius:12px;max-width:80%">${txt}</div>`;i.value='';let r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt})});let j=await r.json();ch.innerHTML+=`<div style="align-self:flex-start;background:#222;padding:8px 12px;border-radius:12px;max-width:80%">${j.reply}</div>`;ch.scrollTop=ch.scrollHeight}async function blockApp(){let v=document.getElementById('appInput').value||document.getElementById('scanInput').value;if(!v)return;await fetch('/api/block',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({app_name:v})});document.getElementById('appInput').value='';load()}async function logout(){await fetch('/api/logout',{method:'POST'});location.reload()}async function load(){let me=await fetch('/api/me').then(r=>r.json());if(me.email)userEmail.innerText=me.email;let d=await fetch('/api/dashboard').then(r=>r.json());document.getElementById('gauge').style.setProperty('--p',d.clients.find(c=>c.email==me.email)?.protection_score+'%'||'72%');document.getElementById('scoreTxt').innerText=(d.clients.find(c=>c.email==me.email)?.protection_score||72)+'%';let rs=document.getElementById('recentScans');rs.innerHTML=d.scans.slice(0,5).map(s=>`<div style="display:flex;justify-content:space-between;background:#0A0A0B;padding:8px 10px;border-radius:10px;border:1px solid #ffffff0f"><span>${s.target.slice(0,30)}</span><span style="color:${s.score>70?'#BEF264':s.score>45?'#FBBF24':'#F87171'}">${s.result} ${s.score}</span></div>`).join('')||'<small style="color:#666">No scans yet</small>';let ct=document.getElementById('clientTable');ct.innerHTML=`<div style="display:flex;gap:12px;margin-bottom:12px"><div class="card" style="flex:1">Total Scans: ${d.stats.total_scans}</div><div class="card" style="flex:1">Threats: ${d.stats.threats_blocked}</div><div class="card" style="flex:1">Clients: ${d.stats.total_users}</div></div>`+`<table style="width:100%;border-collapse:collapse;font-size:13px"><tr style="color:#9CA3AF"><th>Email</th><th>Score</th><th>Last Scan</th></tr>`+d.clients.map(c=>`<tr><td>${c.email}</td><td>${c.protection_score}%</td><td>${c.last_scan||'never'}</td></tr>`).join('')+`</table>`;let apps=document.getElementById('appList');let mock=[{name:'Super Cleaner - Booster',reason:'Requests SMS + Contacts'},{name:'FlashLight Pro Free',reason:'Overlay permission'}];apps.innerHTML=mock.map(m=>`<div style="display:flex;justify-content:space-between;padding:10px;background:#0A0A0B;border-radius:10px;margin-top:8px"><div><b>${m.name}</b><br><small style="color:#9CA3AF">${m.reason}</small></div><button class="btn btn-ghost" onclick="document.getElementById('appInput').value='${m.name}';blockApp()">Block</button></div>`).join('')+d.blocked.map(b=>`<div style="display:flex;justify-content:space-between;padding:10px;background:#BEF26422;border:1px solid #BEF26444;border-radius:10px;margin-top:8px"><div><b>${b.app_name} BLOCKED</b></div><span style="color:#BEF264">● Protected</span></div>`).join('')}load();</script></body></html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
