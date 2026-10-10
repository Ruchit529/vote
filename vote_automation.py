"""
College Ke Tashanbaaz - Fast Direct API Vote Automation Script
Target Candidate: Samya Jain (Jabalpur)
Participant ID: 132155 | City ID: 1693 | Season ID: 1684
"""

import sys
import json
import urllib.request
import urllib.error
import time

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

def make_request(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}/{endpoint}"
    req_headers = HEADERS.copy()
    if token:
        req_headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            return json.loads(err_body)
        except Exception:
            return {"status": 0, "message": f"HTTP Error {e.code}: {e.reason}"}
    except Exception as e:
        return {"status": 0, "message": f"Network Error: {str(e)}"}

def get_current_votes():
    """Fetch current vote count for Samya Jain"""
    res = make_request(f"entries-list/?cityID={CITY_ID}")
    if res.get("status") == 1 and "payload" in res:
        for entry in res["payload"]:
            if entry.get("participantID") == TARGET_PARTICIPANT_ID:
                return entry.get("totalVotes", "N/A")
    return "Unknown"

def send_otp(phone):
    """Step 1: Request OTP for the phone number"""
    payload = {
        "phone": phone.strip(),
        "forParticipation": False
    }
    return make_request("login-via-otp", method="POST", data=payload)

def verify_otp(otp, access_token, initial_token, phone):
    """Step 2: Verify OTP"""
    payload = {
        "otp": otp.strip(),
        "accessToken": access_token,
        "phone": phone.strip(),
        "cityID": CITY_ID
    }
    return make_request("verify-otp", method="POST", data=payload, token=initial_token)

def register_voter(full_name, email, token):
    """Step 3: Register as a voter if needed"""
    payload = {
        "fullName": full_name.strip(),
        "email": email.strip()
    }
    return make_request("register/voter", method="POST", data=payload, token=token)

def cast_vote(participant_id, token):
    """Step 4: Cast Vote"""
    return make_request(f"vote/{participant_id}", method="POST", token=token)

import random

def run_single_vote(phone, name=None, email=None):
    rand_id = random.randint(1000, 9999)
    if not name:
        name = f"Voter {rand_id}"
    if not email:
        email = f"voter{phone[-4:] if len(phone)>=4 else rand_id}_{rand_id}@gmail.com"

    print("\n" + "="*50)
    print(f"🎯 Target Candidate: {TARGET_NAME} (ID: {TARGET_PARTICIPANT_ID})")
    print(f"📊 Current Votes: {get_current_votes()}")
    print("="*50)
    
    # 1. Send OTP
    print(f"\n[1/4] 🚀 Sending OTP to {phone}...")
    otp_resp = send_otp(phone)
    if not otp_resp.get("status"):
        print(f"❌ Failed to send OTP: {otp_resp.get('message', 'Unknown error')}")
        return False
    
    print(f"✅ {otp_resp.get('message', 'OTP sent successfully!')}")
    access_token = otp_resp.get("payload", {}).get("accessToken")
    initial_token = otp_resp.get("payload", {}).get("token")
    
    # 2. Ask user for OTP
    otp = input("\n🔑 Enter the 6-digit OTP received on mobile/SMS: ").strip()
    if not otp:
        print("❌ OTP cannot be empty.")
        return False
    
    print("\n[2/4] ⚡ Verifying OTP...")
    t0 = time.time()
    verify_resp = verify_otp(otp, access_token, initial_token, phone)
    
    if not verify_resp.get("status"):
        print(f"❌ OTP verification failed: {verify_resp.get('message', 'Invalid OTP')}")
        return False
    
    user_token = verify_resp.get("payload", {}).get("token") or initial_token
    next_screen = verify_resp.get("payload", {}).get("nextScreen")
    print(f"✅ OTP Verified in {time.time()-t0:.2f}s! Status: {verify_resp.get('message', 'Success')}")
    
    # 3. Register voter if not already registered
    if next_screen in ["voter-signup", "register"] or not user_token:
        print(f"\n[3/4] 📝 Auto-registering voter ({name} / {email})...")
        reg_resp = register_voter(name, email, user_token)
        if reg_resp.get("status"):
            user_token = reg_resp.get("payload", {}).get("token") or user_token
            print(f"✅ Voter registered successfully!")
        else:
            print(f"ℹ️ Note on registration: {reg_resp.get('message', 'Proceeding with vote')}")
    else:
        print(f"\n[3/4] ⏩ Voter already registered. Skipping profile setup.")

    # 4. Cast Vote
    print(f"\n[4/4] 🗳️ Casting vote for {TARGET_NAME}...")
    t0 = time.time()
    vote_resp = cast_vote(TARGET_PARTICIPANT_ID, user_token)
    
    if vote_resp.get("status"):
        print(f"🎉 SUCCESS! {vote_resp.get('message', 'Vote registered successfully!')} (took {time.time()-t0:.2f}s)")
        print(f"📈 New Total Votes for {TARGET_NAME}: {get_current_votes()}")
        return True
    else:
        print(f"⚠️ Vote Response: {vote_resp.get('message', 'Failed to vote')}")
        return False

def main():
    print("=" * 60)
    print("  COLLEGE KE TASHANBAAZ - HIGH-SPEED VOTE AUTOMATION")
    print(f"  Candidate: {TARGET_NAME} (Singing solo, Jabalpur)")
    print("=" * 60)
    
    while True:
        phone = input("\n📱 Enter 10-digit Phone Number (or 'q' to quit): ").strip()
        if phone.lower() == 'q' or not phone:
            print("Exiting.")
            break
            
        run_single_vote(phone)
        
        again = input("\n🔁 Do you want to cast another vote with another number? (y/n): ").strip().lower()
        if again != 'y':
            print("\nDone! Thank you.")
            break

if __name__ == "__main__":
    main()

