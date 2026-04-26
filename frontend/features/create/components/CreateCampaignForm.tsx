import { Badge } from "@/frontend/components/ui/Badge";
import { Button } from "@/frontend/components/ui/Button";
import { Card, CardGlow } from "@/frontend/components/ui/Card";
import { Input, Label, Textarea, HelperText } from "@/frontend/components/ui/Input";
import { Select, SelectWrap } from "@/frontend/components/ui/Select";

const categories = [
  "Medical",
  "Education",
  "Emergency",
  "Community",
  "Climate",
  "Open Source",
] as const;

export default function CreateCampaignForm() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div className="max-w-2xl">
          <h1 className="font-syne font-700 tracking-tight text-[28px] sm:text-[40px]">
            Create a campaign
          </h1>
          <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
            UI-only form. Wallet connection, validations, and on-chain writes come
            later.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="green">Milestones</Badge>
          <Badge variant="neutral">Refund rules</Badge>
          <Badge variant="purple">Endorsements</Badge>
        </div>
      </div>

      <div className="mt-10 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="p-6 overflow-hidden lg:col-span-2">
          <CardGlow className="opacity-25" />
          <div className="relative space-y-5">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input id="title" placeholder="e.g., Clean Water for Communities" />
              <HelperText>Keep it clear and outcome-focused.</HelperText>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe the problem, your plan, and how milestones will be delivered..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="category">Category</Label>
                <SelectWrap>
                  <Select id="category" defaultValue={categories[0]}>
                    {categories.map((c) => (
                      <option key={c} value={c} className="bg-[#0f172a]">
                        {c}
                      </option>
                    ))}
                  </Select>
                </SelectWrap>
              </div>
              <div>
                <Label htmlFor="deadline">Deadline</Label>
                <Input id="deadline" type="date" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="goal">Goal (USD)</Label>
                <Input id="goal" placeholder="50000" inputMode="numeric" />
              </div>
              <div>
                <Label htmlFor="chain">Chain</Label>
                <SelectWrap>
                  <Select id="chain" defaultValue="Base">
                    {["Arbitrum", "Base", "Optimism", "Polygon", "Ethereum"].map(
                      (c) => (
                        <option key={c} value={c} className="bg-[#0f172a]">
                          {c}
                        </option>
                      ),
                    )}
                  </Select>
                </SelectWrap>
              </div>
            </div>

            <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-4">
              <div className="text-[13px] font-medium text-white/90">
                Milestones (placeholder)
              </div>
              <div className="mt-2 text-[12px] text-[color:var(--ff-muted)]">
                You’ll add 3–5 milestones with amounts + acceptance criteria.
              </div>
            </div>

            <div className="pt-2">
              <Button variant="primary" size="lg">
                Create campaign
              </Button>
            </div>
          </div>
        </Card>

        <Card className="p-6 overflow-hidden">
          <CardGlow className="opacity-25" />
          <div className="relative">
            <div className="font-syne font-700 tracking-tight text-[18px]">
              What happens next
            </div>
            <div className="mt-3 space-y-3 text-[13px] text-[color:var(--ff-muted)] leading-relaxed">
              <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3">
                1) You publish campaign details (title, goal, deadline, chain).
              </div>
              <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3">
                2) Backers contribute and automatically earn NFT badges.
              </div>
              <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3">
                3) Funds release milestone-by-milestone as updates are approved.
              </div>
              <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3">
                4) If failure conditions trigger, contributors can claim refunds.
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

