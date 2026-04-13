"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const navLinks = [
  { label: "Ecosystem", href: "/ecosystem" },
  { label: "Learn", href: "/learn" },
  { label: "Build", href: "/build" },
  { label: "Grants", href: "/grants" },
  { label: "Events", href: "/events" },
  { label: "Blog", href: "/blog" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled
            ? "bg-[#080B12]/80 backdrop-blur-xl border-b border-white/[0.06] shadow-[0_8px_32px_rgba(0,0,0,0.4)]"
            : "bg-transparent"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="flex items-center justify-between h-[72px]">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2.5 group">
              {/* Geometric logo mark */}
              <div className="relative w-8 h-8">
                <div className="absolute inset-0 bg-gradient-to-br from-[#00F5A0] to-[#00C8FF] rounded-lg opacity-90 group-hover:opacity-100 transition-opacity" />
                <div className="absolute inset-[2px] bg-[#080B12] rounded-md flex items-center justify-center">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M8 1L14.5 5V11L8 15L1.5 11V5L8 1Z"
                      stroke="url(#hexGrad)"
                      strokeWidth="1.5"
                      strokeLinejoin="round"
                      fill="none"
                    />
                    <circle cx="8" cy="8" r="2" fill="url(#hexGrad)" />
                    <defs>
                      <linearGradient
                        id="hexGrad"
                        x1="1.5"
                        y1="1"
                        x2="14.5"
                        y2="15"
                        gradientUnits="userSpaceOnUse"
                      >
                        <stop stopColor="#00F5A0" />
                        <stop offset="1" stopColor="#00C8FF" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
              </div>
              <span className="font-syne font-700 text-[17px] tracking-tight text-white">
                nexus<span className="text-[#00F5A0]">.</span>
              </span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="relative px-4 py-2 text-[13.5px] font-dm-sans font-medium text-white/50 hover:text-white transition-colors duration-200 group"
                >
                  <span className="relative z-10">{link.label}</span>
                  {/* Hover pill */}
                  <span className="absolute inset-0 rounded-lg bg-white/0 group-hover:bg-white/[0.05] transition-colors duration-200" />
                </Link>
              ))}
            </nav>

            {/* Right side */}
            <div className="hidden md:flex items-center gap-3">
              {/* Network status pill */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.08] bg-white/[0.03] text-[12px] font-dm-sans text-white/40">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F5A0] opacity-75" />
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#00F5A0]" />
                </span>
                Mainnet
              </div>

              {/* CTA */}
              <Link
                href="/launch"
                className="relative inline-flex items-center gap-2 px-5 py-2 rounded-xl text-[13px] font-syne font-600 text-[#080B12] overflow-hidden group"
              >
                {/* Gradient bg */}
                <span className="absolute inset-0 bg-gradient-to-r from-[#00F5A0] to-[#00C8FF] transition-transform duration-300" />
                {/* Shimmer */}
                <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out" />
                <span className="relative">Launch App</span>
                <svg
                  className="relative w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform"
                  fill="none"
                  viewBox="0 0 14 14"
                >
                  <path
                    d="M1 7h12M8 2l5 5-5 5"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </Link>
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden flex flex-col justify-center items-center w-9 h-9 gap-[5px] group"
              aria-label="Toggle menu"
            >
              <span
                className={`block h-[1.5px] bg-white/70 transition-all duration-300 ${
                  mobileOpen ? "w-5 rotate-45 translate-y-[6.5px]" : "w-5"
                }`}
              />
              <span
                className={`block h-[1.5px] bg-white/70 transition-all duration-300 ${
                  mobileOpen ? "w-0 opacity-0" : "w-3.5"
                }`}
              />
              <span
                className={`block h-[1.5px] bg-white/70 transition-all duration-300 ${
                  mobileOpen ? "w-5 -rotate-45 -translate-y-[6.5px]" : "w-5"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        <div
          className={`md:hidden overflow-hidden transition-all duration-400 ease-in-out ${
            mobileOpen ? "max-h-[400px] opacity-100" : "max-h-0 opacity-0"
          }`}
        >
          <div className="bg-[#080B12]/95 backdrop-blur-xl border-t border-white/[0.06] px-6 pt-4 pb-6">
            <nav className="flex flex-col gap-1 mb-5">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-3 text-[15px] font-dm-sans text-white/50 hover:text-white hover:bg-white/[0.04] rounded-lg transition-all duration-150"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
            <Link
              href="/launch"
              onClick={() => setMobileOpen(false)}
              className="flex items-center justify-center gap-2 w-full py-3 rounded-xl font-syne font-600 text-[14px] text-[#080B12] bg-gradient-to-r from-[#00F5A0] to-[#00C8FF]"
            >
              Launch App
            </Link>
          </div>
        </div>
      </header>
    </>
  );
}