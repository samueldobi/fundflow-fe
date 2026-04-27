"""
FundFlow — Helper utilities, mock data, and Web3 integration layer.

In production, replace mock data functions with actual Web3 contract calls.
The Web3 integration functions are provided as templates ready for deployment.
"""

import time
import random
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum

# ═══════════════════════════════════════════════════════════════
#                        ENUMS & MODELS
# ═══════════════════════════════════════════════════════════════

class CampaignStatus(IntEnum):
    ACTIVE = 0
    SUCCESSFUL = 1
    FAILED = 2
    CANCELLED = 3

class ContributionTier(IntEnum):
    SUPPORTER = 0
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    PLATINUM = 4
    DIAMOND = 5

TIER_NAMES = ["Supporter", "Bronze", "Silver", "Gold", "Platinum", "Diamond"]
TIER_COLORS = ["#8B9DAF", "#CD7F32", "#C0C0C0", "#FFD700", "#E5E4E2", "#B9F2FF"]
TIER_THRESHOLDS = [0, 0.01, 0.1, 0.5, 1.0, 5.0]  # in ETH

STATUS_LABELS = {
    CampaignStatus.ACTIVE: ("Active", "status-active"),
    CampaignStatus.SUCCESSFUL: ("Funded", "status-successful"),
    CampaignStatus.FAILED: ("Failed", "status-failed"),
    CampaignStatus.CANCELLED: ("Cancelled", "status-failed"),
}

CATEGORIES = [
    "Medical", "Education", "Emergency", "Community",
    "Creative", "Technology", "Environment", "Sports", "Other"
]

CATEGORY_EMOJIS = {
    "Medical": "🏥", "Education": "📚", "Emergency": "🚨",
    "Community": "🤝", "Creative": "🎨", "Technology": "💻",
    "Environment": "🌍", "Sports": "⚽", "Other": "✨"
}

SUPPORTED_NETWORKS = {
    # Testnets
    "Arbitrum Sepolia": {"chain_id": 421614, "rpc": "https://sepolia-rollup.arbitrum.io/rpc", "explorer": "https://sepolia.arbiscan.io", "symbol": "ETH", "color": "#28A0F0"},
    "Base Sepolia": {"chain_id": 84532, "rpc": "https://sepolia.base.org", "explorer": "https://sepolia.basescan.org", "symbol": "ETH", "color": "#0052FF"},
    # Mainnets
    "Arbitrum One": {"chain_id": 42161, "rpc": "https://arb1.arbitrum.io/rpc", "explorer": "https://arbiscan.io", "symbol": "ETH", "color": "#28A0F0"},
    "Base": {"chain_id": 8453, "rpc": "https://mainnet.base.org", "explorer": "https://basescan.org", "symbol": "ETH", "color": "#0052FF"},
    "Optimism": {"chain_id": 10, "rpc": "https://mainnet.optimism.io", "explorer": "https://optimistic.etherscan.io", "symbol": "ETH", "color": "#FF0420"},
    "Polygon": {"chain_id": 137, "rpc": "https://polygon-rpc.com", "explorer": "https://polygonscan.com", "symbol": "MATIC", "color": "#8247E5"},
    "Ethereum": {"chain_id": 1, "rpc": "https://eth.llamarpc.com", "explorer": "https://etherscan.io", "symbol": "ETH", "color": "#627EEA"},
}

# ═══════════════════════════════════════════════════════════════
#                        DATA CLASSES
# ═══════════════════════════════════════════════════════════════

@dataclass
class Milestone:
    description: str
    percentage: int
    completed: bool = False
    funds_released: bool = False

@dataclass
class Contribution:
    contributor: str
    amount: float  # in ETH
    timestamp: int
    message: str = ""
    refunded: bool = False
    tier: int = 0

@dataclass
class Campaign:
    address: str
    creator: str
    title: str
    description: str
    image_uri: str
    category: str
    goal_amount: float  # in ETH
    total_raised: float
    deadline: int
    contributor_count: int
    status: CampaignStatus
    created_at: int
    milestones: list = field(default_factory=list)
    contributions: list = field(default_factory=list)
    endorsements: dict = field(default_factory=dict)
    updates: list = field(default_factory=list)
    network: str = "Arbitrum One"

    @property
    def progress(self) -> float:
        if self.goal_amount == 0:
            return 0
        return min((self.total_raised / self.goal_amount) * 100, 100)

    @property
    def time_remaining(self) -> int:
        remaining = self.deadline - int(time.time())
        return max(remaining, 0)

    @property
    def days_remaining(self) -> int:
        return self.time_remaining // 86400

    @property
    def is_active(self) -> bool:
        return self.status == CampaignStatus.ACTIVE and self.time_remaining > 0

