const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');

  try {
    const htmlPath = path.join(process.cwd(), 'public', 'admin.html');
    if (fs.existsSync(htmlPath)) {
      const htmlContent = fs.readFileSync(htmlPath, 'utf8');
      return res.status(200).send(htmlContent);
    }
  } catch (e) {
    console.error("Error reading admin.html:", e);
  }

  return res.status(200).send("<html><body><h2>Loading Admin...</h2><script>location.reload()</script></body></html>");
}
