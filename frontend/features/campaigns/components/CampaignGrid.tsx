import CampaignCard from "@/features/campaigns/components/CampaignCard";
import type { Campaign } from "@/features/campaigns/mock";

export default function CampaignGrid({ items }: { items: Campaign[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((campaign) => (
        <CampaignCard key={campaign.id} campaign={campaign} />
      ))}
    </div>
  );
}
