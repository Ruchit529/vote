const { getStats } = require('./_db');

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0");
  res.setHeader("Pragma", "no-cache");
  res.setHeader("Expires", "0");

  try {
    const stats = await getStats();
    return res.status(200).json({
      success: true,
      totalVotesCast: stats.totalVotes || 0,
      phoneVotes: stats.phoneVotes || {},
      history: stats.history || []
    });
  } catch (error) {
    return res.status(500).json({ success: false, message: error.message });
  }
}
