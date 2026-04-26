import type { ComponentProps } from "react";
import { cn } from "@/lib/cn";

export function Label({ className, ...props }: ComponentProps<"label">) {
  return (
    <label
      className={cn(
        "block text-[13px] font-medium text-white/85 mb-2",
        className,
      )}
      {...props}
    />
  );
}

export function Input({ className, ...props }: ComponentProps<"input">) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-2xl border border-white/[0.12] bg-white/[0.04] px-4 text-[14px] text-white placeholder:text-white/35",
        "outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--ff-accent)]/60",
        className,
      )}
      {...props}
    />
  );
}

export function Textarea({
  className,
  ...props
}: ComponentProps<"textarea">) {
  return (
    <textarea
      className={cn(
        "min-h-[120px] w-full resize-none rounded-2xl border border-white/[0.12] bg-white/[0.04] px-4 py-3 text-[14px] text-white placeholder:text-white/35",
        "outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--ff-accent)]/60",
        className,
      )}
      {...props}
    />
  );
}

export function HelperText({
  className,
  ...props
}: ComponentProps<"div">) {
  return (
    <div
      className={cn("mt-2 text-[12px] text-[color:var(--ff-muted)]", className)}
      {...props}
    />
  );
}

