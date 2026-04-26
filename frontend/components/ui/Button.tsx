import Link from "next/link";
import type { ComponentProps } from "react";

import { cn } from "@/lib/cn";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

const base =
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-2xl font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--ff-accent)]/60 focus-visible:ring-offset-0 disabled:opacity-50 disabled:pointer-events-none";

const variants: Record<ButtonVariant, string> = {
  primary:
    "bg-white text-[#020617] hover:bg-white/90 shadow-[0_18px_60px_rgba(0,255,163,0.14)]",
  secondary:
    "border border-white/[0.14] bg-white/[0.05] text-white hover:bg-white/[0.08]",
  ghost: "text-white/80 hover:text-white hover:bg-white/[0.06]",
};

const sizes: Record<ButtonSize, string> = {
  sm: "h-10 px-4 text-[13px]",
  md: "h-11 px-5 text-[14px]",
  lg: "h-12 px-6 text-[15px]",
};

type ButtonProps = ComponentProps<"button"> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function Button({
  className,
  variant = "secondary",
  size = "md",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(base, variants[variant], sizes[size], className)}
      {...props}
    />
  );
}

type ButtonLinkProps = ComponentProps<typeof Link> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

export function ButtonLink({
  className,
  variant = "secondary",
  size = "md",
  ...props
}: ButtonLinkProps) {
  return (
    <Link
      className={cn(base, variants[variant], sizes[size], className)}
      {...props}
    />
  );
}

