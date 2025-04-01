"use client";

import React from 'react';
import { type LeaderboardEntry } from '@/lib/db';

interface LeaderboardTableProps {
  entries: LeaderboardEntry[];
}

export default function LeaderboardTable({ entries }: LeaderboardTableProps) {
  // Format date to show in a readable format with milliseconds
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
  };

  // Format profit with 2 decimal places and a + sign if positive
  const formatProfit = (profit: number) => {
    return profit >= 0
      ? `+$${profit.toFixed(2)}`
      : `-$${Math.abs(profit.toFixed(2))}`;
  };

  // Format profit with 2 decimal places and a + sign if positive
  const formatPoints = (points: number) => {
    return `${points.toFixed(0)}`;
  };

  return (
    <div className="overflow-x-auto w-full rounded-lg shadow-xl">
      <div className="bg-nova-gray4/70 backdrop-blur-sm border border-nova-gray5 rounded-lg">
        <table className="w-full text-white border-collapse">
          <thead>
            <tr className="border-b border-nova-gray5/80 backdrop-blur-sm">
              <th className="py-5 px-6 text-left font-light text-lg text-nova-light">Position</th>
              <th className="py-5 px-6 text-left font-light text-lg text-nova-light">Team Name</th>
              <th className="py-5 px-6 text-right font-light text-lg text-nova-light">Points</th>
              <th className="py-5 px-6 text-right font-light text-lg text-nova-light">Profit</th>
              <th className="py-5 px-6 text-right font-light text-lg text-nova-light">Last Submission</th>
            </tr>
          </thead>
          <tbody>
            {entries.length > 0 ? (
              entries.map((entry) => (
                <tr
                  key={entry.team_name}
                  className="border-b border-nova-gray5/50 hover:bg-nova-gray4/90 transition-all duration-200"
                >
                  <td className="py-4 px-6 text-left font-semibold">{entry.position}</td>
                  <td className="py-4 px-6 text-left">{entry.team_name}</td>
                  <td className="py-4 px-6 text-right font-mono">{formatPoints(entry.points)}</td>
                  <td className={`py-4 px-6 text-right font-mono ${entry.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {formatProfit(entry.profit)}
                  </td>
                  <td className="py-4 px-6 text-right font-mono text-sm text-gray-300">
                    {formatDate(entry.last_submission_time)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="py-8 text-center text-nova-gray2">
                  No leaderboard data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
