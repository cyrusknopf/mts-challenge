-- SQL Setup Script for PRISM Leaderboard
-- Execute this script to set up your database


-- Create a database (uncomment and modify if you need to create the database)
CREATE DATABASE teams;

-- Create the teams table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    api_key VARCHAR(100) NOT NULL UNIQUE,
    team_name VARCHAR(100) NOT NULL,
    points DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    profit DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    last_submission_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_leaderboard_entries_points_profit ON teams (points DESC, profit DESC);

-- Insert sample data (for testing purposes only)
INSERT INTO teams (team_name, api_key, points, profit, last_submission_time)
VALUES
    -- ('Alpha Traders', 'a', 950, 142.57, NOW() - INTERVAL '1 hour'),
    -- ('Quantum Capital', 'b', 920, 128.32, NOW() - INTERVAL '2 hours'),
    -- ('Nebula Investments', 'c', 880, 98.45, NOW() - INTERVAL '30 minutes'),
    -- ('Horizon Quants', 'd', 850, 75.18, NOW() - INTERVAL '15 minutes'),
    -- ('Stellar Algo', 'e', 830, 62.79, NOW() - INTERVAL '45 minutes'),
    -- ('Fusion Trading', 'f', 790, -12.34, NOW() - INTERVAL '1 day'),
    -- ('Apex Quants', 'g', 720, 45.60, NOW() - INTERVAL '3 hours'),
    -- ('Matrix Strategy', 'h', 680, 18.25, NOW() - INTERVAL '5 hours'),
    -- ('Velocity Capital', 'i',650, -24.50, NOW() - INTERVAL '2 days'),
    -- ('Sigma Investments', 'j', 590, 5.12, NOW() - INTERVAL '4 hours'),
    ('Administrator', 'top 10 most glorious imperial rules', 1, 0, NOW() - INTERVAL '9 hours');

-- FIXME: get it compatible with this
-- ON CONFLICT (team_name) DO UPDATE
-- SET
--     points = EXCLUDED.points,
--     profit = EXCLUDED.profit,
--     last_submission_time = EXCLUDED.last_submission_time;

-- Add a stored procedure to update or insert a team's data
CREATE OR REPLACE FUNCTION update_leaderboard (
    p_team_name VARCHAR(100),
    p_points INTEGER,
    p_profit DECIMAL(15, 2)
) RETURNS VOID AS $$
BEGIN
    INSERT INTO teams (team_name, points, profit, last_submission_time)
    VALUES (p_team_name, p_points, p_profit, CURRENT_TIMESTAMP)
    ON CONFLICT (team_name) DO UPDATE
    SET
        points = EXCLUDED.points,
        profit = EXCLUDED.profit,
        last_submission_time = EXCLUDED.last_submission_time;
END;
$$ LANGUAGE plpgsql;
