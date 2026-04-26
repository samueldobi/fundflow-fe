import type { ComponentProps } from "react";
import { cn } from "@/lib/cn";

export function Select({ className, ...props }: ComponentProps<"select">) {
  return (
    <select
      className={cn(
        "h-11 w-full appearance-none rounded-2xl border border-white/[0.12] bg-white/[0.04] px-4 pr-10 text-[14px] text-white",
        "outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--ff-accent)]/60",
        className,
      )}
      {...props}
    />
  );
}

export function SelectWrap({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("relative", className)}>
      {children}
      <svg
        className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 h-4 w-4 text-white/60"
        viewBox="0 0 20 20"
        fill="none"
      >
        <path
          d="M6 8l4 4 4-4"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}

