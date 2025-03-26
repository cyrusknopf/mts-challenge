import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Logo from '@/components/ui/Logo';
import AnimatedButton from '@/components/ui/AnimatedButton';
import Link from 'next/link';

export default function CareersPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 pt-16 md:pt-24">
        <div className="mb-16">
          <Logo variant="full" />
        </div>

        <div className="mb-16">
          <h1 className="text-4xl font-light mb-8">Join us in our mission to build a leader in systematic trading</h1>

          <Link
            href="https://sg.linkedin.com/company/nova-prospect-ltd"
            target="_blank"
            className="text-white underline hover:text-gray-300"
          >
            Linkedin
          </Link>
        </div>

        <div className="mb-24">
          <h3 className="text-xl uppercase mb-10 mt-20 border-t pt-8">open positions</h3>

          <div className="mb-12">
            <h4 className="text-2xl mb-4">Quantitative Developer</h4>
            <div className="h-[1px] w-16 bg-white"></div>
          </div>

          <div className="mb-12">
            <h4 className="text-2xl mb-4">Quantitative Researcher</h4>
            <div className="h-[1px] w-16 bg-white"></div>
          </div>
        </div>

        <div className="mb-12">
          <AnimatedButton href="/" className="mb-16">
            go back
          </AnimatedButton>
        </div>

        <div className="mb-32">
          <h2 className="text-3xl mb-6">privacy policy</h2>

          <div className="text-lg space-y-6 max-w-3xl">
            <h3 className="text-xl font-bold">Information We Collect</h3>
            <p>
              Nova Prospects Privacy Policy (Policy) informs you about privacy practices of Nova Prospect, including those related to our website https://www.novaprospect.com (Site). Nova Prospect respects your privacy and this Policy provides you with information about how we use your personal information and the privacy choices you have regarding your personal information.
            </p>
            <p>
              Nova Prospect may collect and store, or have third parties collect and store, personal information provided through the Site. This information includes but is not limited to: contact information (like your name, email address, phone numbers); information automatically collected from the devices you use to connect to the Site; demographics like birthdate and zip code; comments, creative assets, portfolio information, resumes and other content you upload or submit to the Site when you apply for a job (collectively, Personal Information).
            </p>

            <h3 className="text-xl font-bold mt-8">How We Use Data</h3>
            <p>We may use your Personal Information as follows:</p>
            <ul className="list-disc list-inside space-y-2 pl-4">
              <li>To provide information you request based on your consent, which you can withdraw at any time;</li>
              <li>To allow you to better use the Site, based on Nova Prospects legitimate interest in providing the best experience to you and to provide information regarding use of the Site;</li>
              <li>To view and act on your job application, based on our legitimate interest in reviewing your application, and communicating with you about the process;</li>
              <li>To allow you to submit materials, comments and assets to the Site, based on your consent, which you can withdraw at any time; and</li>
              <li>To comply with our policies and applicable law.</li>
            </ul>
            <p>
              We may also combine your Personal Information in an aggregated manner which is no longer personally identifiable to use for Nova Prospects own legitimate business purposes.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
