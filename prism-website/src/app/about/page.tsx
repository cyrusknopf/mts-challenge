"use client";

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Logo from '@/components/ui/Logo';
import AnimatedButton from '@/components/ui/AnimatedButton';
import Link from 'next/link';
import { FaInstagram, FaLinkedin } from 'react-icons/fa';

export default function AboutPage() {
  return (
    <MainLayout>
      <div className="flex flex-col h-screen">
        {/* Header with Logo */}
        <header className="py-4">
          <div className="flex justify-center">
            <Logo variant="full" />
          </div>
        </header>


        <main className="flex-grow flex justify-center items-center px-4">
          <div
            className="
      w-full
      max-w-5xl
      bg-nova-gray4/80
      backdrop-blur-sm
      border
      border-nova-gray5
      rounded-lg
      shadow-2xl
      overflow-y-auto
      p-8
      custom-scrollbar
      content-center
    "
            style={{ maxHeight: '70vh' }}
          >
            <h1 className="text-4xl font-light mb-8 text-center">
              Competition Instructions
            </h1>

            <section className="mb-12">
              <h3 className="text-xl border-t mb-4 pt-4 text-center">About Us</h3>
              <div className="mt-4 flex space-x-4 justify-center">
                <Link href="https://www.instagram.com/manchestertradingsociety" target="_blank">
                  <FaInstagram className="text-2xl text-white hover:text-gray-300" />
                </Link>
                <Link href="https://www.linkedin.com/company/manchester-trading-society" target="_blank">
                  <FaLinkedin className="text-2xl text-white hover:text-gray-300" />
                </Link>
              </div>
              <div className="mb-4">
                <h4 className="text-xl mb-2">Manchester Trading Society</h4>
                <ul className="list-none ml-4 space-y-2">
                  <li>🏆 Top trading society at the University of Manchester (610+ LinkedIn | 430+ Instagram).</li>
                  <li>💡 By traders, for traders: learn, collaborate, and grow.</li>
                  <li>📚 Gain skills through workshops, idea-sharing, and real-world projects.</li>
                  <li>🤝 Join a thriving network of passionate traders and investors.</li>
                  <li>🚀 Elevate your trading journey with us!</li>
                </ul>
              </div>
            </section>

            <section className="mb-12">
              <h3 className="text-xl border-t mb-4 pt-4 text-center">Background & Challenge Overview</h3>

              <h4 className="text-lg font-semibold mb-2">Your Role as Portfolio Manager</h4>
              <p className="mb-4">
                As a portfolio manager for retail investors, you will receive various details and investment contexts from each investor, including budget, investment period, and miscellaneous personal information. Your job is to interpret these details carefully and accurately.
              </p>

              <h4 className="text-lg font-semibold mb-2">The Core Task</h4>
              <p className="mb-4">
                Using the information provided, you must generate a tailored portfolio consisting exclusively of US equities and specify the exact quantity of shares to purchase. Portfolios will be rigorously evaluated against each investor’s specific risk profile derived from the provided details.
              </p>

              <h4 className="text-lg font-semibold mb-2">Evaluation Criteria</h4>
              <p className="mb-4">
                Your submissions will be ranked first by the points you score, then by the profit your portfolio generates, and finally by the speed of your response. Retail investors are notably impatient, requiring answers rapidly—typically within 10 seconds, though this can vary throughout the day. Manual solutions are not advised 😉.
              </p>

              <p className="mb-4 font-semibold text-center">
                Best of luck building your own money-printing machine! 💸🚀
              </p>
            </section>

            <section className="mb-12">
              <h3 className="text-xl border-t mb-4 pt-4 text-center">Technical Details</h3>

              <h4 className="text-lg font-semibold mb-2">Service Connection</h4>
              <ul className="list-none ml-4 space-y-1 mb-4">
                <li><strong>Connect to </strong> http://mts-prism.com:PORT </li>
                <li><strong>Port 80:</strong> Competition information website</li>
                <li><strong>Port 8082:</strong> Main server for API interactions</li>
              </ul>

              <h4 className="text-lg font-semibold mb-2">API Endpoints</h4>
              <ul className="list-none ml-4 space-y-1 mb-4">
                <li><strong>GET /request:</strong> Obtain investor context details.</li>
                <li><strong>POST /submit:</strong> Submit your portfolio solution.</li>
              </ul>

              <h4 className="text-lg font-semibold mb-2">Portfolio Submission Format</h4>
              <pre className="bg-gray-800 text-white p-4 rounded mb-4 overflow-x-auto">
                {`[{"ticker": "AAPL", "quantity": 1}, {"ticker": "MSFT", "quantity": 10}]`}
              </pre>

              <h4 className="text-lg font-semibold mb-2">Submission Headers</h4>
              <p className="mb-4">
                Include this header with your API submissions:
                <code className="bg-gray-800 text-white p-1 rounded ml-2">X-API-Code: &lt;your-api-token&gt;</code>
                <br />If you do not have an API token, please contact the event administrators.
              </p>

              <h4 className="text-lg font-semibold mb-2">Penalties</h4>
              <ul className="list-disc ml-8 space-y-1 mb-4">
                <li>Submitting duplicate tickers within the same request.</li>
                <li>Exceeding the specified budget.</li>
                <li>Selecting stocks that are not recognized.</li>
              </ul>

            </section>
          </div>
        </main>

        {/* Footer with Go Back Button */}
        <footer className="py-4">
          <div className="flex justify-center">
            <AnimatedButton href="/">
              go back
            </AnimatedButton>
          </div>
        </footer>
      </div>
    </MainLayout>
  );
}

