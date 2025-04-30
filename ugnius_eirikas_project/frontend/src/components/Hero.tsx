import React, { useState } from 'react';

const HeroSection = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className="bg-white">
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div
          className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
          aria-hidden="true"
        >
          <div
            className="relative left-1/2 w-full -translate-x-1/2 rotate-30 bg-gradient-to-tr from-pink-300 to-purple-400 opacity-30"
            style={{
              aspectRatio: '1155/678',
              clipPath:
                'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
            }}
          ></div>
        </div>

        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-5xl font-semibold tracking-tight text-gray-900 sm:text-7xl">
              Traffilyzer
            </h1>
            <p className="mt-8 text-lg font-medium text-gray-500 sm:text-xl">
              Get insights of Lithuania traffic incidents from 2023 years.
              Understand, analyse and make action today!
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <a href="/map" className="text-sm font-semibold text-gray-900">
                Interactive map <span aria-hidden="true">→</span>
              </a>
              <a
                href="/analysis"
                className="text-sm font-semibold text-gray-900"
              >
                Data analysis <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;
