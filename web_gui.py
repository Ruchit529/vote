"""
College Ke Tashanbaaz - Fast Voting Local Web Interface
Run with: py web_gui.py
Open: http://localhost:5000
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.error
import time

PORT = 5000
BASE_URL = "https://api.collegeketashanbaaz.in/v1"
SEASON_ID = "1684"
CITY_ID = 1693  # Jabalpur
TARGET_PARTICIPANT_ID = 132155  # Samya Jain
TARGET_NAME = "Samya Jain"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "seasonID": SEASON_ID,
    "Origin": "https://collegeketashanbaaz.in",
    "Referer": "https://collegeketashanbaaz.in/shortlisted"
}

def api_call(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}/{endpoint}"
    req_headers = HEADERS.copy()
    if token:
        req_headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            return {"status": 0, "message": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"status": 0, "message": str(e)}

def get_stats():
    res = api_call(f"entries-list/?cityID={CITY_ID}")
    votes = "N/A"
    if res.get("status") == 1 and "payload" in res:
        for entry in res["payload"]:
            if entry.get("participantID") == TARGET_PARTICIPANT_ID:
                votes = entry.get("totalVotes", "N/A")
                break
    return {"candidate": TARGET_NAME, "participantID": TARGET_PARTICIPANT_ID, "votes": votes}

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ultra-Fast Voting Tool - Samya Jain</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { background: #080c14; color: #f3f4f6; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
  .card { background: #111827; border: 1px solid #1f293d; border-radius: 16px; width: 100%; max-width: 440px; padding: 28px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }
  .badge { background: linear-gradient(135deg, #ec4899, #8b5cf6); color: white; padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 12px; }
  h1 { font-size: 22px; font-weight: 800; margin-bottom: 4px; color: #ffffff; }
  p.sub { font-size: 13px; color: #9ca3af; margin-bottom: 20px; }
  .stat-box { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
  .stat-label { font-size: 13px; color: #94a3b8; font-weight: 500; }
  .stat-val { font-size: 26px; font-weight: 800; color: #38bdf8; }
  .field { margin-bottom: 16px; }
  label { display: block; font-size: 13px; color: #cbd5e1; margin-bottom: 6px; font-weight: 600; }
  input { width: 100%; background: #0f172a; border: 1.5px solid #334155; color: white; padding: 12px 14px; border-radius: 8px; font-size: 16px; outline: none; transition: border 0.2s; }
  input:focus { border-color: #ec4899; box-shadow: 0 0 0 3px rgba(236,72,153,0.15); }
  .btn { width: 100%; background: #ec4899; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s; margin-top: 6px; }
  .btn:hover { background: #db2777; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .log-box { margin-top: 18px; background: #090d16; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; max-height: 140px; overflow-y: auto; color: #a5f3fc; }
  .step-hidden { display: none; }
</style>
</head>
<body>
<div class="card">
  <div class="badge">Direct Fast Voter</div>
  <h1>Vote for Samya Jain</h1>
  <p class="sub">College Ke Tashanbaaz (Jabalpur)</p>

  <div class="stat-box">
    <div>
      <div class="stat-label">Live Candidate Votes</div>
      <div style="font-size:12px; color:#64748b;">Participant ID: 132155</div>
    </div>
    <div class="stat-val" id="voteCount">...</div>
  </div>

  <div id="step1">
    <div class="field">
      <label>Mobile Number (10 Digits)</label>
      <input type="tel" id="phone" placeholder="Enter mobile number" maxlength="10" autofocus onkeyup="if(event.key==='Enter') sendOtp()">
    </div>
    <button class="btn" id="btnSendOtp" onclick="sendOtp()">⚡ Send OTP Instantly</button>
  </div>

  <div id="step2" class="step-hidden">
    <div class="field">
      <label>Enter 6-Digit OTP</label>
      <input type="text" id="otp" placeholder="123456" maxlength="6" style="letter-spacing: 6px; font-size: 22px; text-align: center;" onkeyup="if(event.key==='Enter') submitVote()">
    </div>
    <button class="btn" id="btnSubmitVote" onclick="submitVote()" style="background:#10b981;">🚀 Verify & Cast Vote</button>
    <button class="btn" onclick="resetForm()" style="background:#334155; font-size:13px; padding:8px; margin-top:8px;">Back / Try Another Number</button>
  </div>

  <div class="log-box" id="logBox">Status: Ready to vote.</div>
</div>

<script>
let state = { accessToken: '', initialToken: '', phone: '' };

function log(msg) {
  const box = document.getElementById('logBox');
  box.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}<br>` + box.innerHTML;
}

async function refreshStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    document.getElementById('voteCount').innerText = data.votes;
  } catch(e){}
}
refreshStats();
setInterval(refreshStats, 4000);

async function sendOtp() {
  const phone = document.getElementById('phone').value.trim();
  if (phone.length !== 10 || isNaN(phone)) {
    alert('Please enter a valid 10-digit mobile number');
    return;
  }
  
  const btn = document.getElementById('btnSendOtp');
  btn.disabled = true;
  btn.innerText = 'Sending OTP...';
  log('⏳ Requesting OTP for ' + phone + '...');

  try {
    const res = await fetch('/api/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const data = await res.json();
    if (data.status === 1) {
      state.accessToken = data.payload.accessToken;
      state.initialToken = data.payload.token;
      state.phone = phone;
      log('✅ OTP sent successfully!');
      document.getElementById('step1').classList.add('step-hidden');
      document.getElementById('step2').classList.remove('step-hidden');
      setTimeout(() => document.getElementById('otp').focus(), 100);
    } else {
      log('❌ Failed: ' + (data.message || 'Error sending OTP'));
      alert(data.message || 'Error sending OTP');
    }
  } catch(e) {
    log('❌ Request error: ' + e.message);
  } finally {
    btn.disabled = false;
    btn.innerText = '⚡ Send OTP Instantly';
  }
}

async function submitVote() {
  const otp = document.getElementById('otp').value.trim();

  if (otp.length < 4) {
    alert('Please enter the OTP received');
    return;
  }

  const btn = document.getElementById('btnSubmitVote');
  btn.disabled = true;
  btn.innerText = '🚀 Processing Vote...';
  log('⏳ Verifying OTP & submitting vote...');

  // Auto-generate random dummy voter details
  const randomId = Math.floor(1000 + Math.random() * 9000);
  const fullName = 'Voter ' + randomId;
  const email = 'voter' + state.phone.slice(-4) + '_' + randomId + '@gmail.com';

  try {
    const res = await fetch('/api/verify-and-vote', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        otp,
        accessToken: state.accessToken,
        initialToken: state.initialToken,
        phone: state.phone,
        fullName,
        email
      })
    });
    const data = await res.json();
    if (data.success) {
      log('🎉 SUCCESS! ' + data.message);
      alert('🎉 ' + data.message);
      refreshStats();
      resetForm();
    } else {
      log('⚠️ ' + data.message);
      alert(data.message);
    }
  } catch(e) {
    log('❌ Error: ' + e.message);
  } finally {
    btn.disabled = false;
    btn.innerText = '🚀 Verify & Cast Vote';
  }
}

function resetForm() {
  document.getElementById('step2').classList.add('step-hidden');
  document.getElementById('step1').classList.remove('step-hidden');
  document.getElementById('phone').value = '';
  document.getElementById('otp').value = '';
  setTimeout(() => document.getElementById('phone').focus(), 100);
}
</script>
</body>
</html>
"""

