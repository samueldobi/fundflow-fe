import Link from "next/link";

import type { Campaign } from "@/features/campaigns/mock";
import { Badge } from "@/components/ui/Badge";
import { Card, CardGlow } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";

function money(value: number) {
  return value.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

function statusVariant(status: Campaign["status"]) {
  if (status === "In Progress") return "green";
  if (status === "Completed") return "purple";
  return "neutral";
}

export default function CampaignCard({ campaign }: { campaign: Campaign }) {
  const progress =
    campaign.goalUsd > 0
      ? Math.round((campaign.raisedUsd / campaign.goalUsd) * 100)
      : 0;

  return (
    <Card className="p-6 overflow-hidden">
      <CardGlow />
      <div className="relative">
        <div className="flex items-center justify-between gap-3">
          <Badge variant="neutral">{campaign.category}</Badge>
          <Badge variant={statusVariant(campaign.status)}>{campaign.status}</Badge>
        </div>

        <div className="mt-4 font-syne font-700 tracking-tight text-[18px]">
          <Link
            href={`/campaigns/${campaign.id}`}
            className="hover:text-white/90 transition-colors"
          >
            {campaign.title}
          </Link>
        </div>
        <p className="mt-2 text-[14px] leading-relaxed text-[color:var(--ff-muted)] line-clamp-3">
          {campaign.description}
        </p>

        <div className="mt-5">
          <ProgressBar value={campaign.status === "Failed" ? 0 : progress} />
          <div className="mt-2 flex items-center justify-between text-[12px] text-[color:var(--ff-muted)]">
            <span>{money(campaign.raisedUsd)} raised</span>
            <span>{money(campaign.goalUsd)} goal</span>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-3 gap-3">
          <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-3 py-2">
            <div className="text-[11px] text-[color:var(--ff-muted)]">
              Backers
            </div>
            <div className="text-[14px] font-600 text-white">
              {campaign.backers.toLocaleString()}
            </div>
          </div>
          <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-3 py-2">
            <div className="text-[11px] text-[color:var(--ff-muted)]">
              Days left
            </div>
            <div className="text-[14px] font-600 text-white">
              {campaign.daysLeft}
            </div>
          </div>
          <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-3 py-2">
            <div className="text-[11px] text-[color:var(--ff-muted)]">
              Milestones
            </div>
            <div className="text-[14px] font-600 text-white">2/4</div>
          </div>
        </div>
      </div>
    </Card>
  );
}
