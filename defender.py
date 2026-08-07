from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>GHOSTBOX DEFENDER</title>
<style>
body { background:#0a0a0a; color:#00ff88; font-family: monospace; text-align:center; padding:50px; }
h1 { font-size:3em; text-shadow: 0 0 20px #00ff88; }
.box { border:2px solid #00ff88; padding:30px; border-radius:15px; max-width:600px; margin:20px auto; box-shadow: 0 0 30px #00ff8844; }
button { background:#00ff88; color:#000; padding:15px 30px; font-size:1.2em; border:none; border-radius:8px; cursor:pointer; margin:10px; font-weight:bold; }
button:hover { background:#00cc6a; }
</style>
</head>
<body>
<h1>👻 GHOSTBOX DEFENDER 🛡️</h1>
<div class="box">
<h2>System Online - LIVE</h2>
<p>Your project is successfully deployed on Render!</p>
<button onclick="alert('GHOSTBOX Activated! 👻')">ACTIVATE DEFENDER</button>
<button onclick="alert('Scanning... No ghosts found ✅')">SCAN</button>
</div>
<p>Deployed: 2026 | Render + GitHub Auto-Deploy Active</p>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run()
