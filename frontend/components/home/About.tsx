import { Badge } from "@/components/ui/Badge";
import { Card, CardGlow } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";

const highlights = [
  {
    title: "Milestone releases",
    description:
      "Funds unlock in stages—backers get accountability, creators get momentum.",
    badge: { label: "In Progress", variant: "green" as const },
  },
  {
    title: "Refund protection",
    description:
      "If a campaign fails, contributors can claim refunds based on the rules.",
    badge: { label: "Built-in", variant: "neutral" as const },
  },
  {
    title: "NFT contribution badges",
    description:
      "Supporter → Diamond tiers, minted automatically for every contribution.",
    badge: { label: "On-chain SVG", variant: "purple" as const },
  },
  {
    title: "Swap before you fund",
    description:
      "Built-in quotes with price impact and fee breakdown for multiple tokens.",
    badge: { label: "DEX", variant: "neutral" as const },
  },
  {
    title: "Multi-chain by design",
    description: "Deploy on Arbitrum, Base, Optimism, Polygon, and Ethereum.",
    badge: { label: "Web3", variant: "purple" as const },
  },
  {
    title: "Real-time analytics",
    description:
      "Track contributions, categories, and growth signals—live and readable.",
    badge: { label: "Dashboard", variant: "neutral" as const },
  },
];

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="text-[12px] text-[color:var(--ff-muted)]">{label}</div>
      <div className="text-[15px] font-600 text-white">{value}</div>
    </div>
  );
}

export default function About() {
  return (
    <section className="relative py-16 sm:py-20">
      <div className="max-w-7xl mx-auto px-6 lg:px-10">
        <div className="max-w-2xl">
          <h2 className="font-syne font-700 tracking-tight text-[28px] sm:text-[36px]">
            A bento-style platform for creators and communities
          </h2>
          <p className="mt-3 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
            Everything you need to run transparent crowdfunding: milestones,
            protection, badges, swaps, and analytics—wrapped in a clean,
            developer-friendly UI.
          </p>
        </div>

        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {highlights.map((item) => (
            <Card key={item.title} className="p-6 overflow-hidden">
              <CardGlow />
              <div className="relative">
                <Badge variant={item.badge.variant}>{item.badge.label}</Badge>
                <div className="mt-4 font-syne font-700 text-[18px] tracking-tight">
                  {item.title}
                </div>
                <div className="mt-2 text-[14px] leading-relaxed text-[color:var(--ff-muted)]">
                  {item.description}
                </div>
              </div>
            </Card>
          ))}

          <Card className="p-6 md:col-span-2 lg:col-span-3 overflow-hidden">
            <CardGlow className="opacity-30" />
            <div className="relative grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
              <div className="lg:col-span-1">
                <div className="font-syne font-700 text-[18px] tracking-tight">
                  Crowdfunding health
                </div>
                <div className="mt-2 text-[14px] leading-relaxed text-[color:var(--ff-muted)]">
                  A quick snapshot of how an example campaign progresses toward
                  its goal.
                </div>
              </div>
              <div className="lg:col-span-2">
                <div className="flex items-center justify-between gap-4">
                  <Stat label="Raised" value="$32,480" />
                  <Stat label="Goal" value="$50,000" />
                  <Stat label="Backers" value="1,204" />
                  <Stat label="Days left" value="12" />
                </div>
                <div className="mt-5">
                  <ProgressBar value={65} />
                  <div className="mt-2 text-[12px] text-[color:var(--ff-muted)]">
                    65% funded • milestone 2/4 in progress
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
