import Link from "next/link";

import { Badge } from "@/frontend/components/ui/Badge";
import { ButtonLink } from "@/frontend/components/ui/Button";
import { Card, CardGlow } from "@/frontend/components/ui/Card";
import { ProgressBar } from "@/frontend/components/ui/ProgressBar";

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3">
      <div className="text-[11px] text-[color:var(--ff-muted)]">{label}</div>
      <div className="mt-1 text-[15px] font-600 text-white">{value}</div>
    </div>
  );
}

function ChartPlaceholder() {
  return (
    <div className="h-[180px] rounded-2xl border border-white/[0.10] bg-[linear-gradient(180deg,rgba(255,255,255,0.05)_0%,rgba(255,255,255,0.02)_100%)] overflow-hidden">
      <div className="h-full w-full bg-[radial-gradient(60%_70%_at_40%_20%,rgba(0,255,163,0.18)_0%,rgba(2,6,23,0)_60%),radial-gradient(55%_60%_at_70%_65%,rgba(168,85,247,0.14)_0%,rgba(2,6,23,0)_55%)]" />
    </div>
  );
}

export default function DashboardOverview() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div className="max-w-2xl">
          <h1 className="font-syne font-700 tracking-tight text-[28px] sm:text-[40px]">
            Dashboard
          </h1>
          <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
            Track campaigns, contributions, and analytics (UI only—wallet logic
            comes later).
          </p>
        </div>
        <div className="flex gap-3">
          <ButtonLink href="/create" variant="primary">
            New campaign
          </ButtonLink>
          <ButtonLink href="/campaigns" variant="secondary">
            Browse
          </ButtonLink>
        </div>
      </div>

      <div className="mt-10 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="p-6 overflow-hidden lg:col-span-2">
          <CardGlow className="opacity-25" />
          <div className="relative">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="font-syne font-700 tracking-tight text-[18px]">
                  Contributions over time
                </div>
                <div className="mt-1 text-[13px] text-[color:var(--ff-muted)]">
                  Real-time chart placeholder
                </div>
              </div>
              <Badge variant="green">Live</Badge>
            </div>
            <div className="mt-6">
              <ChartPlaceholder />
            </div>
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
              <MiniStat label="Total contributed" value="$8,420" />
              <MiniStat label="Badges earned" value="5" />
              <MiniStat label="Streak" value="7 days" />
              <MiniStat label="Networks" value="4" />
            </div>
          </div>
        </Card>

        <Card className="p-6 overflow-hidden">
          <CardGlow className="opacity-25" />
          <div className="relative">
            <div className="flex items-center justify-between gap-4">
              <div className="font-syne font-700 tracking-tight text-[18px]">
                Your campaigns
              </div>
              <Badge variant="purple">Creator</Badge>
            </div>
            <div className="mt-2 text-[13px] text-[color:var(--ff-muted)]">
              Quick health checks and milestones.
            </div>

            <div className="mt-6 space-y-3">
              {[
                { title: "Clean Water Initiative", pct: 65, status: "In Progress" },
                { title: "Open-source Grants", pct: 100, status: "Completed" },
              ].map((c) => (
                <Link
                  key={c.title}
                  href="/campaigns"
                  className="block rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-4 hover:bg-white/[0.05] transition-colors"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-[13px] text-white/90">{c.title}</div>
                    <Badge variant={c.status === "Completed" ? "purple" : "green"}>
                      {c.status}
                    </Badge>
                  </div>
                  <div className="mt-3">
                    <ProgressBar value={c.pct} />
                  </div>
                </Link>
              ))}
            </div>

            <div className="mt-6 rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-4">
              <div className="text-[13px] font-medium text-white/90">
                Category breakdown
              </div>
              <div className="mt-3 space-y-2 text-[12px] text-[color:var(--ff-muted)]">
                <div className="flex items-center justify-between">
                  <span>Education</span>
                  <span>34%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Community</span>
                  <span>28%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Medical</span>
                  <span>18%</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

