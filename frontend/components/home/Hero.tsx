import Image from "next/image";

import { ButtonLink } from "@/frontend/components/ui/Button";
import { Badge } from "@/frontend/components/ui/Badge";

export default function HeroSection() {
  return (
    <section className="relative isolate overflow-hidden">
      {/* Background image */}
      <div className="absolute inset-0 -z-10">
        <Image
          src="/hero1.png"
          alt=""
          aria-hidden="true"
          fill
          priority
          className="object-cover object-center opacity-85"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-[color:var(--ff-bg)]/75" />
        <div className="absolute inset-0 bg-[radial-gradient(62%_62%_at_50%_35%,rgba(0,255,163,0.20)_0%,rgba(2,6,23,0)_62%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(55%_55%_at_15%_20%,rgba(168,85,247,0.16)_0%,rgba(2,6,23,0)_55%)]" />
      </div>

      <div className="min-h-[calc(100vh-72px)] flex items-center">
        <div className="w-full max-w-6xl mx-auto px-6 lg:px-10 py-20 lg:py-24">
          <div className="mx-auto max-w-3xl text-center">
            <div className="flex justify-center mb-6">
              <Badge variant="green" className="bg-white/[0.03]">
                Live on multiple chains
              </Badge>
            </div>

            <h1 className="font-syne font-700 tracking-tight text-[44px] leading-[1.02] sm:text-[64px] lg:text-[80px]">
              On-chain crowdfunding,
              <span className="text-[color:var(--ff-accent)]"> done right</span>.
            </h1>
            <p className="mt-5 text-[15px] sm:text-[16px] leading-relaxed text-[color:var(--ff-muted)]">
              Create campaigns, unlock milestone-based releases, mint NFT
              contribution badges, and swap tokens before you contribute.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3">
              <ButtonLink href="/campaigns" variant="primary" size="lg">
                Explore campaigns
              </ButtonLink>
              <ButtonLink href="/create" variant="secondary" size="lg">
                Start a campaign
              </ButtonLink>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
