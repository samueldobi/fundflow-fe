import type { ComponentProps } from "react";
import { cn } from "@/lib/cn";

export function Card({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "relative rounded-[28px] border border-white/[0.10] bg-[color:var(--ff-surface)]/70 backdrop-blur-xl",
        "shadow-[0_18px_70px_rgba(0,0,0,0.40)]",
        className,
      )}
      {...props}
    />
  );
}

export function CardGlow({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "absolute -inset-px rounded-[28px] opacity-40 pointer-events-none",
        "bg-[radial-gradient(70%_70%_at_30%_20%,rgba(0,255,163,0.22)_0%,rgba(2,6,23,0)_60%),radial-gradient(60%_60%_at_75%_35%,rgba(168,85,247,0.18)_0%,rgba(2,6,23,0)_55%)]",
        className,
      )}
      {...props}
    />
  );
}

