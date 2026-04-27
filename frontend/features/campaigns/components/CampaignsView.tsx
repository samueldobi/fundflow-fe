import CampaignFilters from "@/features/campaigns/components/CampaignFilters";
import CampaignGrid from "@/features/campaigns/components/CampaignGrid";
import { campaigns } from "@/features/campaigns/mock";

export default function CampaignsView() {
  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
      <div className="max-w-2xl">
        <h1 className="font-syne font-700 tracking-tight text-[28px] sm:text-[40px]">
          Campaigns
        </h1>
        <p className="mt-2 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
          Search and filter across categories.
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
