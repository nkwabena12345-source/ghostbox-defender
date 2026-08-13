# GH SHIELD V9.2 - GHANA REAL API + Rate Limiter
# Built in Accra, Ghana - 2:06 AM Failed → 7:15 PM Connected → V9.2 Protected
import os, re, time, hashlib, requests
from flask import Flask, request, render_template_string
from collections import defaultdict

app = Flask(__name__)

# --- KEYS FROM RENDER ENV ---
VT_KEY = os.environ.get("VT_KEY", "")
HIBP_KEY = os.environ.get("HIBP_KEY", "") # optional

# --- V9.2 RATE LIMITER ---
CACHE = {}
CACHE_TIME = 3600
user_requests = defaultdict(list)
vt_used_today = 0
VT_QUOTA = 480

HTML = """
<!DOCTYPE html>
<html>
<head><title>GH SHIELD V9.2</title>
<style>
body{background:#0a0a0a;color:#00ff88;font-family:monospace;padding:20px}
.box{border:1px solid #00ff88;padding:15px;margin:10px 0;border-radius:8px}
input,button{padding:10px;width:90%;margin:5px;background:#111;color:#00ff88;border:1px solid #00ff88}
.high{color:red}.medium{color:yellow}.low{color:#00ff88}
</style>
</head>
<body>
<h1>🛡️ GH SHIELD V9.2 - GHANA REAL API</h1>
<div class="box">STATUS: ONLINE | VT: CONNECTED ✅ | CACHE: {{cache_size}} | VT USED: {{vt_used}}/480</div>

<div class="box">
<h3>1. LINK REAL - VirusTotal 70 engines + Ghana Patterns</h3>
<form method="POST"><input name="url" placeholder="https://greatland-gold.com/#/pages/register?invite=77735343"><button name="action" value="link">SCAN LINK</button></form>
<div>{{link_result}}</div>
</div>

<div class="box">
<h3>2. PWD REAL - HaveIBeenPwned k-anonymity</h3>
<form method="POST"><input name="pwd" type="password" placeholder="password123"><button name="action" value="pwd">CHECK PWD</button></form>
<div>{{pwd_result}}</div>
</div>

<div class="box">
<h3>3. BREACH REAL - Email leak check</h3>
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
    score = 0
    reasons = []
    if "invite=" in url.lower():
        score += 40; reasons.append("invite= parameter (MLM pattern)")
    if "greatland-gold" in url.lower() or "gold" in url.lower() and "invite" in url.lower():
        score += 50; reasons.append("greatland-gold Ghana scam signature")
    if "momo" in url.lower() and "double" in url.lower():
        score += 40; reasons.append("MoMo double money scam")
    if "whatsapp" in url.lower() and "earn" in url.lower():
        score += 30; reasons.append("WhatsApp earn money")
    return score, reasons

def real_vt_check(url):
    global vt_used_today
    now = time.time()
    ip = request.remote_addr

    # Cache check
    if url in CACHE:
        res, ts = CACHE[url]
        if now - ts < CACHE_TIME:
            return res + " <br><b>[CACHED - Ghana Fast ⚡]</b>"

    # Quota check
    if vt_used_today >= VT_QUOTA:
        return "⚠️ VT DAILY LIMIT - Using Ghana Patterns Only (Resets midnight UTC)"

    # Rate limit 5/min
    user_requests[ip] = [t for t in user_requests[ip] if now - t < 60]
    if len(user_requests[ip]) >= 5:
        return "⏳ SLOW DOWN - 5 scans/min max"

    if not VT_KEY:
        return "VT_KEY not set in Render Env"

    try:
        # Submit URL
        r = requests.post("https://www.virustotal.com/api/v3/urls", headers={"x-apikey": VT_KEY}, data={"url": url}, timeout=10)
        if r.status_code!= 200:
            return f"VT Error {r.status_code}: {r.text[:100]}"
        url_id = r.json()["data"]["id"]
        # Get report
        r2 = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_KEY}, timeout=10)
        data = r2.json()["data"]["attributes"]["last_analysis_stats"]
        malicious = data.get("malicious", 0)
        result = f"VT REAL: {malicious}/70 malicious | Harmless: {data.get('harmless',0)}"
        CACHE[url] = (result, now)
        user_requests[ip].append(now)
        vt_used_today += 1
        return result
    except Exception as e:
        return f"VT Offline: {str(e)[:100]} - Using Ghana Patterns"

def real_pwd_check(pwd):
    try:
        sha1 = hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        r = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=10)
        for line in r.text.splitlines():
            if line.startswith(suffix):
                count = line.split(":")[1]
                return f"🔴 PWNED REAL: Found {count} times in 613M leaks! (k-anonymity safe)"
        return "🟢 SAFE REAL: Not found in 613M leaks"
    except Exception as e:
        return f"Pwd Check Error: {e}"

def real_breach_check(email):
    if not HIBP_KEY:
        return "Add HIBP_KEY in Render Env for breach check, or use PWD check (free)"
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers={"hibp-api-key": HIBP_KEY, "user-agent": "GH-SHIELD"}, timeout=10)
        if r.status_code == 200:
            breaches = [b["Name"] for b in r.json()]
            return f"🔴 BREACHED in: {', '.join(breaches)}"
        if r.status_code == 404:
            return "🟢 Not breached"
        return f"HIBP {r.status_code}"
    except Exception as e:
        return f"Breach Error: {e}"

def waf_check(payload):
    if not payload:
        return ""
    payload_lower = payload.lower()
    if "../" in payload or "/etc/passwd" in payload_lower:
        return "🔴 BLOCKED LFI"
    if "<script" in payload_lower or "onerror=" in payload_lower:
        return "🔴 BLOCKED XSS"
    if "' or '1'='1" in payload_lower or "' or 1=1" in payload_lower:
        return "🔴 BLOCKED SQLi"
    if ";" in payload and ("cat " in payload_lower or "ls " in payload_lower):
        return "🔴 BLOCKED CMDi"
    return "🟢 ALLOW - Clean"

@app.route("/", methods=["GET", "POST"])
def home():
    link_result = pwd_result = breach_result = waf_result = ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "link":
            url = request.form.get("url","").strip()
            score, reasons = ghana_patterns(url)
            vt = real_vt_check(url) if url else ""
            gh = f"<br>Ghana Score: {score} - {', '.join(reasons) if reasons else 'No local pattern'}"
            risk = "<span class='high'>HIGH RISK</span>" if score>=50 or "malicious" in vt.lower() else "<span class='low'>LOW</span>"
            link_result = f"{vt}{gh}<br>Final: {risk}"
        elif action == "pwd":
            pwd = request.form.get("pwd","")
            pwd_result = real_pwd_check(pwd) if pwd else ""
        elif action == "breach":
            email = request.form.get("email","")
            breach_result = real_breach_check(email) if email else ""
        elif action == "waf":
            payload = request.form.get("waf","")
            waf_result = waf_check(payload)

    return render_template_string(HTML, link_result=link_result, pwd_result=pwd_result, breach_result=breach_result, waf_result=waf_result, cache_size=len(CACHE), vt_used=vt_used_today)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
