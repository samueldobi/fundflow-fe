import { ButtonLink } from "@/components/ui/Button";
import CampaignGrid from "@/features/campaigns/components/CampaignGrid";
import { campaigns } from "@/features/campaigns/mock";

export default function FeaturedCampaigns() {
  return (
    <section className="py-16 sm:py-20">
      <div className="max-w-7xl mx-auto px-6 lg:px-10">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
          <div className="max-w-2xl">
            <h2 className="font-syne font-700 tracking-tight text-[28px] sm:text-[36px]">
              Featured campaigns
            </h2>
            <p className="mt-3 text-[15px] leading-relaxed text-[color:var(--ff-muted)]">
              Browse active campaigns across Medical, Education, Emergency, and
              Community.
            </p>
          </div>
          <ButtonLink href="/campaigns" variant="secondary">
            View all
          </ButtonLink>
        </div>

        <div className="mt-10">
          <CampaignGrid items={campaigns.slice(0, 3)} />
        </div>
      </div>
    </section>
  );
}
