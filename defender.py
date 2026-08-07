from flask import Flask, request
import re, socket

app = Flask(__name__)

def check_phishing(url):
    url = url.lower()
    score = 0
    reasons = []
    if "@" in url: 
        score+=3; reasons.append("Contains @")
    if url.count("-")>3:
        score+=2; reasons.append("Too many hyphens")
    if "mtn" in url and "mtn.com.gh" not in url and "mtn-gh" in url:
        score+=4; reasons.append("Fake MTN domain")
    if "bit.ly" in url or "tinyurl" in url:
        score+=2; reasons.append("Shortened link")
    if "vodafone" in url or "telecel" in url:
        if ".com.gh" not in url: score+=3; reasons.append("Fake telco")
    if re.search(r"\d+\.\d+\.\d+\.\d+", url):
        score+=3; reasons.append("IP address link")
    
    status = "🔴 BLOCK - PHISHING!" if score>=3 else "🟢 Safe"
    return status, score, ", ".join(reasons)

def check_momo(text):
    text=text.lower()
    scams = ["send your pin", "your momo is blocked", "send to", "win lottery", "secret code", "urgently", "your account has been suspended"]
    found = [s for s in scams if s in text]
    if found:
        return f"🔴 SCAM DETECTED: {', '.join(found)}", 95
    else:
        return "🟢 Looks normal", 10

def scan_ports(target):
    open_ports=[]
    for port in [21,22,80,443,8080,8000,5000]:
        try:
            s=socket.socket()
            s.settimeout(0.5)
            s.connect((target, port))
            open_ports.append(port)
            s.close()
        except: pass
    return open_ports

HTML = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:sans-serif;background:#0f0f0f;color:white;padding:15px}
.card{background:#1e1e1e;padding:15px;border-radius:12px;margin-bottom:15px;border-left:4px solid #00ff88}
input,textarea{width:95%;padding:12px;border-radius:8px;border:none;margin:8px 0}
button{padding:12px 20px;background:#00ff88;color:black;border:none;border-radius:8px;font-weight:bold;width:100%}
.result{padding:10px;background:black;border-radius:8px;margin-top:10px;font-weight:bold}
h1{color:#00ff88} small{color:gray}
</style>
</head>
<body>
<h1>🛡️ GHOSTBOX DEFENDER v3</h1>
<small>Built in Accra | By You | Shareable Edition</small>

<div class="card">
<h3>1. 🔍 Phishing Link Checker</h3>
<form method="POST" action="/scan_link">
<input name="url" placeholder="https://mtn-gh-promo-free.com" value="https://mtn-gh-promo-free.com">
<button>Scan Link</button>
</form>
<div class="result">{{link_result}}</div>
</div>

<div class="card">
<h3>2. 💬 AI MoMo Scam Detector</h3>
<form method="POST" action="/scan_sms">
<textarea name="sms" rows="3" placeholder="Paste MoMo SMS here..."></textarea>
<button>Check SMS</button>
</form>
<div class="result">{{sms_result}}</div>
</div>

<div class="card">
<h3>3. 📱 My Device Scanner</h3>
<form method="POST" action="/scan_port">
<input name="target" value="127.0.0.1">
<button>Scan My Ports</button>
</form>
<div class="result">{{port_result}}</div>
</div>

<p><small>Share: defender.ghostbox.gh</small></p>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML.replace("{{link_result}}","Ready to protect").replace("{{sms_result}}","Paste SMS").replace("{{port_result}}","Ready")

@app.route('/scan_link', methods=['POST'])
def scan_link():
    url = request.form['url']
    status, score, reasons = check_phishing(url)
    res = f"{status} (Score: {score}/10) - {reasons}"
    return HTML.replace("{{link_result}}",res).replace("{{sms_result}}","").replace("{{port_result}}","")

@app.route('/scan_sms', methods=['POST'])
def scan_sms():
    sms = request.form['sms']
    status, score = check_momo(sms)
    res = f"{status} - Risk: {score}%"
    return HTML.replace("{{sms_result}}",res).replace("{{link_result}}","").replace("{{port_result}}","")

@app.route('/scan_port', methods=['POST'])
def scan_port():
    target = request.form['target']
    ports = scan_ports(target)
    res = f"Open ports on {target}: {ports}" if ports else f"No risky ports open on {target} - Safe ✅"
    return HTML.replace("{{port_result}}",res).replace("{{link_result}}","").replace("{{sms_result}}","")

if __name__ == "__main__":
    app.run()
"""

