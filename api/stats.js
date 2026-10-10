const BASE_URL = "https://api.collegeketashanbaaz.in/v1";
const SEASON_ID = "1684";
const CITY_ID = 1693; // Jabalpur
const TARGET_PARTICIPANT_ID = 132155; // Samya Jain
const TARGET_NAME = "Samya Jain";

const HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
  "Content-Type": "application/json",
  "Accept": "application/json, text/plain, */*",
  "seasonID": SEASON_ID,
  "Origin": "https://collegeketashanbaaz.in",
  "Referer": "https://collegeketashanbaaz.in/shortlisted"
};

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0");
  res.setHeader("Pragma", "no-cache");
  res.setHeader("Expires", "0");

  try {
    const response = await fetch(`${BASE_URL}/entries-list/?cityID=${CITY_ID}`, {
      headers: HEADERS,
      cache: "no-store"
    });
    const data = await response.json();
    let votes = "N/A";
    if (data.status === 1 && Array.isArray(data.payload)) {
      const candidate = data.payload.find(e => e.participantID === TARGET_PARTICIPANT_ID);
      if (candidate) {
        votes = candidate.totalVotes;
      }
    }
    return res.status(200).json({
      candidate: TARGET_NAME,
      participantID: TARGET_PARTICIPANT_ID,
      votes,
      timestamp: Date.now()
    });
  } catch (error) {
    return res.status(500).json({ candidate: TARGET_NAME, votes: "N/A", error: error.message });
  }
}
