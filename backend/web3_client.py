"""
╔═══════════════════════════════════════════════════════════════╗
║   FundFlow — Web3 Integration Layer                           ║
║   Reads chain data via Web3.py, constructs tx for MetaMask    ║
╚═══════════════════════════════════════════════════════════════╝

Usage:
    1. Set FACTORY_ADDRESS in config.py after deploying
    2. The client reads all campaign data from chain
    3. Write transactions are encoded and sent to MetaMask via JS
"""

import json
import os
import logging
from pathlib import Path
from typing import Optional
from web3 import Web3
from web3.exceptions import ContractLogicError

from helpers import (
    Campaign, Milestone, Contribution, Badge,
    CampaignStatus, get_tier, SUPPORTED_NETWORKS,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
#                       CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# --- EDIT THESE AFTER DEPLOYMENT ---
FACTORY_ADDRESS = os.getenv("FACTORY_ADDRESS", "")  # Set after deploying
ACTIVE_NETWORK = os.getenv("ACTIVE_NETWORK", "Arbitrum Sepolia")

# Testnet RPCs (free, no API key needed)
NETWORK_RPCS = {
    "Arbitrum Sepolia": "https://sepolia-rollup.arbitrum.io/rpc",
    "Base Sepolia": "https://sepolia.base.org",
    "Sepolia": "https://rpc.sepolia.org",
    # Mainnets (add when ready)
    "Arbitrum One": "https://arb1.arbitrum.io/rpc",
    "Base": "https://mainnet.base.org",
    "Optimism": "https://mainnet.optimism.io",
}

# Chain IDs for MetaMask
CHAIN_IDS = {
    "Arbitrum Sepolia": 421614,
    "Base Sepolia": 84532,
    "Sepolia": 11155111,
    "Arbitrum One": 42161,
    "Base": 8453,
    "Optimism": 10,
}

# ═══════════════════════════════════════════════════════════════
#                       ABI LOADING
# ═══════════════════════════════════════════════════════════════

ABI_DIR = Path(__file__).parent / "abi"

def load_abi(name: str) -> list:
    """Load ABI from JSON file."""
    abi_path = ABI_DIR / f"{name}.json"
    with open(abi_path) as f:
        return json.load(f)

FACTORY_ABI = load_abi("CrowdfundFactory")
CAMPAIGN_ABI = load_abi("CrowdfundCampaign")
BADGE_ABI = load_abi("ContributorBadge")


# ═══════════════════════════════════════════════════════════════
#                     WEB3 CONNECTION
# ═══════════════════════════════════════════════════════════════

class FundFlowClient:
    """
    Web3 client for reading FundFlow contract data.
    
    Reads are done server-side via Web3.py.
    Writes are encoded as tx data and sent to MetaMask via JS injection.
    """

    def __init__(self, network: str = None, factory_address: str = None):
        self.network = network or ACTIVE_NETWORK
        self.factory_address = factory_address or FACTORY_ADDRESS
        self.w3 = None
        self.factory = None
        self.badge_address = None
        self.badge_contract = None
        self._connected = False

        if self.factory_address and self.network:
            self._connect()

    def _connect(self):
        """Establish Web3 connection and load factory contract."""
        rpc_url = NETWORK_RPCS.get(self.network)
        if not rpc_url:
            logger.error(f"No RPC URL for network: {self.network}")
            return

        try:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
            if not self.w3.is_connected():
                logger.error(f"Cannot connect to {self.network} RPC")
                return

            self.factory = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.factory_address),
                abi=FACTORY_ABI,
            )

            # Load badge NFT address from factory
            try:
                self.badge_address = self.factory.functions.badgeNFT().call()
                self.badge_contract = self.w3.eth.contract(
                    address=self.badge_address,
                    abi=BADGE_ABI,
                )
            except Exception as e:
                logger.warning(f"Could not load badge contract: {e}")

            self._connected = True
            logger.info(f"Connected to {self.network} | Factory: {self.factory_address}")

        except Exception as e:
            logger.error(f"Web3 connection failed: {e}")
            self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self.w3 is not None and self.w3.is_connected()

    @property
    def chain_id(self) -> int:
        return CHAIN_IDS.get(self.network, 1)

    # ═══════════════════════════════════════════════════════════
    #                   READ: CAMPAIGNS
    # ═══════════════════════════════════════════════════════════

    def get_all_campaign_addresses(self) -> list[str]:
        """Get all campaign contract addresses from factory."""
        if not self.is_connected:
            return []
        try:
            return self.factory.functions.getAllCampaigns().call()
        except Exception as e:
            logger.error(f"Error fetching campaigns: {e}")
            return []

    def get_campaign_count(self) -> int:
        """Get total number of campaigns."""
        if not self.is_connected:
            return 0
        try:
            return self.factory.functions.getCampaignCount().call()
        except Exception as e:
            logger.error(f"Error fetching campaign count: {e}")
            return 0

    def get_campaign(self, campaign_address: str) -> Optional[Campaign]:
        """Fetch full campaign data from a campaign contract."""
        if not self.is_connected:
            return None

        try:
            addr = Web3.to_checksum_address(campaign_address)
            contract = self.w3.eth.contract(address=addr, abi=CAMPAIGN_ABI)

            # getCampaignInfo() returns a tuple
            info = contract.functions.getCampaignInfo().call()
            (
                creator, title, description, image_uri, category,
                goal_amount, total_raised, deadline, contributor_count,
                status, created_at
            ) = info

            # Fetch milestones
            raw_milestones = contract.functions.getMilestones().call()
            milestones = [
                Milestone(
                    description=ms[0],
                    percentage=ms[1],
                    completed=ms[2],
                    funds_released=ms[3],
                )
                for ms in raw_milestones
            ]

            # Fetch contributions
            raw_contribs = contract.functions.getContributions().call()
            contributions = [
                Contribution(
                    contributor=c[0],
                    amount=self.w3.from_wei(c[1], "ether"),
                    timestamp=c[2],
                    message=c[3],
                    refunded=c[4],
                    tier=get_tier(float(self.w3.from_wei(c[1], "ether"))),
                )
                for c in raw_contribs
            ]

            # Fetch endorsements
            endorsements = {}
            try:
                endorser_addrs = contract.functions.getEndorsers().call()
                for e_addr in endorser_addrs:
                    msg = contract.functions.endorsements(e_addr).call()
                    if msg:
                        endorsements[e_addr] = msg
            except Exception:
                pass  # endorsements are optional

            # Fetch updates
            updates = []
            try:
                update_contents, update_timestamps = contract.functions.getUpdates().call()
                for content, ts in zip(update_contents, update_timestamps):
                    updates.append({"content": content, "timestamp": ts})
            except Exception:
                pass

            return Campaign(
                address=campaign_address,
                creator=creator,
                title=title,
                description=description,
                image_uri=image_uri,
                category=category,
                goal_amount=float(self.w3.from_wei(goal_amount, "ether")),
                total_raised=float(self.w3.from_wei(total_raised, "ether")),
                deadline=deadline,
                contributor_count=contributor_count,
                status=CampaignStatus(status),
                created_at=created_at,
                milestones=milestones,
                contributions=contributions,
                endorsements=endorsements,
                updates=updates,
                network=self.network,
            )

        except Exception as e:
            logger.error(f"Error fetching campaign {campaign_address}: {e}")
            return None

    def get_all_campaigns(self) -> list[Campaign]:
        """Fetch all campaigns with full data."""
        addresses = self.get_all_campaign_addresses()
        campaigns = []
        for addr in addresses:
            campaign = self.get_campaign(addr)
            if campaign:
                campaigns.append(campaign)
        return campaigns

    def get_campaigns_by_category(self, category: str) -> list[str]:
        """Get campaign addresses filtered by category."""
        if not self.is_connected:
            return []
        try:
            return self.factory.functions.getCampaignsByCategory(category).call()
        except Exception as e:
            logger.error(f"Error fetching by category: {e}")
            return []

    def get_campaigns_by_creator(self, creator: str) -> list[str]:
        """Get campaign addresses created by a specific address."""
        if not self.is_connected:
            return []
        try:
            addr = Web3.to_checksum_address(creator)
            return self.factory.functions.getCampaignsByCreator(addr).call()
        except Exception as e:
            logger.error(f"Error fetching by creator: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    #                    READ: BADGES
    # ═══════════════════════════════════════════════════════════

    def get_badges_for_owner(self, owner: str) -> list[Badge]:
        """Fetch all badge NFTs owned by an address."""
        if not self.is_connected or not self.badge_contract:
            return []

        try:
            addr = Web3.to_checksum_address(owner)
            token_ids = self.badge_contract.functions.getBadgesByOwner(addr).call()

            badges = []
            for tid in token_ids:
                raw = self.badge_contract.functions.badges(tid).call()
                badges.append(Badge(
                    token_id=tid,
                    campaign_address=raw[0],
                    campaign_title=raw[1],
                    amount=float(self.w3.from_wei(raw[2], "ether")),
                    tier=raw[3],
                    minted_at=raw[4],
                ))
            return badges

        except Exception as e:
            logger.error(f"Error fetching badges for {owner}: {e}")
            return []

    def get_badge_total_supply(self) -> int:
        """Get total number of badges minted."""
        if not self.is_connected or not self.badge_contract:
            return 0
        try:
            return self.badge_contract.functions.totalSupply().call()
        except Exception:
            return 0

    # ═══════════════════════════════════════════════════════════
    #                   READ: WALLET INFO
    # ═══════════════════════════════════════════════════════════

    def get_balance(self, address: str) -> float:
        """Get ETH balance for an address."""
        if not self.is_connected:
            return 0.0
        try:
            addr = Web3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(addr)
            return float(self.w3.from_wei(balance_wei, "ether"))
        except Exception:
            return 0.0

    def get_contributor_total(self, campaign_address: str, contributor: str) -> float:
        """Get total contribution by an address to a specific campaign."""
        if not self.is_connected:
            return 0.0
        try:
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(campaign_address),
                abi=CAMPAIGN_ABI,
            )
            total_wei = contract.functions.contributorTotals(
                Web3.to_checksum_address(contributor)
            ).call()
            return float(self.w3.from_wei(total_wei, "ether"))
        except Exception:
            return 0.0

    # ═══════════════════════════════════════════════════════════
    #            WRITE: ENCODE TX DATA FOR METAMASK
    # ═══════════════════════════════════════════════════════════
    #
    # These methods encode transaction data that gets sent to
    # MetaMask via JavaScript injection. The user signs in their
    # browser — we never touch private keys.
    # ═══════════════════════════════════════════════════════════

    def encode_create_campaign(
        self,
        title: str,
        description: str,
        goal_wei: int,
        duration_days: int,
        category: str,
        milestones: list[str],
        milestone_percentages: list[int],
        image_uri: str,
    ) -> dict:
        """Encode createCampaign transaction for MetaMask signing."""
        tx_data = self.factory.encode_abi(
            "createCampaign",
            [
                title, description, goal_wei, duration_days,
                category, milestones, milestone_percentages, image_uri,
            ]
        )
        return {
            "to": self.factory_address,
            "data": tx_data,
            "value": "0x0",
            "chainId": hex(self.chain_id),
        }

    def encode_contribute(self, campaign_address: str, message: str, value_wei: int) -> dict:
        """Encode contribute transaction for MetaMask signing."""
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(campaign_address),
            abi=CAMPAIGN_ABI,
        )
        tx_data = contract.encode_abi("contribute", [message])
        return {
            "to": campaign_address,
            "data": tx_data,
            "value": hex(value_wei),
            "chainId": hex(self.chain_id),
        }

    def encode_endorse(self, campaign_address: str, message: str) -> dict:
        """Encode endorse transaction for MetaMask signing."""
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(campaign_address),
            abi=CAMPAIGN_ABI,
        )
        tx_data = contract.encode_abi("endorse", [message])
        return {
            "to": campaign_address,
            "data": tx_data,
            "value": "0x0",
            "chainId": hex(self.chain_id),
        }

    def encode_complete_milestone(self, campaign_address: str) -> dict:
        """Encode completeMilestone transaction."""
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(campaign_address),
            abi=CAMPAIGN_ABI,
        )
        tx_data = contract.encode_abi("completeMilestone")
        return {
            "to": campaign_address,
            "data": tx_data,
            "value": "0x0",
            "chainId": hex(self.chain_id),
        }

    def encode_withdraw_milestone(self, campaign_address: str) -> dict:
        """Encode withdrawMilestone transaction."""
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(campaign_address),
            abi=CAMPAIGN_ABI,
        )
        tx_data = contract.encode_abi("withdrawMilestone")
        return {
            "to": campaign_address,
            "data": tx_data,
            "value": "0x0",
            "chainId": hex(self.chain_id),
        }

    def encode_claim_refund(self, campaign_address: str) -> dict:
        """Encode claimRefund transaction."""
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(campaign_address),
            abi=CAMPAIGN_ABI,
        )
        tx_data = contract.encode_abi("claimRefund")
        return {
            "to": campaign_address,
            "data": tx_data,
            "value": "0x0",
            "chainId": hex(self.chain_id),
        }

    def encode_cancel_campaign(self, campaign_address: str) -> dict:
        """Encode cancelCampaign transaction."""
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(campaign_address),
            abi=CAMPAIGN_ABI,
        )
        tx_data = contract.encode_abi("cancelCampaign")
        return {
            "to": campaign_address,
            "data": tx_data,
            "value": "0x0",
            "chainId": hex(self.chain_id),
        }

    def encode_post_update(self, campaign_address: str, content: str) -> dict:
        """Encode postUpdate transaction."""
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(campaign_address),
            abi=CAMPAIGN_ABI,
        )
        tx_data = contract.encode_abi("postUpdate", [content])
        return {
            "to": campaign_address,
            "data": tx_data,
            "value": "0x0",
            "chainId": hex(self.chain_id),
        }

    def wei(self, eth_amount: float) -> int:
        """Convert ETH to Wei."""
        return self.w3.to_wei(eth_amount, "ether")