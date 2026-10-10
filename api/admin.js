const fs = require('fs');
const path = require('path');

const ADMIN_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Dashboard - Voting Counter</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { background: #080c14; color: #f3f4f6; min-height: 100vh; padding: 30px 20px; }
  .container { max-width: 900px; margin: 0 auto; }
  
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
  .header h1 { font-size: 24px; font-weight: 800; color: #ffffff; }
  .badge { background: linear-gradient(135deg, #ec4899, #8b5cf6); color: white; padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; }

  .btn-refresh { background: #1e293b; border: 1px solid #334155; color: #38bdf8; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
  .btn-refresh:hover { background: #334155; }

  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .stat-card { background: #111827; border: 1px solid #1f293d; border-radius: 14px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
  .stat-title { font-size: 13px; color: #94a3b8; margin-bottom: 8px; font-weight: 500; }
  .stat-value { font-size: 32px; font-weight: 800; color: #38bdf8; }
  .stat-sub { font-size: 12px; color: #64748b; margin-top: 4px; }

  .section-title { font-size: 18px; font-weight: 700; margin-bottom: 14px; color: #e2e8f0; }
  
  .table-card { background: #111827; border: 1px solid #1f293d; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
  table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
  th { background: #1e293b; color: #94a3b8; font-weight: 600; padding: 14px 18px; border-bottom: 1px solid #334155; }
  td { padding: 14px 18px; border-bottom: 1px solid #1f293d; color: #cbd5e1; }
  tr:last-child td { border-bottom: none; }
  tr:hover { background: #162032; }

  .status-tag { padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; display: inline-block; }
  .status-success { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
  .status-failed { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }

  .empty-state { padding: 40px; text-align: center; color: #64748b; font-size: 14px; }
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <div>
      <div class="badge">Backend Analytics</div>
      <h1>Platform Vote Counter & Logs</h1>
    </div>
    <button class="btn-refresh" onclick="loadAdminStats()">🔄 Refresh Data</button>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-title">Votes Cast via This Platform</div>
      <div class="stat-value" id="platformVotes" style="color: #ec4899;">0</div>
      <div class="stat-sub">Tracked from backend server</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">Unique Mobile Numbers</div>
      <div class="stat-value" id="uniqueNumbers" style="color: #8b5cf6;">0</div>
      <div class="stat-sub">Distinct phones used</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">Live Candidate Votes</div>
      <div class="stat-value" id="liveCandidateVotes">...</div>
      <div class="stat-sub">Official count for Samya Jain</div>
    </div>
  </div>

  <div class="section-title">📱 Phone Number Summary</div>
  <div class="table-card" style="margin-bottom: 30px;">
    <table>
      <thead>
        <tr>
          <th>Mobile Number</th>
          <th>Votes Cast</th>
          <th>Last Voted Time</th>
        </tr>
      </thead>
      <tbody id="summaryTableBody">
        <tr><td colspan="3" class="empty-state">Loading phone summary...</td></tr>
      </tbody>
    </table>
  </div>

  <div class="section-title">📜 Detailed Activity Log</div>
  <div class="table-card">
    <table>
      <thead>
        <tr>
          <th>Mobile Number</th>
          <th>Status</th>
          <th>Timestamp</th>
          <th>Message / Note</th>
        </tr>
      </thead>
      <tbody id="logTableBody">
        <tr><td colspan="4" class="empty-state">Loading vote activity...</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script>
async function loadAdminStats() {
  try {
    const res = await fetch('/api/admin-stats');
    const data = await res.json();
    
    try {
      const statsRes = await fetch('/api/stats');
      const statsData = await statsRes.json();
      document.getElementById('liveCandidateVotes').innerText = statsData.votes || 'N/A';
    } catch(e){}

    if (!data.success) return;

    document.getElementById('platformVotes').innerText = data.totalVotesCast || 0;

    const phoneVotes = data.phoneVotes || {};
    const phoneKeys = Object.keys(phoneVotes);
    document.getElementById('uniqueNumbers').innerText = phoneKeys.length;

    const summaryBody = document.getElementById('summaryTableBody');
    if (phoneKeys.length === 0) {
      summaryBody.innerHTML = '<tr><td colspan="3" class="empty-state">No votes recorded yet via this platform.</td></tr>';
    } else {
      let html = '';
      phoneKeys.forEach(phone => {
        const item = phoneVotes[phone];
        const lastTime = item.lastVoted ? new Date(item.lastVoted).toLocaleString() : 'N/A';
        html += \`
          <tr>
            <td style="font-weight:700; letter-spacing:0.5px;">\${phone}</td>
            <td><strong style="color:#ec4899;">\${item.count}</strong> vote(s)</td>
            <td style="color:#94a3b8; font-size:13px;">\${lastTime}</td>
          </tr>
        \`;
      });
      summaryBody.innerHTML = html;
    }

    const logBody = document.getElementById('logTableBody');
    const history = data.history || [];
    if (history.length === 0) {
      logBody.innerHTML = '<tr><td colspan="4" class="empty-state">No activity logged yet.</td></tr>';
    } else {
      let html = '';
      history.forEach(log => {
        const tagClass = log.status === 'Success' ? 'status-success' : 'status-failed';
        const formattedTime = new Date(log.timestamp).toLocaleString();
        html += \`
          <tr>
            <td style="font-weight:600;">\${log.phone}</td>
            <td><span class="status-tag \${tagClass}">\${log.status}</span></td>
            <td style="color:#94a3b8; font-size:13px;">\${formattedTime}</td>
            <td style="color:#cbd5e1; font-size:13px;">\${log.message || '-'}</td>
          </tr>
        \`;
      });
      logBody.innerHTML = html;
    }
  } catch(e) {
    console.error("Failed to fetch admin stats:", e);
  }
}

loadAdminStats();
setInterval(loadAdminStats, 5000);
</script>
</body>
</html>`;

export default function handler(req, res) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(200).send(ADMIN_HTML);
}