@dataclass
class Badge:
    token_id: int
    campaign_address: str
    campaign_title: str
    amount: float
    tier: int
    minted_at: int

# ═══════════════════════════════════════════════════════════════
#                       UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_tier(amount_eth: float) -> int:
    """Determine contribution tier based on ETH amount."""
    if amount_eth >= 5.0: return ContributionTier.DIAMOND
    if amount_eth >= 1.0: return ContributionTier.PLATINUM
    if amount_eth >= 0.5: return ContributionTier.GOLD
    if amount_eth >= 0.1: return ContributionTier.SILVER
    if amount_eth >= 0.01: return ContributionTier.BRONZE
    return ContributionTier.SUPPORTER

def short_address(addr: str) -> str:
    """Shorten an Ethereum address for display."""
    if len(addr) < 10:
        return addr
    return f"{addr[:6]}...{addr[-4:]}"

def format_eth(amount: float) -> str:
    """Format ETH amount for display."""
    if amount >= 1:
        return f"{amount:.2f}"
    elif amount >= 0.01:
        return f"{amount:.4f}"
    else:
        return f"{amount:.6f}"

def format_time_remaining(seconds: int) -> str:
    """Format remaining time as human-readable string."""
    if seconds <= 0:
        return "Ended"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    if days > 0:
        return f"{days}d {hours}h"
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

def generate_mock_address() -> str:
    """Generate a realistic-looking Ethereum address."""
    return "0x" + hashlib.sha256(str(random.random()).encode()).hexdigest()[:40]

def generate_campaign_image_placeholder(category: str, index: int) -> str:
    """Generate placeholder image URL using a gradient pattern."""
    colors = {
        "Medical": ("6c5ce7", "a29bfe"),
        "Education": ("00b894", "00cec9"),
        "Emergency": ("e17055", "fdcb6e"),
        "Community": ("0984e3", "74b9ff"),
        "Creative": ("e84393", "fd79a8"),
        "Technology": ("6c5ce7", "00cec9"),
        "Environment": ("00b894", "55efc4"),
        "Sports": ("e17055", "ff7675"),
        "Other": ("636e72", "b2bec3"),
    }
    c1, c2 = colors.get(category, ("6c5ce7", "a29bfe"))
    return f"https://placehold.co/600x300/{c1}/{c2}?text={category}+Campaign+{index+1}&font=roboto"


# ═══════════════════════════════════════════════════════════════
#                        MOCK DATA
# ═══════════════════════════════════════════════════════════════

