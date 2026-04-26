import SwapWidget from "@/features/swap/components/SwapWidget";

export default function SwapPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
      <div className="max-w-2xl">
        <h1 className="font-syne font-700 tracking-tight text-[28px] sm:text-[40px]">
          Swap
        </h1>
        <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
          Swap tokens before contributing (UI-only).
        </p>
      </div>

      <div className="mt-8 max-w-[520px]">
        <SwapWidget />
      </div>
    </div>
  );
}
