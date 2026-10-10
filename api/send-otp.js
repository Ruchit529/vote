const BASE_URL = "https://api.collegeketashanbaaz.in/v1";
const SEASON_ID = "1684";

const HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
  "Content-Type": "application/json",
  "Accept": "application/json, text/plain, */*",
  "seasonID": SEASON_ID,
  "Origin": "https://collegeketashanbaaz.in",
  "Referer": "https://collegeketashanbaaz.in/shortlisted"
};

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, no-cache, must-revalidate");

  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  try {
    const { phone } = req.body || {};
    if (!phone) {
      return res.status(400).json({ status: 0, message: "Phone number is required" });
    }

    const response = await fetch(`${BASE_URL}/login-via-otp`, {
      method: "POST",
      headers: HEADERS,
      body: JSON.stringify({
        phone: phone.toString().trim(),
        forParticipation: false
      })
    });

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ status: 0, message: error.message });
  }
}
