"use client";

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Logo from '@/components/ui/Logo';
import AnimatedButton from '@/components/ui/AnimatedButton';
import LeaderboardTable from '@/components/ui/LeaderboardTable';
import { LeaderboardEntry } from '@/lib/db';
import { generateMockLeaderboardData } from '@/lib/mockData';

export default function LeaderboardPage() {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // Auto-refresh function
  const loadMockData = () => {
    setIsLoading(true);
    setError(null);

    // Simulate API delay
    setTimeout(() => {
      const mockData = generateMockLeaderboardData();

      // Process data to add positions (calculated by the frontend instead of database)
      const processedData = [...mockData].sort((a, b) =>
        b.points - a.points || b.profit - a.profit
      ).map((entry, index) => ({
        ...entry,
        position: index + 1
      }));

      setLeaderboardData(processedData);
      setLastUpdated(new Date());
      setIsLoading(false);
    }, 800);
  };

  // Setup auto-refresh and initial data load
  useEffect(() => {
    // Initial data load
    loadMockData();

    // Set up 30-second interval for auto-refresh
    const interval = setInterval(() => {
      loadMockData();
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
    loadMockData();
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
