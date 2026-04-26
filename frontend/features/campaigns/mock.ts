export type CampaignCategory =
  | "Medical"
  | "Education"
  | "Emergency"
  | "Community"
  | "Climate"
  | "Open Source";

export type CampaignStatus = "In Progress" | "Completed" | "Failed";

export type Campaign = {
  id: string;
  title: string;
  description: string;
  category: CampaignCategory;
  status: CampaignStatus;
  goalUsd: number;
  raisedUsd: number;
  backers: number;
  daysLeft: number;
};

export const campaigns: Campaign[] = [
  {
    id: "clean-water-001",
    title: "Clean Water for 3 Rural Communities",
    description:
      "Milestone-based fundraising for boreholes, filtration, and maintenance training.",
    category: "Community",
    status: "In Progress",
    goalUsd: 50000,
    raisedUsd: 32480,
    backers: 1204,
    daysLeft: 12,
  },
  {
    id: "edtech-scholarship-002",
    title: "Web3 Scholarship Cohort (100 Learners)",
    description:
      "Structured track covering wallets, on-chain safety, and smart contract basics.",
    category: "Education",
    status: "In Progress",
    goalUsd: 30000,
    raisedUsd: 21400,
    backers: 834,
    daysLeft: 19,
  },
  {
    id: "medical-surgery-003",
    title: "Urgent Surgery & Recovery Support",
    description:
      "Transparent contributions with updates and verified endorsements from doctors.",
    category: "Medical",
    status: "In Progress",
    goalUsd: 18000,
    raisedUsd: 15650,
    backers: 642,
    daysLeft: 6,
  },
  {
    id: "opensource-grants-004",
    title: "Open-source Grants for Public Goods",
    description:
      "Fund maintainers with milestone releases and transparent progress tracking.",
    category: "Open Source",
    status: "Completed",
    goalUsd: 40000,
    raisedUsd: 40000,
    backers: 2011,
    daysLeft: 0,
  },
  {
    id: "emergency-relief-005",
    title: "Emergency Relief: Rapid Response Fund",
    description:
      "Fast disbursement milestones with on-chain proofs and contributor refunds if unmet.",
    category: "Emergency",
    status: "Failed",
    goalUsd: 25000,
    raisedUsd: 8600,
    backers: 309,
    daysLeft: 0,
  },
  {
    id: "climate-tree-006",
    title: "Plant 10,000 Mangrove Trees",
    description:
      "Community-led restoration with milestone-based reporting and photo updates.",
    category: "Climate",
    status: "In Progress",
    goalUsd: 22000,
    raisedUsd: 13120,
    backers: 512,
    daysLeft: 27,
  },
];