import os


VOTE_LOG_FILE = "vote_log.json"

def load_vote_log():
    if os.path.exists(VOTE_LOG_FILE):
        try:
            with open(VOTE_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"totalVotes": 0, "phoneVotes": {}, "history": []}

def record_local_vote(phone, status="Success", message=""):
    data = load_vote_log()
    phone_key = str(phone or "Unknown").strip()
    if phone_key not in data["phoneVotes"]:
        data["phoneVotes"][phone_key] = {"count": 0, "lastVoted": None}
    if status == "Success":
        data["totalVotes"] += 1
        data["phoneVotes"][phone_key]["count"] += 1
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    data["phoneVotes"][phone_key]["lastVoted"] = ts
    data["history"].insert(0, {
        "phone": phone_key,
        "timestamp": ts,
        "status": status,
        "message": message
    })
    data["history"] = data["history"][:500]
    try:
        with open(VOTE_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
    return data

class FastVoteHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/admin" or self.path == "/admin.html":
            admin_file = os.path.join(os.path.dirname(__file__), "public", "admin.html")
            if os.path.exists(admin_file):
                with open(admin_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(get_stats()).encode("utf-8"))
        elif self.path == "/api/admin-stats":
            log_data = load_vote_log()
            resp = {
                "success": True,
                "totalVotesCast": log_data.get("totalVotes", 0),
                "phoneVotes": log_data.get("phoneVotes", {}),
                "history": log_data.get("history", [])
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8")
        body = json.loads(post_body) if post_body else {}

        if self.path == "/api/send-otp":
            phone = body.get("phone", "")
            resp = api_call("login-via-otp", method="POST", data={"phone": phone, "forParticipation": False})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif self.path == "/api/verify-and-vote":
            otp = body.get("otp")
            access_token = body.get("accessToken")
            initial_token = body.get("initialToken")
            phone = body.get("phone", "")
            full_name = body.get("fullName") or f"Voter {time.time_ns() % 10000}"
            email = body.get("email") or f"voter{phone[-4:] if len(phone)>=4 else '0000'}@gmail.com"

            # 1. Verify OTP
            verify_res = api_call("verify-otp", method="POST", data={
                "otp": otp,
                "accessToken": access_token,
                "phone": phone,
                "cityID": CITY_ID
            }, token=initial_token)

            if not verify_res.get("status"):
                err_msg = verify_res.get("message", "Invalid OTP")
                record_local_vote(phone, "Failed", err_msg)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": err_msg}).encode("utf-8"))
                return

            user_token = verify_res.get("payload", {}).get("token") or initial_token
            next_screen = verify_res.get("payload", {}).get("nextScreen")

            # 2. Register if needed
            if next_screen in ["voter-signup", "register"]:
                reg_res = api_call("register/voter", method="POST", data={"fullName": full_name, "email": email}, token=user_token)
                if reg_res.get("status"):
                    user_token = reg_res.get("payload", {}).get("token") or user_token

            # 3. Vote for Samya Jain
            vote_res = api_call(f"vote/{TARGET_PARTICIPANT_ID}", method="POST", token=user_token)
            if vote_res.get("status"):
                msg = vote_res.get("message", "Vote cast successfully!")
                record_local_vote(phone, "Success", msg)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": msg}).encode("utf-8"))
            else:
                fail_msg = vote_res.get("message", "Vote failed")
                record_local_vote(phone, "Failed", fail_msg)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": fail_msg}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    server = socketserver.TCPServer(("", PORT), FastVoteHandler)
    print(f"🚀 High-Speed Voting Web Server running at: http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")