def generate_mock_campaigns() -> list:
    """Generate realistic mock campaign data for the demo."""
    now = int(time.time())
    campaigns = []

    mock_data = [
        {
            "title": "Help Maria's Cancer Treatment",
            "description": "Maria is a 34-year-old mother of two fighting stage 3 breast cancer. Insurance won't cover the experimental immunotherapy her oncologist recommends. Every contribution brings her closer to the treatment she needs. All funds go directly to Memorial Sloan Kettering Cancer Center for her treatment plan.",
            "category": "Medical",
            "goal": 15.0,
            "raised": 11.2,
            "contributors": 87,
            "status": CampaignStatus.ACTIVE,
            "days_offset": 21,
            "network": "Arbitrum One",
        },
        {
            "title": "Build a School in Rural Kenya",
            "description": "Our organization has been working with the Maasai community in Kajiado County for three years. We've secured the land and have government approval. Now we need funding for construction materials, desks, and initial teacher salaries. This school will serve 200+ children who currently walk 15km to the nearest classroom.",
            "category": "Education",
            "goal": 25.0,
            "raised": 25.8,
            "contributors": 142,
            "status": CampaignStatus.SUCCESSFUL,
            "days_offset": -3,
            "network": "Base",
        },
        {
            "title": "Earthquake Relief — Türkiye",
            "description": "A 6.8 magnitude earthquake devastated southeastern Türkiye on December 12th. Thousands of families are displaced and in urgent need of shelter, clean water, and medical supplies. We're partnering with local NGOs to deliver aid directly to affected communities. 100% of funds go to relief supplies — our team operates on separate grants.",
            "category": "Emergency",
            "goal": 50.0,
            "raised": 38.5,
            "contributors": 312,
            "status": CampaignStatus.ACTIVE,
            "days_offset": 14,
            "network": "Arbitrum One",
        },
        {
            "title": "Open Source DeFi Analytics Platform",
            "description": "We're building a free, open-source analytics dashboard for DeFi users. Think Dune Analytics but fully self-hostable, with real-time data across 15+ chains. Our alpha has 2,000+ users. Funds will support 6 months of full-time development for our 3-person team, server costs, and a security audit.",
            "category": "Technology",
            "goal": 30.0,
            "raised": 18.7,
            "contributors": 203,
            "status": CampaignStatus.ACTIVE,
            "days_offset": 35,
            "network": "Optimism",
        },
        {
            "title": "Community Garden & Food Forest — Detroit",
            "description": "Transform a vacant 2-acre lot in East Detroit into a thriving community food forest. We'll plant 50+ fruit and nut trees, install raised beds, and build a teaching pavilion. Free produce for the neighborhood, workshops for kids, and green space for everyone. We have 40 committed volunteers ready to break ground.",
            "category": "Community",
            "goal": 8.0,
            "raised": 6.1,
            "contributors": 64,
            "status": CampaignStatus.ACTIVE,
            "days_offset": 28,
            "network": "Base",
        },
        {
            "title": "Indie Animated Short Film — 'Echoes'",
            "description": "A hand-drawn animated short exploring memory and identity through a deaf protagonist's journey. Our team of 5 animators has completed storyboarding and key frames. We need funding for final animation, sound design, and festival submissions. Selected for Annecy Festival's work-in-progress program.",
            "category": "Creative",
            "goal": 12.0,
            "raised": 4.3,
            "contributors": 58,
            "status": CampaignStatus.ACTIVE,
            "days_offset": 45,
            "network": "Polygon",
        },
        {
            "title": "Ocean Plastic Cleanup — Bali Shores",
            "description": "Deploy 10 autonomous solar-powered trash interceptors along Bali's most polluted river systems. Each unit captures 500kg of plastic per day before it reaches the ocean. We've piloted 2 units successfully. Funding covers manufacturing, deployment, and 1 year of maintenance for the remaining 8 units.",
            "category": "Environment",
            "goal": 40.0,
            "raised": 29.3,
            "contributors": 256,
            "status": CampaignStatus.ACTIVE,
            "days_offset": 18,
            "network": "Arbitrum One",
        },
        {
            "title": "Youth Boxing Academy — South Bronx",
            "description": "Keep at-risk youth off the streets with free after-school boxing training, tutoring, and mentorship. Former champion boxer Marcus Reed has been running this program from a donated garage for 2 years. We need a proper space, equipment, and funding for academic tutors. 85% of participants improved their grades last year.",
            "category": "Sports",
            "goal": 10.0,
            "raised": 10.8,
            "contributors": 91,
            "status": CampaignStatus.SUCCESSFUL,
            "days_offset": -5,
            "network": "Base",
        },
    ]

    for i, data in enumerate(mock_data):
        address = generate_mock_address()
        creator = generate_mock_address()
        deadline = now + (data["days_offset"] * 86400)
        created = now - (random.randint(10, 40) * 86400)

        milestones = [
            Milestone("Initial planning & setup", 20, completed=True, funds_released=True),
            Milestone("Core execution phase", 50, completed=data["raised"] > data["goal"] * 0.5),
            Milestone("Completion & reporting", 30),
        ]

        # Generate some mock contributions
        contributions = []
        contributor_addresses = [generate_mock_address() for _ in range(min(data["contributors"], 15))]
        messages = [
            "Best of luck! 🙏", "You got this!", "Happy to support.",
            "Amazing cause.", "Sharing this with friends!",
            "Keep going!", "Donated in honor of my grandmother.",
            "The world needs more of this.", "Small but from the heart.",
            "Let's make this happen!", "Proud to be part of this.",
            "", "", "", ""  # some empty messages
        ]

        for j, addr in enumerate(contributor_addresses):
            amount = round(random.uniform(0.001, 2.0), 4)
            contributions.append(Contribution(
                contributor=addr,
                amount=amount,
                timestamp=created + random.randint(0, max(1, (deadline - created))),
                message=random.choice(messages),
                tier=get_tier(amount),
            ))

        endorsements = {}
        if random.random() > 0.3:
            for _ in range(random.randint(1, 4)):
                e_addr = generate_mock_address()
                endorsements[e_addr] = random.choice([
                    "I know this team personally. They deliver.",
                    "Verified — the need is real and urgent.",
                    "Worked with the founder before. Top notch.",
                    "This project has my full endorsement.",
                    "The impact per dollar here is incredible.",
                ])

        updates = []
        if data["raised"] > data["goal"] * 0.3:
            updates = [
                {"content": f"Thank you all! We've passed {int(data['raised']/data['goal']*100)}% of our goal!", "timestamp": now - 86400 * 3},
                {"content": "Milestone 1 complete. Detailed report coming soon.", "timestamp": now - 86400 * 7},
            ]

        campaigns.append(Campaign(
            address=address,
            creator=creator,
            title=data["title"],
            description=data["description"],
            image_uri=generate_campaign_image_placeholder(data["category"], i),
            category=data["category"],
            goal_amount=data["goal"],
            total_raised=data["raised"],
            deadline=deadline,
            contributor_count=data["contributors"],
            status=data["status"],
            created_at=created,
            milestones=milestones,
            contributions=contributions,
            endorsements=endorsements,
            updates=updates,
            network=data["network"],
        ))

    return campaigns


