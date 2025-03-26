import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';
import { LeaderboardEntry } from '@/lib/db';

export async function POST() {
  try {

    // Create a new pool with the provided config
    const pool = new Pool({
      user: 'postgres',
      password: 'l??pT-87pBqE2hN9-zY/)',
      host: 'postgresql',
      port: 5432,
      database: 'prism',
      ssl: false,
      // Short connection timeout to prevent hanging
      connectionTimeoutMillis: 5000,
    });

    try {
      // Test the connection
      await pool.query('SELECT NOW()');

      // Query the leaderboard data
      const result = await pool.query(`
        SELECT
          ROW_NUMBER() OVER (ORDER BY points DESC, profit DESC) as position,
          team_name,
          points,
          profit,
          last_submission_time
        FROM leaderboard_entries
        ORDER BY points DESC, profit DESC
        LIMIT 10
      `);

      // End the pool to avoid connection leaks
      await pool.end();

      return NextResponse.json(result.rows as LeaderboardEntry[]);
    } catch (error) {
      // Make sure to end the pool on error
      await pool.end();
      console.error('Database query error:', error);

      return NextResponse.json(
        { error: 'Error connecting to database or executing query' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
