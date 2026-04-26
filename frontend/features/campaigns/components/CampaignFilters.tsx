import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Input, Label } from "@/components/ui/Input";
import { Select, SelectWrap } from "@/components/ui/Select";

const categories = [
  "All",
  "Medical",
  "Education",
  "Emergency",
  "Community",
  "Climate",
  "Open Source",
] as const;

export default function CampaignFilters() {
  return (
    <Card className="p-5">
      <div className="flex flex-col md:flex-row md:items-end gap-4">
        <div className="flex-1">
          <Label htmlFor="q">Search</Label>
          <Input id="q" placeholder="Search campaigns, creators, keywords..." />
        </div>

        <div className="w-full md:w-[260px]">
          <Label htmlFor="category">Category</Label>
          <SelectWrap>
            <Select id="category" defaultValue="All">
              {categories.map((c) => (
                <option key={c} value={c} className="bg-[#0f172a]">
                  {c}
                </option>
              ))}
            </Select>
          </SelectWrap>
        </div>

        <div className="w-full md:w-[220px]">
          <Label htmlFor="status">Status</Label>
          <SelectWrap>
            <Select id="status" defaultValue="In Progress">
              <option value="In Progress" className="bg-[#0f172a]">
                In Progress
              </option>
              <option value="Completed" className="bg-[#0f172a]">
                Completed
              </option>
              <option value="Failed" className="bg-[#0f172a]">
                Failed
              </option>
            </Select>
          </SelectWrap>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <Badge variant="green">Milestone-based</Badge>
        <Badge variant="purple">NFT badges</Badge>
        <Badge variant="neutral">Refunds</Badge>
        <Badge variant="neutral">Verified endorsements</Badge>
      </div>
    </Card>
  );
}
