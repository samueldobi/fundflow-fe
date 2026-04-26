import CampaignFilters from "@/frontend/features/campaigns/components/CampaignFilters";
import CampaignGrid from "@/frontend/features/campaigns/components/CampaignGrid";
import { campaigns } from "@/frontend/features/campaigns/mock";

export default function CampaignsView() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
      <div className="max-w-2xl">
        <h1 className="font-syne font-700 tracking-tight text-[28px] sm:text-[40px]">
          Campaigns
        </h1>
        <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
          Search and filter across categories. This list is currently mocked to
          focus on UI.
        </p>
      </div>

      <div className="mt-8">
        <CampaignFilters />
      </div>

      <div className="mt-6">
        <CampaignGrid items={campaigns} />
      </div>
    </div>
  );
}

