import { Pool } from 'pg';

// Create a connection pool
const pool = new Pool({
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  host: process.env.POSTGRES_HOST,
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  database: process.env.POSTGRES_DB,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Function to query the database
export async function query(text: string, params: any[] = []) {
  try {
    const start = Date.now();
    const result = await pool.query(text, params);
    const duration = Date.now() - start;
    console.log('Executed query', { text, duration, rows: result.rowCount });
    return result;
  } catch (error) {
    console.error('Error executing query:', error);
    throw error;
  }
}

// Define the leaderboard entry type
export interface LeaderboardEntry {
  position?: number; // Position is calculated on frontend, not stored in database
  team_name: string;
  points: number;
  profit: number;
  last_submission_time: string;
}

// Function to get leaderboard data
export async function getLeaderboard(): Promise<Omit<LeaderboardEntry, 'position'>[]> {
  try {
    const result = await query(`
      SELECT
        team_name,
        points,
        profit,
        last_submission_time
      FROM leaderboard_entries
      ORDER BY points DESC, profit DESC
      LIMIT 10
    `);

    return result.rows;
  } catch (error) {
    console.error('Error fetching leaderboard data:', error);
    return [];
  }
}
