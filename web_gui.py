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
<title>Fast Vote Automation - Samya Jain</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { background: #0b0f19; color: #f3f4f6; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
  .card { background: #161f30; border: 1px solid #283548; border-radius: 16px; width: 100%; max-width: 480px; padding: 32px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
  .badge { background: #ec4899; color: white; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 12px; }
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 6px; color: #ffffff; }
  p.sub { font-size: 14px; color: #9ca3af; margin-bottom: 24px; }
  .stat-box { background: #1f2d45; border-radius: 10px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
  .stat-label { font-size: 13px; color: #94a3b8; }
  .stat-val { font-size: 24px; font-weight: 800; color: #38bdf8; }
  .field { margin-bottom: 16px; }
  label { display: block; font-size: 13px; color: #cbd5e1; margin-bottom: 6px; font-weight: 500; }
  input { width: 100%; background: #0f172a; border: 1px solid #334155; color: white; padding: 12px 14px; border-radius: 8px; font-size: 15px; outline: none; transition: border 0.2s; }
  input:focus { border-color: #ec4899; }
  .btn { width: 100%; background: #ec4899; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s; margin-top: 8px; }
  .btn:hover { background: #db2777; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .log-box { margin-top: 20px; background: #0f172a; border: 1px solid #222f42; border-radius: 8px; padding: 12px; font-family: monospace; font-size: 13px; max-height: 140px; overflow-y: auto; color: #a5f3fc; }
  .step-hidden { display: none; }
</style>
</head>
<body>
<div class="card">
  <div class="badge">Direct API Booster</div>
  <h1>Fast Vote: Samya Jain</h1>
  <p class="sub">College Ke Tashanbaaz (Jabalpur) - Singing (Solo)</p>

  <div class="stat-box">
    <div>
      <div class="stat-label">Current Live Votes</div>
      <div style="font-size:12px; color:#64748b;">Target: Samya Jain</div>
    </div>
    <div class="stat-val" id="voteCount">...</div>
  </div>

  <div id="step1">
    <div class="field">
      <label>10-Digit Mobile Number</label>
      <input type="tel" id="phone" placeholder="e.g. 9876543210" maxlength="10">
    </div>
    <div class="field">
      <label>Full Name</label>
      <input type="text" id="fullName" value="Voter" placeholder="Voter Name">
    </div>
    <div class="field">
      <label>Email Address</label>
      <input type="email" id="email" placeholder="email@gmail.com">
    </div>
    <button class="btn" id="btnSendOtp" onclick="sendOtp()">Send OTP Instantly</button>
  </div>

  <div id="step2" class="step-hidden">
    <div class="field">
      <label>Enter 6-Digit OTP</label>
      <input type="text" id="otp" placeholder="123456" maxlength="6" style="letter-spacing: 4px; font-size: 20px; text-align: center;">
    </div>
    <button class="btn" id="btnSubmitVote" onclick="submitVote()" style="background:#10b981;">⚡ Verify & Cast Vote Fast</button>
    <button class="btn" onclick="resetForm()" style="background:#475569; font-size:13px; padding:8px; margin-top:6px;">Cancel / Start Over</button>
  </div>

  <div class="log-box" id="logBox">Status: Ready.</div>
</div>

<script>
let state = { accessToken: '', initialToken: '', phone: '' };

function log(msg) {
  const box = document.getElementById('logBox');
  box.innerHTML = msg + '<br>' + box.innerHTML;
}

async function refreshStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    document.getElementById('voteCount').innerText = data.votes;
  } catch(e){}
}
refreshStats();
setInterval(refreshStats, 5000);

async function sendOtp() {
  const phone = document.getElementById('phone').value.trim();
  let email = document.getElementById('email').value.trim();
  if (!email) {
    email = 'voter' + phone.slice(-4) + '@gmail.com';
    document.getElementById('email').value = email;
  }
  if (phone.length !== 10) {
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
      log('✅ OTP sent successfully! Check SMS.');
      document.getElementById('step1').classList.add('step-hidden');
      document.getElementById('step2').classList.remove('step-hidden');
      document.getElementById('otp').focus();
    } else {
      log('❌ Failed: ' + (data.message || 'Error sending OTP'));
      alert(data.message || 'Error sending OTP');
    }
  } catch(e) {
    log('❌ Request error: ' + e.message);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Send OTP Instantly';
  }
}

async function submitVote() {
  const otp = document.getElementById('otp').value.trim();
  const fullName = document.getElementById('fullName').value.trim() || 'Voter';
  const email = document.getElementById('email').value.trim() || ('voter' + state.phone.slice(-4) + '@gmail.com');

  if (otp.length < 4) {
    alert('Please enter the OTP received');
    return;
  }

  const btn = document.getElementById('btnSubmitVote');
  btn.disabled = true;
  btn.innerText = '⚡ Processing Vote...';
  log('⏳ Verifying OTP & casting vote via direct API...');

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
    btn.innerText = '⚡ Verify & Cast Vote Fast';
  }
}

function resetForm() {
  document.getElementById('step2').classList.add('step-hidden');
  document.getElementById('step1').classList.remove('step-hidden');
  document.getElementById('phone').value = '';
  document.getElementById('otp').value = '';
}
</script>
</body>
</html>
"""

class FastVoteHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(get_stats()).encode("utf-8"))
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
            phone = body.get("phone")
            full_name = body.get("fullName", "Voter")
            email = body.get("email", f"voter{phone[-4:]}@gmail.com")

            # 1. Verify OTP
            verify_res = api_call("verify-otp", method="POST", data={
                "otp": otp,
                "accessToken": access_token,
                "phone": phone,
                "cityID": CITY_ID
            }, token=initial_token)

            if not verify_res.get("status"):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": verify_res.get("message", "Invalid OTP")}).encode("utf-8"))
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
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": msg}).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": vote_res.get("message", "Vote failed")}).encode("utf-8"))

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
