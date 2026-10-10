const CLOUD_DB_ID = "ff808181a09d98f701a12556a82f34d5";
const CLOUD_DB_URL = `https://api.restful-api.dev/objects/${CLOUD_DB_ID}`;

let inMemoryStore = {
  totalVotes: 0,
  phoneVotes: {},
  history: []
};

async function getStats() {
  try {
    const res = await fetch(CLOUD_DB_URL, {
      headers: { "Accept": "application/json", "User-Agent": "Mozilla/5.0" },
      cache: "no-store"
    });
    if (res.ok) {
      const json = await res.json();
      if (json && json.data) {
        inMemoryStore = {
          totalVotes: json.data.totalVotes || 0,
          phoneVotes: json.data.phoneVotes || {},
          history: Array.isArray(json.data.history) ? json.data.history : []
        };
      }
    }
  } catch (e) {
    console.error("Cloud DB read error:", e.message);
  }
  return inMemoryStore;
}

async function recordVote(phone, status = "Success", message = "") {
  const cleanPhone = (phone || "Unknown").toString().trim();
  
  // 1. Fetch latest state
  await getStats();
  
  if (!inMemoryStore.phoneVotes[cleanPhone]) {
    inMemoryStore.phoneVotes[cleanPhone] = { count: 0, lastVoted: null };
  }
  
  if (status === "Success" || status === "success") {
    inMemoryStore.totalVotes += 1;
    inMemoryStore.phoneVotes[cleanPhone].count += 1;
  }
  
  const timestamp = new Date().toISOString();
  inMemoryStore.phoneVotes[cleanPhone].lastVoted = timestamp;
  
  inMemoryStore.history.unshift({
    phone: cleanPhone,
    timestamp,
    status,
    message
  });
  
  if (inMemoryStore.history.length > 300) {
    inMemoryStore.history = inMemoryStore.history.slice(0, 300);
  }
  
  // 2. Persist to Cloud DB
  try {
    await fetch(CLOUD_DB_URL, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
      },
      body: JSON.stringify({
        name: "samya_jain_vote_portal_db_v1",
        data: inMemoryStore
      })
    });
  } catch (e) {
    console.error("Cloud DB write error:", e.message);
  }
  
  return inMemoryStore;
}

module.exports = { recordVote, getStats };
