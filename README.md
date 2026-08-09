# 👻 GH SHIELD V9.1 GHANA REAL API 🛰️
### Real Threat Intel Platform Built in Accra, Ghana

> **LIVE DEMO:** https://ghostbox-defender.onrender.com
> **STATUS:** 🟢 V9.1 ONLINE | VT_KEY CONNECTED ✅ | REAL VirusTotal + HIBP

Built at 5AM - 7PM in Accra, Ghana - From Failed Deploy to Real SOC Platform.

---

## 💥 WHAT IS REAL vs FAKE?

| Feature | V8 FAKE | V9.1 REAL ✅ |
|---------|---------|-------------|
| LINK SCAN | Checks if word `bit.ly` in URL | **REAL VirusTotal API - 70 engines** |
| PWD CHECK | If `password` in text = pwned | **REAL HaveIBeenPwned - 613M passwords, k-anonymity** |
| BREACH | Fake list | **REAL HIBP Breach API** |
| GHANA RULES | None | **invite=, greatland-gold, momo double detector** |

---

## 🛡️ 5 MODULES

1. **WAF** - SQLi / XSS / Command Injection blocker
2. **LINK REAL** - VirusTotal v3 API + Ghana scam patterns (greatland-gold, invite=)
3. **BREACH REAL** - HaveIBeenPwned email breach check
4. **PWD REAL** - Pwned Passwords API with k-anonymity (only 5 chars of SHA1 sent)
5. **MoMo Fraud Detector** - Ghana Mobile Money scam detector

---

## 🚀 INSTALLATION

### Option 1: Deploy to Render (FREE) - Recommended for Ghana

1. Fork this repo
2. Go to https://dashboard.render.com → New Web Service → Connect your repo
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn defender:app`
4. Add Environment Variable:
   - Key: `VT_KEY` 
   - Value: Your VirusTotal API key from https://www.virustotal.com/gui/my-apikey
5. Deploy! Wait for `Live` green badge.

### Option 2: Local Installation (Accra / Offline Dev)

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ghostbox-defender.git
cd ghostbox-defender

# Install Python deps
pip install -r requirements.txt

# requirements.txt must contain:
# Flask
# requests
# gunicorn

# Set VT_KEY (Windows)
set VT_KEY=your_virustotal_key_here
# Set VT_KEY (Linux/Mac)
export VT_KEY=your_virustotal_key_here

# Run
python defender.py
# or
gunicorn defender:app

# Open: http://127.0.0.1:5000
