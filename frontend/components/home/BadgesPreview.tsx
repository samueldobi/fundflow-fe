import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Card, CardGlow } from "@/components/ui/Card";

const tiers = [
  { name: "Supporter", variant: "green" as const },
  { name: "Gold", variant: "green" as const },
  { name: "Diamond", variant: "purple" as const },
];

export default function BadgesPreview() {
  return (
    <section className="py-16 sm:py-20">
      <div className="max-w-7xl mx-auto px-6 lg:px-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="p-8 overflow-hidden">
            <CardGlow className="opacity-30" />
            <div className="relative">
              <div className="font-syne font-700 tracking-tight text-[22px] sm:text-[26px]">
                Earn NFT badges for every contribution
              </div>
              <p className="mt-3 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
                Every contribution earns a badge. Collect tiers as you support more campaigns..
              </p>

              <div className="mt-6 flex flex-wrap gap-2">
                {tiers.map((t) => (
                  <Badge key={t.name} variant={t.variant}>
                    {t.name}
                  </Badge>
                ))}
                <Badge variant="neutral">+3 more</Badge>
              </div>

              <div className="mt-8">
                <ButtonLink href="/badges" variant="secondary">
                  View collection
                </ButtonLink>
              </div>
            </div>
          </Card>

          <Card className="p-8 overflow-hidden">
            <CardGlow className="opacity-25" />
            <div className="relative">
              <div className="font-syne font-700 tracking-tight text-[22px] sm:text-[26px]">
                Swap tokens before you fund
              </div>
              <p className="mt-3 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
                Built-in quotes with fee breakdown and price impact so backers
                can contribute in the right asset.
              </p>

              <div className="mt-6 grid grid-cols-2 gap-3">
                {["ETH", "USDC", "USDT", "DAI", "WBTC", "ARB"].map((t) => (
                  <div
                    key={t}
                    className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3"
                  >
                    <div className="text-[12px] text-[color:var(--ff-muted)]">
                      Token
                    </div>
                    <div className="mt-1 text-[15px] font-600 text-white">
                      {t}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8">
                <ButtonLink href="/swap" variant="secondary">
                  Open swap
                </ButtonLink>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
