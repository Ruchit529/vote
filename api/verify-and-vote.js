const BASE_URL = "https://api.collegeketashanbaaz.in/v1";
const SEASON_ID = "1684";
const CITY_ID = 1693; // Jabalpur
const TARGET_PARTICIPANT_ID = 132155; // Samya Jain
const { recordVote } = require('./_db');

const HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
  "Content-Type": "application/json",
  "Accept": "application/json, text/plain, */*",
  "seasonID": SEASON_ID,
  "Origin": "https://collegeketashanbaaz.in",
  "Referer": "https://collegeketashanbaaz.in/shortlisted"
};

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ success: false, message: "Method not allowed" });
  }

  try {
    const { otp, accessToken, initialToken, phone, fullName, email } = req.body || {};
    if (!otp || !phone) {
      return res.status(400).json({ success: false, message: "Missing required fields" });
    }

    // 1. Verify OTP
    const verifyHeaders = { ...HEADERS };
    if (initialToken) {
      verifyHeaders["Authorization"] = `Bearer ${initialToken}`;
    }

    const verifyResp = await fetch(`${BASE_URL}/verify-otp`, {
      method: "POST",
      headers: verifyHeaders,
      body: JSON.stringify({
        otp: otp.toString().trim(),
        accessToken,
        phone: phone.toString().trim(),
        cityID: CITY_ID
      })
    });

    const verifyData = await verifyResp.json();
    if (!verifyData || !verifyData.status) {
      const errMsg = (verifyData && verifyData.message) || "Invalid OTP";
      recordVote(phone, "Failed", errMsg);
      return res.status(200).json({
        success: false,
        message: errMsg
      });
    }

    let userToken = (verifyData.payload && verifyData.payload.token) || initialToken;
    const nextScreen = verifyData.payload && verifyData.payload.nextScreen;

    // 2. Register voter if new user
    if (nextScreen === "voter-signup" || nextScreen === "register") {
      const regHeaders = { ...HEADERS, Authorization: `Bearer ${userToken}` };
      const regResp = await fetch(`${BASE_URL}/register/voter`, {
        method: "POST",
        headers: regHeaders,
        body: JSON.stringify({
          fullName: (fullName || "Voter").trim(),
          email: (email || `voter${phone.toString().slice(-4)}@gmail.com`).trim()
        })
      });
      const regData = await regResp.json();
      if (regData && regData.status && regData.payload && regData.payload.token) {
        userToken = regData.payload.token;
      }
    }

    // 3. Cast Vote
    const voteHeaders = { ...HEADERS, Authorization: `Bearer ${userToken}` };
    const voteResp = await fetch(`${BASE_URL}/vote/${TARGET_PARTICIPANT_ID}`, {
      method: "POST",
      headers: voteHeaders
    });

    const voteData = await voteResp.json();
    if (voteData && voteData.status) {
      const successMsg = voteData.message || "Vote cast successfully!";
      recordVote(phone, "Success", successMsg);
      return res.status(200).json({
        success: true,
        message: successMsg
      });
    } else {
      const failMsg = (voteData && voteData.message) || "Vote could not be registered.";
      recordVote(phone, "Failed", failMsg);
      return res.status(200).json({
        success: false,
        message: failMsg
      });
    }
  } catch (error) {
    recordVote(req.body?.phone || "Unknown", "Error", error.message);
    return res.status(500).json({ success: false, message: error.message });
  }
}

