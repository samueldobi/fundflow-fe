import { Badge } from "@/components/ui/Badge";
import { Card, CardGlow } from "@/components/ui/Card";

export default function LearnPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
      <div className="max-w-2xl">
        <h1 className="font-syne font-700 tracking-tight text-[28px] sm:text-[40px]">
          Learn
        </h1>
        <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
          Placeholder learning hub for the EdTech side of the platform.
        </p>
      </div>

      <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { title: "Wallet basics", tag: "Beginner" },
          { title: "On-chain safety", tag: "Essential" },
          { title: "Crowdfunding mechanics", tag: "Product" },
          { title: "Milestones + refunds", tag: "Protocol" },
          { title: "NFT badge tiers", tag: "Gamified" },
          { title: "Token swaps", tag: "DeFi" },
        ].map((item) => (
          <Card key={item.title} className="p-6 overflow-hidden">
            <CardGlow className="opacity-25" />
            <div className="relative">
              <Badge variant="neutral">{item.tag}</Badge>
              <div className="mt-4 font-syne font-700 tracking-tight text-[18px]">
                {item.title}
              </div>
              <div className="mt-2 text-[14px] leading-relaxed text-[color:var(--ff-muted)]">
                Short module description goes here. Content and routing will be
                wired later.
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
