import CampaignDetail from "@/frontend/features/campaigns/components/CampaignDetail";

export default async function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CampaignDetail id={id} />;
}

