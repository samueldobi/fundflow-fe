import { campaigns } from "@/features/campaigns/mock";
import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Card, CardGlow } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";

function money(value: number) {
  return value.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

export default function CampaignDetail({ id }: { id: string }) {
  const campaign = campaigns.find((c) => c.id === id) ?? campaigns[0];
  const progress =
    campaign.goalUsd > 0
      ? Math.round((campaign.raisedUsd / campaign.goalUsd) * 100)
      : 0;

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <Badge variant="neutral">{campaign.category}</Badge>
            <Badge variant={campaign.status === "In Progress" ? "green" : "purple"}>
              {campaign.status}
            </Badge>
          </div>
          <h1 className="mt-4 font-syne font-700 tracking-tight text-[32px] sm:text-[44px]">
            {campaign.title}
          </h1>
          <p className="mt-3 text-[15px] leading-relaxed text-[color:var(--ff-muted)] max-w-2xl">
            {campaign.description}
          </p>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-6 overflow-hidden">
              <CardGlow className="opacity-25" />
              <div className="relative">
                <div className="font-syne font-700 text-[16px]">
                  Milestones
                </div>
                <div className="mt-2 text-[13px] text-[color:var(--ff-muted)]">
                  Funds release only when each milestone is approved.
                </div>

                <div className="mt-5 space-y-3">
                  {[
                    { name: "Milestone 1", status: "Completed", pct: 25 },
                    { name: "Milestone 2", status: "In Progress", pct: 50 },
                    { name: "Milestone 3", status: "Locked", pct: 75 },
                    { name: "Milestone 4", status: "Locked", pct: 100 },
                  ].map((m) => (
                    <div
                      key={m.name}
                      className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-[13px] text-white/90">
                          {m.name}
                        </div>
                        <Badge
                          variant={
                            m.status === "In Progress"
                              ? "green"
                              : m.status === "Completed"
                                ? "purple"
                                : "neutral"
                          }
                        >
                          {m.status}
                        </Badge>
                      </div>
                      <div className="mt-3">
                        <ProgressBar
                          value={
                            m.status === "Locked"
                              ? 0
                              : m.status === "Completed"
                                ? 100
                                : 55
                          }
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            <Card className="p-6 overflow-hidden">
              <CardGlow className="opacity-25" />
              <div className="relative">
                <div className="font-syne font-700 text-[16px]">
                  Creator updates
                </div>
                <div className="mt-2 text-[13px] text-[color:var(--ff-muted)]">
                  Transparent communication keeps backers confident.
                </div>

                <div className="mt-5 space-y-3">
                  {[
                    {
                      title: "Kickoff: milestone plan published",
                      meta: "2 days ago • 1.2k views",
                    },
                    {
                      title: "Suppliers shortlisted + budget breakdown",
                      meta: "5 days ago • 840 views",
                    },
                    {
                      title: "Endorsement verified",
                      meta: "9 days ago • 2.1k views",
                    },
                  ].map((u) => (
                    <div
                      key={u.title}
                      className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3"
                    >
                      <div className="text-[13px] text-white/90">{u.title}</div>
                      <div className="mt-1 text-[12px] text-[color:var(--ff-muted)]">
                        {u.meta}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        </div>

        <div className="w-full lg:w-[380px]">
          <Card className="p-6 overflow-hidden sticky top-[92px]">
            <CardGlow className="opacity-30" />
            <div className="relative">
              <div className="flex items-baseline justify-between gap-4">
                <div className="text-[12px] text-[color:var(--ff-muted)]">
                  Raised
                </div>
                <div className="font-syne font-700 text-[22px]">
                  {money(campaign.raisedUsd)}
                </div>
              </div>
              <div className="mt-2 flex items-center justify-between gap-4 text-[12px] text-[color:var(--ff-muted)]">
                <span>{campaign.backers.toLocaleString()} backers</span>
                <span>{money(campaign.goalUsd)} goal</span>
              </div>

              <div className="mt-5">
                <ProgressBar value={campaign.status === "Failed" ? 0 : progress} />
                <div className="mt-2 text-[12px] text-[color:var(--ff-muted)]">
                  {campaign.status === "In Progress"
                    ? `${campaign.daysLeft} days left`
                    : "Campaign ended"}
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-3">
                <ButtonLink href="/swap" variant="primary" size="lg">
                  Swap & contribute
                </ButtonLink>
                <ButtonLink href="/badges" variant="secondary" size="lg">
                  View NFT badges
                </ButtonLink>
              </div>

              <div className="mt-6 rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-4">
                <div className="text-[13px] font-medium text-white/90">
                  Platform fee
                </div>
                <div className="mt-1 text-[12px] text-[color:var(--ff-muted)]">
                  1.5% of raised amount (placeholder UI).
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
