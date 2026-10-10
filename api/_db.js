const fs = require('fs');
const path = require('path');

const DB_FILE = path.join('/tmp', 'vote_counter_db.json');

let inMemoryStore = {
  totalVotes: 0,
  phoneVotes: {},
  history: []
};

function loadDb() {
  try {
    if (fs.existsSync(DB_FILE)) {
      const content = fs.readFileSync(DB_FILE, 'utf8');
      const data = JSON.parse(content);
      inMemoryStore = { ...inMemoryStore, ...data };
    }
  } catch (e) {
    console.error("Failed to load db:", e.message);
  }
  return inMemoryStore;
}

function recordVote(phone, status = "Success", message = "") {
  loadDb();
  const cleanPhone = (phone || "Unknown").toString().trim();
  
  if (!inMemoryStore.phoneVotes[cleanPhone]) {
    inMemoryStore.phoneVotes[cleanPhone] = { count: 0, lastVoted: null };
  }
  
  if (status === "Success") {
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
  
  if (inMemoryStore.history.length > 500) {
    inMemoryStore.history = inMemoryStore.history.slice(0, 500);
  }
  
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(inMemoryStore, null, 2), 'utf8');
  } catch (e) {
    console.error("Failed to write db:", e.message);
  }
  
  return inMemoryStore;
}

function getStats() {
  return loadDb();
}

module.exports = { recordVote, getStats };
