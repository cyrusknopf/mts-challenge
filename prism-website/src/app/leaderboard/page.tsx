"use client";

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Logo from '@/components/ui/Logo';
import AnimatedButton from '@/components/ui/AnimatedButton';
import LeaderboardTable from '@/components/ui/LeaderboardTable';
import { LeaderboardEntry } from '@/lib/db';
// Remove the import of POST from the API route
// import { POST } from '../api/leaderboard/route';

export default function LeaderboardPage() {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // This function makes a POST request to your API endpoint
  const loadData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Make a POST request to your API endpoint at /api/leaderboard.
      // Adjust the request body as needed (here we send an empty object).
      const res = await fetch('/api/leaderboard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });

      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      // Assume the API returns an array of leaderboard entries.
      const apiData: LeaderboardEntry[] = await res.json();
      // Map over each entry to parse position as int and profit as float.
      const parsedData: LeaderboardEntry[] = apiData.map((entry) => ({
        ...entry,
        // If entry.position exists as a string, convert it. Otherwise, leave undefined.
        position: entry.position !== undefined ? parseInt(String(entry.position), 10) : undefined,
        profit: parseFloat(String(entry.profit)),
        // Optionally, ensure points is a number too.
        points: Number(entry.points)
      }));

      setLeaderboardData(parsedData);
      setLastUpdated(new Date());
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Use useEffect to call loadData on mount and every 30 seconds
  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      loadData();
    }, 30000);

    setRefreshInterval(interval);

    // Clean up interval on component unmount
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, []);

  const refreshData = () => {
    loadData();
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 pt-16 md:pt-24">
        <div className="mb-8 flex justify-between items-center">
          <Logo variant="full" />
          <div className="text-sm text-nova-light">
            {lastUpdated && (
              <div className="flex items-center">
                <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
                <div className="ml-2 h-2 w-2 rounded-full bg-green-400 animate-pulse"></div>
                <span className="ml-2 text-xs text-gray-400">(Auto-refresh every 30s)</span>
              </div>
            )}
          </div>
        </div>

        <div className="mb-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-light">Trading Competition Leaderboard</h1>
            <div className="flex space-x-4">
              <AnimatedButton onClick={refreshData} className="w-auto px-4">
                Refresh
              </AnimatedButton>
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-900/50 border border-red-800 rounded-md text-white">
              {error}
            </div>
          )}

          <div className="mt-8">
            {isLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-pulse text-nova-light">Loading...</div>
              </div>
            ) : (
              <LeaderboardTable entries={leaderboardData} />
            )}
          </div>
        </div>

        <div className="mb-12">
          <AnimatedButton href="/" className="mb-16">
            go back
          </AnimatedButton>
        </div>
      </div>
    </MainLayout>
  );
}
