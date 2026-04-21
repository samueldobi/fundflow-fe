import Link from "next/link";
import Image from "next/image";

export default function HeroSection() {
  return (
    <section className="relative isolate overflow-hidden">
      {/* Background image */}
      <div className="absolute inset-0 -z-10">
        <Image
          src="/hero3.jpg"
          alt=""
          aria-hidden="true"
          fill
          priority
          className="object-cover object-center opacity-90"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-[#080B12]/30" />
        <div className="absolute inset-0 bg-[radial-gradient(60%_60%_at_50%_35%,rgba(0,245,160,0.18)_0%,rgba(8,11,18,0)_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(55%_55%_at_20%_20%,rgba(108,99,255,0.14)_0%,rgba(8,11,18,0)_55%)]" />
      </div>

      <div className="min-h-[calc(100vh-72px)] flex items-center">
        <div className="w-full max-w-5xl mx-auto px-6 lg:px-10 py-20 lg:py-24">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="font-syne font-700 tracking-tight text-[40px] leading-[1.05] sm:text-[54px] lg:text-[64px]">
              Fund the future<br/> On-chain.
            </h1>
            <p className="mt-5 text-[20px] sm:text-[18px] leading-relaxed text-white/70">
              A modern crowdfunding experience for founders and communities. Fast,
              transparent, and built for Web3.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-3">
              <Link
                href="/launch"
                className="inline-flex items-center justify-center rounded-xl px-5 py-3 text-[14px] font-medium text-[#0B0F17] bg-white hover:bg-white/90 transition-colors"
              >
                Launch App
              </Link>
              <Link
                href="/learn"
                className="inline-flex items-center justify-center rounded-xl px-5 py-3 text-[14px] font-medium text-white border border-white/[0.14] bg-white/[0.04] hover:bg-white/[0.07] transition-colors"
              >
                Learn more
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
