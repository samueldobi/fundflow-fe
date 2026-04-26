import Image from "next/image";
import { cn } from "@/lib/cn";

export function AvatarStack({
  images,
  className,
  size = 28,
  max = 4,
}: {
  images: string[];
  className?: string;
  size?: number;
  max?: number;
}) {
  const shown = images.slice(0, max);
  const remaining = Math.max(0, images.length - shown.length);

  return (
    <div className={cn("flex items-center", className)}>
      {shown.map((src, idx) => (
        <div
          key={`${src}-${idx}`}
          className="relative rounded-full border border-white/[0.18] bg-white/[0.04] overflow-hidden"
          style={{
            width: size,
            height: size,
            marginLeft: idx === 0 ? 0 : -Math.round(size * 0.35),
          }}
        >
          <Image
            src={src}
            alt=""
            aria-hidden="true"
            fill
            className="object-cover"
            sizes={`${size}px`}
          />
        </div>
      ))}
      {remaining > 0 ? (
        <div
          className="ml-2 rounded-full border border-white/[0.14] bg-white/[0.06] px-2.5 py-1 text-[12px] text-white/75"
          aria-label={`${remaining} more`}
        >
          +{remaining}
        </div>
      ) : null}
    </div>
  );
}

