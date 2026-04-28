"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import ConnectWalletModal from "@/components/wallet/ConnectWalletModal";
import ConnectModal from "@/components/wallet/ConnectModal"

const navLinks = [
  { label: "Campaigns", href: "/campaigns" },
  { label: "Create", href: "/create" },
  { label: "Swap", href: "/swap" },
  { label: "Badges", href: "/badges" },
  { label: "Dashboard", href: "/dashboard" },
  { label: "Learn", href: "/learn" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [walletOpen, setWalletOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll);
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-[color:var(--ff-bg)]/80 backdrop-blur-xl border-b border-white/[0.10] shadow-[0_12px_40px_rgba(0,0,0,0.55)]"
            : "bg-[color:var(--ff-bg)]/55 backdrop-blur-xl border-b border-white/[0.08]"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <div className="flex items-center justify-between h-[72px] gap-4">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-xl border border-white/[0.12] bg-white/[0.04] shadow-[0_0_0_1px_rgba(255,255,255,0.04)_inset]" />
              <span className="font-syne font-700 text-[16px] tracking-tight text-white">
                Fundflow<span className="text-white/40">.</span>
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="ff-nav-desktop flex-1 justify-center">
              <nav className="flex items-center gap-1.5 px-2 py-1 rounded-full border border-white/[0.10] bg-white/[0.04]">
                {navLinks.map((link) => {
                  const active =
                    pathname === link.href ||
                    (link.href !== "/" && pathname.startsWith(link.href + "/"));

                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      aria-current={active ? "page" : undefined}
                      className={`relative px-3.5 py-2 text-[13.5px] font-dm-sans font-medium transition-colors duration-150 group ${
                        active ? "text-white" : "text-white/70 hover:text-white"
                      }`}
                    >
                      <span className="relative z-10">{link.label}</span>
                      <span
                        className={`absolute inset-0 rounded-full transition-colors duration-200 ${
                          active
                            ? "bg-white/[0.10]"
                            : "bg-white/0 group-hover:bg-white/[0.06]"
                        }`}
                      />
                    </Link>
                  );
                })}
              </nav>
            </div>

            {/* Right side */}
            <div className="ff-nav-desktop items-center gap-3">
              <button
                type="button"
                onClick={() => setWalletOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-[13px] font-dm-sans font-medium text-white border border-white/[0.12] bg-white/[0.05] hover:bg-white/[0.08] transition-colors"
              >
                Connect Wallet
                <svg
                  className="w-3.5 h-3.5"
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
              </button>
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="ff-nav-mobile flex-col justify-center items-center w-10 h-10 gap-[5px] rounded-2xl border border-white/[0.12] bg-white/[0.04] hover:bg-white/[0.07] transition-colors"
              aria-label="Toggle menu"
              aria-expanded={mobileOpen}
            >
              <span
                className={`block h-[1.5px] bg-white/80 transition-all duration-200 ${
                  mobileOpen ? "w-5 rotate-45 translate-y-[6.5px]" : "w-5"
                }`}
              />
              <span
                className={`block h-[1.5px] bg-white/80 transition-all duration-200 ${
                  mobileOpen ? "w-0 opacity-0" : "w-3.5"
                }`}
              />
              <span
                className={`block h-[1.5px] bg-white/80 transition-all duration-200 ${
                  mobileOpen ? "w-5 -rotate-45 -translate-y-[6.5px]" : "w-5"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        <div
          className={`ff-nav-mobile overflow-hidden transition-all duration-200 ease-in-out ${
            mobileOpen
              ? "h-[calc(100vh-72px)] opacity-100 pointer-events-auto"
              : "h-0 opacity-0 pointer-events-none"
          }`}
        >
          <div className="h-full bg-[color:var(--ff-surface)]/80 backdrop-blur-xl border-t border-white/[0.08] px-6 pt-4 pb-6 overflow-y-auto">
            <nav className="flex flex-col gap-1.5 mb-5">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  aria-current={pathname === link.href ? "page" : undefined}
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-3 text-[15px] font-dm-sans text-white/80 hover:text-white hover:bg-white/[0.06] rounded-xl transition-colors duration-150"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
            <button
              type="button"
              onClick={() => {
                setMobileOpen(false);
                setWalletOpen(true);
              }}
              className="flex items-center justify-center gap-2 w-full py-3 rounded-xl font-dm-sans font-medium text-[14px] text-[#0B0F17] bg-white hover:bg-white/90 transition-colors"
            >
              Connect Wallet
            </button>
          </div>
        </div>
      </header>

      {walletOpen ? (
        <ConnectWalletModal onClose={() => setWalletOpen(false)} />
      ) : null}
      {/* {walletOpen ? (
        <ConnectModal />
      ) : null} */}
    </>
  );
}
