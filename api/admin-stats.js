const { getStats } = require('./_db');

export default function handler(req, res) {
  try {
    const stats = getStats();
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
