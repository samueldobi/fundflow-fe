import type { ComponentProps } from "react";
import { cn } from "@/lib/cn";

type BadgeVariant = "green" | "purple" | "neutral";

const variants: Record<BadgeVariant, string> = {
  green:
    "border-[rgba(0,255,163,0.25)] bg-[rgba(0,255,163,0.12)] text-[color:var(--ff-accent)]",
  purple:
    "border-[rgba(168,85,247,0.25)] bg-[rgba(168,85,247,0.12)] text-[color:var(--ff-accent-2)]",
  neutral:
    "border-white/[0.14] bg-white/[0.06] text-[color:var(--ff-muted)]",
};

export function Badge({
  className,
  variant = "neutral",
  ...props
}: ComponentProps<"span"> & { variant?: BadgeVariant }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[12px] font-medium leading-none",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}

