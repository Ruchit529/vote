const ADMIN_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin Dashboard - Voting Counter</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { background: #080c14; color: #f3f4f6; min-height: 100vh; padding: 30px 20px; }
  .container { max-width: 960px; margin: 0 auto; }
  
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
  .header h1 { font-size: 24px; font-weight: 800; color: #ffffff; }
  .badge { background: linear-gradient(135deg, #ec4899, #8b5cf6); color: white; padding: 4px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; }

  .actions { display: flex; gap: 8px; flex-wrap: wrap; }
  .btn-action { background: #1e293b; border: 1px solid #334155; color: #38bdf8; padding: 8px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
  .btn-action:hover { background: #334155; }
  .btn-danger { color: #f87171; border-color: #7f1d1d; }
  .btn-danger:hover { background: #450a0a; }

  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .stat-card { background: #111827; border: 1px solid #1f293d; border-radius: 14px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
  .stat-title { font-size: 13px; color: #94a3b8; margin-bottom: 8px; font-weight: 500; }
  .stat-value { font-size: 32px; font-weight: 800; color: #38bdf8; }
  .stat-sub { font-size: 12px; color: #64748b; margin-top: 4px; }

  .section-title { font-size: 17px; font-weight: 700; margin-bottom: 12px; color: #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
  
  .table-card { background: #111827; border: 1px solid #1f293d; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.4); margin-bottom: 28px; }
  table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
  th { background: #1e293b; color: #94a3b8; font-weight: 600; padding: 12px 16px; border-bottom: 1px solid #334155; }
  td { padding: 12px 16px; border-bottom: 1px solid #1f293d; color: #cbd5e1; }
  tr:last-child td { border-bottom: none; }
  tr:hover { background: #162032; }

  .status-tag { padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; display: inline-block; }
  .status-success { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
  .status-failed { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }

  .empty-state { padding: 36px; text-align: center; color: #64748b; font-size: 14px; }
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <div>
      <div class="badge">Live Admin Center</div>
      <h1>Platform Vote Counter & Mobile Logs</h1>
    </div>
    <div class="actions">
      <button class="btn-action" onclick="copyNumbers()">📋 Copy Numbers</button>
      <button class="btn-action" onclick="exportCSV()">📥 Export CSV</button>
      <button class="btn-action" onclick="loadAdminStats()">🔄 Refresh</button>
      <button class="btn-action btn-danger" onclick="clearLogs()">🗑️ Clear Logs</button>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-title">Votes Cast via This Platform</div>
      <div class="stat-value" id="platformVotes" style="color: #ec4899;">0</div>
      <div class="stat-sub">Tracked from direct submissions</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">Unique Mobile Numbers</div>
      <div class="stat-value" id="uniqueNumbers" style="color: #8b5cf6;">0</div>
      <div class="stat-sub">Distinct numbers voted</div>
    </div>
    <div class="stat-card">
      <div class="stat-title">Live Candidate Votes</div>
      <div class="stat-value" id="liveCandidateVotes">...</div>
      <div class="stat-sub">Official count for Samya Jain</div>
    </div>
  </div>

  <div class="section-title">
    <span>📱 Mobile Numbers Summary</span>
  </div>
  <div class="table-card">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Mobile Number</th>
          <th>Votes Completed</th>
          <th>Last Voted Time</th>
        </tr>
      </thead>
      <tbody id="summaryTableBody">
        <tr><td colspan="4" class="empty-state">No voting activity logged yet.</td></tr>
      </tbody>
    </table>
  </div>

  <div class="section-title">
    <span>📜 Detailed Activity Timeline</span>
  </div>
  <div class="table-card">
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Mobile Number</th>
          <th>Status</th>
          <th>API Message</th>
        </tr>
      </thead>
      <tbody id="logTableBody">
        <tr><td colspan="4" class="empty-state">No activity logged yet.</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script>
let cachedNumbers = [];

async function loadAdminStats() {
  // 1. Fetch Official Live Candidate Total
  try {
    const statsRes = await fetch('/api/stats?_t=' + Date.now(), { cache: 'no-store' });
    const statsData = await statsRes.json();
    if (statsData && statsData.votes !== undefined) {
      document.getElementById('liveCandidateVotes').innerText = statsData.votes;
    }
  } catch(e){}

  // 2. Fetch local client logs
  let localLogs = [];
  try {
    localLogs = JSON.parse(localStorage.getItem('vote_samya_admin_logs') || '[]');
  } catch(e){}

  // 3. Fetch server logs
  let serverLogs = [];
  try {
    const sRes = await fetch('/api/admin-stats?_t=' + Date.now(), { cache: 'no-store' });
    const sData = await sRes.json();
    if (sData && sData.history) {
      serverLogs = sData.history;
    }
  } catch(e){}

  // 4. Merge logs & deduplicate
  const allLogs = [...localLogs, ...serverLogs];
  const uniqueLogsMap = new Map();
  allLogs.forEach(item => {
    if (!item.phone) return;
    const key = item.phone.trim() + '_' + (item.timestamp ? item.timestamp.slice(0, 16) : '');
    if (!uniqueLogsMap.has(key)) {
      uniqueLogsMap.set(key, item);
    }
  });

  const mergedLogs = Array.from(uniqueLogsMap.values());
  mergedLogs.sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0));

  // Compute stats per phone
  const phoneStats = {};
  let totalSuccessfulVotes = 0;

  mergedLogs.forEach(entry => {
    const p = entry.phone.trim();
    if (!phoneStats[p]) {
      phoneStats[p] = { count: 0, lastTime: entry.timestamp, status: entry.status };
    }
    if (entry.status === 'Success' || entry.status === 'success') {
      phoneStats[p].count += 1;
      totalSuccessfulVotes += 1;
    }
  });

  const phones = Object.keys(phoneStats);
  cachedNumbers = phones;
  document.getElementById('platformVotes').innerText = totalSuccessfulVotes;
  document.getElementById('uniqueNumbers').innerText = phones.length;

  // Render Summary Table
  const summaryBody = document.getElementById('summaryTableBody');
  if (phones.length === 0) {
    summaryBody.innerHTML = '<tr><td colspan="4" class="empty-state">No numbers recorded yet. Cast a vote on the main page to see logs here.</td></tr>';
  } else {
    let sHtml = '';
    phones.forEach((phone, idx) => {
      const item = phoneStats[phone];
      const timeStr = item.lastTime ? new Date(item.lastTime).toLocaleString() : '-';
      sHtml += \`
        <tr>
          <td style="color:#64748b;">\${idx + 1}</td>
          <td style="font-weight:700; color:#f8fafc; letter-spacing:0.5px;">\${phone}</td>
          <td><strong style="color:#ec4899;">\${item.count}</strong> vote(s)</td>
          <td style="color:#94a3b8; font-size:13px;">\${timeStr}</td>
        </tr>
      \`;
    });
    summaryBody.innerHTML = sHtml;
  }

  // Render Detailed Timeline
  const logBody = document.getElementById('logTableBody');
  if (mergedLogs.length === 0) {
    logBody.innerHTML = '<tr><td colspan="4" class="empty-state">No recent activity.</td></tr>';
  } else {
    let lHtml = '';
    mergedLogs.forEach(entry => {
      const isOk = entry.status === 'Success' || entry.status === 'success';
      const tagClass = isOk ? 'status-success' : 'status-failed';
      const timeStr = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : '-';
      lHtml += \`
        <tr>
          <td style="color:#94a3b8; font-size:13px;">\${timeStr}</td>
          <td style="font-weight:600;">\${entry.phone}</td>
          <td><span class="status-tag \${tagClass}">\${entry.status}</span></td>
          <td style="color:#cbd5e1; font-size:13px;">\${entry.message || '-'}</td>
        </tr>
      \`;
    });
    logBody.innerHTML = lHtml;
  }
}

function copyNumbers() {
  if (cachedNumbers.length === 0) {
    alert('No phone numbers recorded yet.');
    return;
  }
  navigator.clipboard.writeText(cachedNumbers.join('\\n')).then(() => {
    alert('✅ ' + cachedNumbers.length + ' phone number(s) copied to clipboard!');
  });
}

function exportCSV() {
  if (cachedNumbers.length === 0) {
    alert('No data to export.');
    return;
  }
  let csv = 'Index,Phone,Timestamp\\n';
  cachedNumbers.forEach((p, i) => {
    csv += (i + 1) + ',' + p + '\\n';
  });
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'votes_samya_' + Date.now() + '.csv';
  a.click();
}

function clearLogs() {
  if (confirm('Are you sure you want to clear locally saved logs?')) {
    localStorage.removeItem('vote_samya_admin_logs');
    loadAdminStats();
  }
}

loadAdminStats();
setInterval(loadAdminStats, 4000);
</script>
</body>
</html>`;

export default function handler(req, res) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
  return res.status(200).send(ADMIN_HTML);
}
