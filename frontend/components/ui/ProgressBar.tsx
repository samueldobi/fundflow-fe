import { cn } from "@/lib/cn";

export function ProgressBar({
  value,
  className,
}: {
  value: number;
  className?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div
      className={cn(
        "h-2 rounded-full bg-white/[0.08] overflow-hidden",
        className,
      )}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="h-full rounded-full bg-[color:var(--ff-accent)] shadow-[0_0_22px_rgba(0,255,163,0.45)]"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}

