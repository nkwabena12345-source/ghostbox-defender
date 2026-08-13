# GH SHIELD V9.3 - FINAL DEMO - Ghana Always Works Even If VT Fails
import os, re, time, hashlib, requests
from flask import Flask, request, render_template_string
from collections import defaultdict

app = Flask(__name__)
VT_KEY = os.environ.get("VT_KEY", "")
HIBP_KEY = os.environ.get("HIBP_KEY", "")

CACHE = {}
CACHE_TIME = 3600
user_requests = defaultdict(list)
vt_used_today = 0
VT_QUOTA = 480

HTML = """
<!DOCTYPE html>
<html>
<head><title>GH SHIELD V9.3</title>
<style>
body{background:#0a0a0a;color:#00ff88;font-family:monospace;padding:20px}
.box{border:1px solid #00ff88;padding:15px;margin:10px 0;border-radius:8px}
input,button{padding:10px;width:90%;margin:5px;background:#111;color:#00ff88;border:1px solid #00ff88}
.high{color:red;font-weight:bold}.medium{color:yellow}.low{color:#00ff88}
</style>
</head>
<body>
<h1>🛡️ GH SHIELD V9.3 - GHANA REAL API</h1>
<div class="box">STATUS: ONLINE | VT: CONNECTED | CACHE: {{cache_size}} | VT USED: {{vt_used}}/480</div>
<div class="box">
<h3>1. LINK REAL - VirusTotal 70 + Ghana Patterns</h3>
<form method="POST"><input name="url" placeholder="greatland-gold.com"><button name="action" value="link">SCAN LINK</button></form>
<div>{{link_result}}</div>
</div>
<div class="box">
<h3>2. PWD REAL - HaveIBeenPwned</h3>
<form method="POST"><input name="pwd" type="password" placeholder="password123"><button name="action" value="pwd">CHECK PWD</button></form>
<div>{{pwd_result}}</div>
</div>
<div class="box">
<h3>3. BREACH REAL</h3>
<form method="POST"><input name="email" placeholder="test@gmail.com"><button name="action" value="breach">CHECK BREACH</button></form>
<div>{{breach_result}}</div>
</div>
<div class="box">
<h3>4. WAF - SQLi/XSS/CMDi/LFI</h3>
<form method="POST"><input name="waf" placeholder="' OR '1'='1"><button name="action" value="waf">TEST WAF</button></form>
<div>{{waf_result}}</div>
</div>
</body>
</html>
"""

def ghana_patterns(url):
    u = url.lower()
    score = 0
    reasons = []
    if "invite=" in u:
        score += 40
        reasons.append("invite= MLM")
    if "greatland" in u:
        score += 50
        reasons.append("greatland-gold scam")
    if "gold.com" in u or "gold" in u and "invite" in u:
        if score < 50:
            score += 50
            reasons.append("gold+invite")
    if "momo" in u:
        score += 20
        reasons.append("MoMo")
    return score, reasons

def real_vt_check(url):
    global vt_used_today
    now = time.time()
    ip = request.remote_addr
    if url in CACHE:
        res, ts = CACHE[url]
        if now - ts < CACHE_TIME:
            return res + " [CACHED Ghana Fast]"
    if vt_used_today >= VT_QUOTA:
        return "VT LIMIT - Ghana only"
    user_requests[ip] = [t for t in user_requests[ip] if now - t < 60]
    if len(user_requests[ip]) >= 5:
        return "SLOW DOWN 5/min"
    if not VT_KEY:
        return "VT_KEY missing"
    try:
        r = requests.post("https://www.virustotal.com/api/v3/urls", headers={"x-apikey": VT_KEY}, data={"url": url}, timeout=15)
        if r.status_code!= 200:
            return f"VT {r.status_code} - Ghana still works"
        j = r.json()
        if "data" not in j:
            return "VT no data - Ghana works"
        url_id = j["data"]["id"]
        r2 = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_KEY}, timeout=15)
        stats = r2.json()["data"]["attributes"]["last_analysis_stats"]
        mal = stats.get("malicious",0)
        res = f"VT REAL: {mal}/70 malicious"
        CACHE[url] = (res, now)
        user_requests[ip].append(now)
        vt_used_today += 1
        return res
    except Exception as e:
        return f"VT Offline - Ghana Active ({str(e)[:40]})"

def real_pwd_check(pwd):
    try:
        sha1 = hashlib.sha1(pwd.encode()).hexdigest().upper()
        pre, suf = sha1[:5], sha1[5:]
        r = requests.get(f"https://api.pwnedpasswords.com/range/{pre}", timeout=10)
        for line in r.text.splitlines():
            if line.startswith(suf):
                cnt = line.split(":")[1]
                return f"PWNED: Found {cnt} times!"
        return "SAFE: Not in 613M leaks"
    except Exception as e:
        return f"Error {e}"

def real_breach_check(email):
    if not HIBP_KEY:
        return "Need HIBP_KEY - use PWD check (free)"
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers={"hibp-api-key": HIBP_KEY, "user-agent": "GH-SHIELD"}, timeout=10)
        if r.status_code == 200:
            return f"BREACHED in {[b['Name'] for b in r.json()]}"
        if r.status_code == 404:
            return "Not breached"
        return f"HIBP {r.status_code}"
    except Exception as e:
        return f"Error {e}"

def waf_check(payload):
    if not payload:
        return ""
    low = payload.lower()
    if "../" in payload or "/etc/passwd" in low:
        return "BLOCKED LFI"
    if "<script" in low or "onerror=" in low:
        return "BLOCKED XSS"
    if "' or '1'='1" in low or "' or 1=1" in low:
        return "BLOCKED SQLi"
    if ";" in payload and ("cat " in low or "ls " in low):
        return "BLOCKED CMDi"
    return "ALLOW Clean"

@app.route("/", methods=["GET","POST"])
def home():
    link_result = pwd_result = breach_result = waf_result = ""
    if request.method == "POST":
        act = request.form.get("action")
        if act == "link":
            url = request.form.get("url","").strip()
            score, reasons = ghana_patterns(url)
            vt = real_vt_check(url) if url else ""
            gh = f"<br>Ghana Score: {score} - {', '.join(reasons) if reasons else 'No pattern'}"
            final = "HIGH RISK" if score>=40 else "LOW"
            color = "high" if score>=40 else "low"
            link_result = f"{vt}{gh}<br>Final: <span class='{color}'>{final}</span>"
        elif act == "pwd":
            pwd = request.form.get("pwd","")
            pwd_result = real_pwd_check(pwd)
        elif act == "breach":
            email = request.form.get("email","")
            breach_result = real_breach_check(email)
        elif act == "waf":
            waf_result = waf_check(request.form.get("waf",""))
    return render_template_string(HTML, link_result=link_result, pwd_result=pwd_result, breach_result=breach_result, waf_result=waf_result, cache_size=len(CACHE), vt_used=vt_used_today)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
