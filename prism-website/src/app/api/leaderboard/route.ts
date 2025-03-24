import { NextRequest, NextResponse } from 'next/server';
import { Pool } from 'pg';
import { LeaderboardEntry } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const { user, password, host, port, database } = await request.json();

    // Validate all required parameters are present
    if (!host || !database || !user) {
      return NextResponse.json(
        { error: 'Missing required database configuration parameters' },
        { status: 400 }
      );
    }

    // Create a new pool with the provided config
    const pool = new Pool({
      user,
      password,
      host,
      port: port ? parseInt(port) : 5432,
      database,
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
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
