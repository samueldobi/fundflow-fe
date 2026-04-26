import HeroSection from "@/frontend/components/home/Hero";
import About from "@/frontend/components/home/About";
import FeaturedCampaigns from "@/frontend/components/home/FeaturedCampaigns";
import BadgesPreview from "@/frontend/components/home/BadgesPreview";
import CTA from "@/frontend/components/home/CTA";
export default function Home() {
  return (
    <>
      <HeroSection/>
      <About/>
      <FeaturedCampaigns/>
      <BadgesPreview/>
      <CTA/>
    </>
  
    
  );
}