def generate_mock_badges(campaigns: list) -> list:
    """Generate mock badge data from campaign contributions."""
    badges = []
    token_id = 0
    for campaign in campaigns:
        for contrib in campaign.contributions[:3]:  # 3 badges per campaign for demo
            badges.append(Badge(
                token_id=token_id,
                campaign_address=campaign.address,
                campaign_title=campaign.title,
                amount=contrib.amount,
                tier=contrib.tier,
                minted_at=contrib.timestamp,
            ))
            token_id += 1
    return badges


# ═══════════════════════════════════════════════════════════════
#                   TOKEN SWAP HELPERS
# ═══════════════════════════════════════════════════════════════

POPULAR_TOKENS = {
    "ETH": {"symbol": "ETH", "name": "Ethereum", "decimals": 18, "icon": "⟠", "price_usd": 3250.0},
    "USDC": {"symbol": "USDC", "name": "USD Coin", "decimals": 6, "icon": "💵", "price_usd": 1.0},
    "USDT": {"symbol": "USDT", "name": "Tether", "decimals": 6, "icon": "💲", "price_usd": 1.0},
    "DAI": {"symbol": "DAI", "name": "Dai", "decimals": 18, "icon": "◈", "price_usd": 1.0},
    "WBTC": {"symbol": "WBTC", "name": "Wrapped Bitcoin", "decimals": 8, "icon": "₿", "price_usd": 97500.0},
    "ARB": {"symbol": "ARB", "name": "Arbitrum", "decimals": 18, "icon": "🔵", "price_usd": 0.82},
    "OP": {"symbol": "OP", "name": "Optimism", "decimals": 18, "icon": "🔴", "price_usd": 1.65},
    "LINK": {"symbol": "LINK", "name": "Chainlink", "decimals": 18, "icon": "⬡", "price_usd": 19.50},
}

def get_swap_quote(from_token: str, to_token: str, amount: float) -> dict:
    """
    Get a mock swap quote. In production, integrate with:
    - 1inch API (https://1inch.dev/)
    - 0x API (https://0x.org/docs/api)
    - Uniswap Router contract directly
    """
    if amount <= 0:
        return {"output": 0, "rate": 0, "fee": 0, "price_impact": 0}

    from_price = POPULAR_TOKENS.get(from_token, {}).get("price_usd", 1)
    to_price = POPULAR_TOKENS.get(to_token, {}).get("price_usd", 1)

    if to_price == 0:
        return {"output": 0, "rate": 0, "fee": 0, "price_impact": 0}

    rate = from_price / to_price
    output = amount * rate
    fee = output * 0.003  # 0.3% swap fee
    output_after_fee = output - fee

    # Mock price impact based on amount
    usd_value = amount * from_price
    price_impact = min(usd_value * 0.0001, 5.0)  # caps at 5%

    return {
        "output": round(output_after_fee, 6),
        "rate": round(rate, 6),
        "fee": round(fee, 6),
        "fee_usd": round(fee * to_price, 2),
        "price_impact": round(price_impact, 2),
        "gas_estimate": round(random.uniform(0.0002, 0.001), 6),
    }


# ═══════════════════════════════════════════════════════════════
#                   WEB3 INTEGRATION (TEMPLATES)
# ═══════════════════════════════════════════════════════════════

"""
Production Web3 integration guide:

1. Install: pip install web3
2. Connect to RPC:
   from web3 import Web3
   w3 = Web3(Web3.HTTPProvider(SUPPORTED_NETWORKS["Arbitrum One"]["rpc"]))

3. Load contract:
   factory = w3.eth.contract(address=FACTORY_ADDRESS, abi=FACTORY_ABI)

4. Read campaigns:
   all_campaigns = factory.functions.getAllCampaigns().call()
   for addr in all_campaigns:
       campaign = w3.eth.contract(address=addr, abi=CAMPAIGN_ABI)
       info = campaign.functions.getCampaignInfo().call()

5. Write transactions (requires wallet connection):
   - Use Streamlit + JavaScript injection for MetaMask
   - Or use private key signing for server-side transactions

6. Token swaps:
   - Integrate Uniswap V3 SwapRouter
   - Or use 1inch/0x aggregator APIs for better rates

Example MetaMask connection (inject into Streamlit):
   import streamlit.components.v1 as components
   components.html('''
       <script>
       async function connectWallet() {
           const accounts = await window.ethereum.request({
               method: 'eth_requestAccounts'
           });
           // Send account back to Streamlit via query params
           window.parent.postMessage({type: 'wallet', account: accounts[0]}, '*');
       }
       </script>
       <button onclick="connectWallet()">Connect Wallet</button>
   ''')
"""