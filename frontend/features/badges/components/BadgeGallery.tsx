import { Badge } from "@/components/ui/Badge";
import { Card, CardGlow } from "@/components/ui/Card";

const tiers = [
  {
    name: "Supporter",
    accent: "green" as const,
    xp: "120 XP",
    description:
      "First step into supporting impactful campaigns on Fundflow.",
  },
  {
    name: "Bronze",
    accent: "neutral" as const,
    xp: "380 XP",
    description: "Early supporter helping projects gain initial momentum.",
  },
  {
    name: "Silver",
    accent: "neutral" as const,
    xp: "860 XP",
    description: "Consistent contributor backing campaigns over time.",
  },
  {
    name: "Gold",
    accent: "green" as const,
    xp: "1,420 XP",
    description:
      "High-value contributor making a strong impact on campaign progress.",
  },
  {
    name: "Platinum",
    accent: "purple" as const,
    xp: "2,400 XP",
    description: "Major backer supporting campaigns at a significant level.",
  },
  {
    name: "Diamond",
    accent: "purple" as const,
    xp: "4,800 XP",
    description:
      "Top supporter with exceptional contribution across campaigns.",
  },
];

function BadgeArt({ variant }: { variant: "green" | "purple" | "neutral" }) {
  const glow =
    variant === "green"
      ? "rgba(0,255,163,0.35)"
      : variant === "purple"
        ? "rgba(168,85,247,0.32)"
        : "rgba(148,163,184,0.22)";
  const core =
    variant === "green"
      ? "rgba(0,255,163,0.25)"
      : variant === "purple"
        ? "rgba(168,85,247,0.24)"
        : "rgba(148,163,184,0.18)";

  return (
    <div className="relative h-[120px] rounded-2xl border border-white/[0.10] bg-white/[0.03] overflow-hidden">
      <div
        className="absolute -top-16 -left-16 h-48 w-48 rounded-full blur-[40px]"
        style={{ background: glow }}
      />
      <div
        className="absolute -bottom-20 -right-20 h-56 w-56 rounded-full blur-[50px]"
        style={{ background: glow }}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <div
          className="h-16 w-16 rounded-2xl border border-white/[0.14]"
          style={{ background: core, boxShadow: `0 0 50px ${glow}` }}
        />
      </div>
    </div>
  );
}

export default function BadgeGallery() {
  return (
    <section className="py-16 sm:py-20">
      <div className="max-w-7xl mx-auto px-6 lg:px-10">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
          <div className="max-w-2xl">
            <h2 className="font-syne font-700 tracking-tight text-[28px] sm:text-[36px]">
              NFT contribution badges
            </h2>
            <p className="mt-3 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
              Every contribution mints a badge tier on-chain SVG art, no IPFS
              dependency.
            </p>
          </div>
          <div className="flex gap-2">
            <Badge variant="green">XP</Badge>
            <Badge variant="purple">Streaks</Badge>
          </div>
        </div>

        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {tiers.map((tier) => (
            <Card key={tier.name} className="p-6 overflow-hidden">
              <CardGlow className="opacity-25" />
              <div className="relative">
                <div className="flex items-center justify-between gap-3">
                  <Badge variant={tier.accent}>{tier.name}</Badge>
                  <span className="text-[12px] text-[color:var(--ff-muted)]">
                    {tier.xp}
                  </span>
                </div>
                <div className="mt-4">
                  <BadgeArt
                    variant={
                      tier.accent === "neutral" ? "neutral" : tier.accent
                    }
                  />
                </div>
                <div className="mt-4 text-[13px] leading-relaxed text-[color:var(--ff-muted)]">
                  {tier.description}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
