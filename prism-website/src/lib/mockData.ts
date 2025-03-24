import { LeaderboardEntry } from './db';

export const generateMockLeaderboardData = (): Omit<LeaderboardEntry, 'position'>[] => {
  const teamNames = ['Alpha Traders', 'Quantum Capital', 'Nebula Investments', 'Horizon Quants',
                    'Stellar Algo', 'Fusion Trading', 'Apex Quants', 'Matrix Strategy',
                    'Velocity Capital', 'Sigma Investments'];

  const now = new Date();

  return teamNames.map((name) => {
    // Generate random points between 500-1000
    const points = Math.floor(Math.random() * 500) + 500;

    // Generate random profit between -50 and +150
    const profit = (Math.random() * 200 - 50).toFixed(2);

    // Create a random timestamp within the last 24 hours
    const submissionTime = new Date(now.getTime() - Math.random() * 24 * 60 * 60 * 1000);

    return {
      team_name: name,
      points: points,
      profit: parseFloat(profit),
      last_submission_time: submissionTime.toISOString(),
    };
  });
};
