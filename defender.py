def ghana_patterns(url):
    score = 0
    reasons = []
    u = url.lower()
    if "invite=" in u:
        score += 40; reasons.append("invite= (MLM)")
    if "greatland" in u:
        score += 50; reasons.append("greatland-gold Ghana scam")
    if "gold" in u and "invite" in u:
        if "greatland-gold Ghana scam" not in reasons:
            score += 50; reasons.append("gold+invite combo")
    if "momo" in u and "double" in u:
        score += 40; reasons.append("MoMo double")
    if score == 0 and len(u) > 10:
        # fallback check
        if "gold.com" in u:
            score += 50; reasons.append("suspicious gold domain")
    return score, reasons

def real_vt_check(url):
    global vt_used_today
    now = time.time()
    ip = request.remote_addr

    if url in CACHE:
        res, ts = CACHE[url]
        if now - ts < CACHE_TIME:
            return res + " <br><b>[CACHED - Ghana Fast ⚡]</b>"

    if vt_used_today >= VT_QUOTA:
        return "⚠️ VT LIMIT - Ghana Patterns Only"

    user_requests[ip] = [t for t in user_requests[ip] if now - t < 60]
    if len(user_requests[ip]) >= 5:
        return "⏳ SLOW DOWN - 5/min max"

    if not VT_KEY:
        return "VT_KEY missing - Add in Render Env"

    try:
        r = requests.post("https://www.virustotal.com/api/v3/urls", headers={"x-apikey": VT_KEY}, data={"url": url}, timeout=15)
        # DEBUG: if VT error, show it
        if r.status_code!= 200:
            return f"VT API {r.status_code}: {r.text[:200]}<br>→ Using Ghana Patterns (still works!)"
        j = r.json()
        if "data" not in j:
            return f"VT No data:
