import { ButtonLink } from "@/components/ui/Button";
import { Card, CardGlow } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export default function CTA() {
  return (
    <section className="py-16 sm:py-20">
      <div className="max-w-7xl mx-auto px-6 lg:px-10">
        <Card className="p-8 sm:p-10 overflow-hidden">
          <CardGlow className="opacity-35" />
          <div className="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
            <div className="max-w-2xl">
              <div className="flex items-center gap-2 mb-4">
                <Badge variant="green">Crowdfunding</Badge>
                <Badge variant="purple">Badges</Badge>
                <Badge variant="neutral">Swap</Badge>
              </div>
              <h3 className="font-syne font-700 tracking-tight text-[26px] sm:text-[34px]">
                Launch your next campaign with milestone accountability
              </h3>
              <p className="mt-3 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
                Build trust with refunds, updates, and endorsements—then reward
                contributors with NFT badges.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <ButtonLink href="/create" variant="primary" size="lg">
                Create campaign
              </ButtonLink>
              <ButtonLink href="/dashboard" variant="secondary" size="lg">
                Open dashboard
              </ButtonLink>
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
}
