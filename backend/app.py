"""
╔═══════════════════════════════════════════════════════════════╗
║   FundFlow — On-Chain Crowdfunding Platform                   ║
║   "The GoFundMe killer, built on L2s"                        ║
╚═══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import time
import random
import textwrap
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from helpers import (
    Campaign, Badge, CampaignStatus, ContributionTier,
    TIER_NAMES, TIER_COLORS, CATEGORIES, CATEGORY_EMOJIS,
    SUPPORTED_NETWORKS, POPULAR_TOKENS, STATUS_LABELS,
    generate_mock_campaigns, generate_mock_badges,
    get_swap_quote, get_tier, short_address, format_eth,
    format_time_remaining, generate_mock_address,
)

from config import USE_CHAIN_DATA, FACTORY_ADDRESS, ACTIVE_NETWORK

# Import MetaMask + Web3 components
try:
    from web3_client import FundFlowClient
    from metamask_component import (
        render_wallet_connect, render_network_switch,
        render_send_transaction, render_contribute_button,
        render_endorse_button, render_faucet_link,
    )
    WEB3_AVAILABLE = True
except ImportError as e:
    WEB3_AVAILABLE = False
    if USE_CHAIN_DATA:
        import warnings
        warnings.warn(f"Web3 dependencies not installed: {e}. Run: pip install web3")

# ═══════════════════════════════════════════════════════════════
#                      PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="FundFlow — On-Chain Crowdfunding",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
# with open("assets/style.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
with open("assets/style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Helper: Render HTML without indentation issues ────────────
# Streamlit treats 4-space indentation as code blocks.
# This helper strips leading whitespace before rendering.
def _html(text: str):
    """Render HTML via st.markdown with all leading whitespace stripped."""
    # Strip leading whitespace from EVERY line — not just common prefix.
    # Streamlit treats 4-space indentation as code blocks.
    lines = text.strip().split('\n')
    cleaned = '\n'.join(line.lstrip() for line in lines)
    st.markdown(cleaned, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#                     SESSION STATE
# ═══════════════════════════════════════════════════════════════

# Initialize Web3 client if using chain data
if "web3_client" not in st.session_state:
    if USE_CHAIN_DATA and FACTORY_ADDRESS and WEB3_AVAILABLE:
        st.session_state.web3_client = FundFlowClient(
            network=ACTIVE_NETWORK,
            factory_address=FACTORY_ADDRESS,
        )
    else:
        st.session_state.web3_client = None

if "campaigns" not in st.session_state:
    client = st.session_state.web3_client
    if client and client.is_connected:
        # Load real campaigns from chain
        st.session_state.campaigns = client.get_all_campaigns()
    else:
        # Fallback to mock data
        st.session_state.campaigns = generate_mock_campaigns()

if "badges" not in st.session_state:
    st.session_state.badges = generate_mock_badges(st.session_state.campaigns)
if "connected_wallet" not in st.session_state:
    st.session_state.connected_wallet = None
if "selected_network" not in st.session_state:
    st.session_state.selected_network = ACTIVE_NETWORK if USE_CHAIN_DATA else "Arbitrum One"
if "current_page" not in st.session_state:
    st.session_state.current_page = "discover"
if "selected_campaign_idx" not in st.session_state:
    st.session_state.selected_campaign_idx = None
if "data_mode" not in st.session_state:
    st.session_state.data_mode = "chain" if (USE_CHAIN_DATA and st.session_state.web3_client and st.session_state.web3_client.is_connected) else "mock"


# ═══════════════════════════════════════════════════════════════
#                       SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        # Logo / Brand
        _html("""
        <div style="text-align:center; padding: 1rem 0 1.5rem;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 800;
                        background: linear-gradient(135deg, #6c5ce7, #a29bfe); -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent; letter-spacing: -0.03em;">
                🌊 FundFlow
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: #5c6184;
                        text-transform: uppercase; letter-spacing: 0.15em; margin-top: 0.25rem;">
                On-Chain Crowdfunding
            </div>
        </div>
        """)

        _html("---")

        # Network selector
        _html("""
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #5c6184;
                    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
            ⛓️ Network
        </div>
        """)

        network = st.selectbox(
            "Select Network",
            list(SUPPORTED_NETWORKS.keys()),
            index=list(SUPPORTED_NETWORKS.keys()).index(st.session_state.selected_network),
            label_visibility="collapsed",
            key="network_selector",
        )
        st.session_state.selected_network = network

        net_info = SUPPORTED_NETWORKS[network]
        _html(f"""
        <div class="network-pill">
            <div class="network-dot"></div>
            {network} · Chain {net_info['chain_id']}
        </div>
        """)

        _html("<br>")

        # Wallet connection
        _html("""
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #5c6184;
                    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
            👛 Wallet
        </div>
        """)

        if st.session_state.connected_wallet:
            wallet = st.session_state.connected_wallet
            # Show connected state
            balance = 0.0
            if st.session_state.web3_client and st.session_state.web3_client.is_connected:
                balance = st.session_state.web3_client.get_balance(wallet)
            _html(f"""
            <div style="background: rgba(0,230,118,0.06); border: 1px solid rgba(0,230,118,0.15);
                        border-radius: 10px; padding: 0.8rem; text-align: center;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00e676;">
                    ✅ {short_address(wallet)}
                </div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 0.7rem; color: #5c6184; margin-top: 0.3rem;">
                    Balance: {format_eth(balance)} ETH
                </div>
            </div>
            """)
            if st.button("Disconnect", use_container_width=True, key="disconnect_btn"):
                st.session_state.connected_wallet = None
                st.rerun()
        else:
            # Wallet input - user pastes their MetaMask address
            _html("""
            <div style="font-family: 'Outfit', sans-serif; font-size: 0.75rem; color: #5c6184; margin-bottom: 0.3rem;">
                Paste your wallet address from MetaMask:
            </div>
            """)
            wallet_input = st.text_input(
                "Wallet address",
                placeholder="0x...",
                label_visibility="collapsed",
                key="wallet_input",
            )
            if st.button("🔗 Connect", use_container_width=True, key="connect_btn"):
                if wallet_input and wallet_input.startswith("0x") and len(wallet_input) == 42:
                    st.session_state.connected_wallet = wallet_input
                    st.rerun()
                else:
                    st.warning("Enter a valid 0x... address (42 characters)")

        # MetaMask JS for signing transactions (works in iframe)
        if USE_CHAIN_DATA and WEB3_AVAILABLE:
            render_faucet_link(ACTIVE_NETWORK, height=40)

        # Data mode indicator
        mode_color = "#00e676" if st.session_state.data_mode == "chain" else "#ffab00"
        mode_label = "🟢 Live Chain Data" if st.session_state.data_mode == "chain" else "🟡 Demo Mode"
        _html(f"""
        <div style="text-align: center; margin-top: 0.5rem; font-family: 'JetBrains Mono', monospace;
                    font-size: 0.6rem; color: {mode_color};">
            {mode_label}
        </div>
        """)

        # Refresh chain data button (only in chain mode)
        if st.session_state.data_mode == "chain":
            if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_data"):
                client = st.session_state.web3_client
                if client and client.is_connected:
                    st.session_state.campaigns = client.get_all_campaigns()
                    if st.session_state.connected_wallet:
                        st.session_state.badges = client.get_badges_for_owner(st.session_state.connected_wallet)
                    st.rerun()

        _html("---")

        # Navigation
        _html("""
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #5c6184;
                    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
            Navigation
        </div>
        """)

        nav_items = {
            "discover": "🔍  Discover",
            "create": "➕  Create Campaign",
            "dashboard": "📊  My Dashboard",
            "swap": "🔄  Token Swap",
            "badges": "🏅  NFT Badges",
        }

        for key, label in nav_items.items():
            is_active = st.session_state.current_page == key
            if st.button(
                label,
                use_container_width=True,
                key=f"nav_{key}",
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = key
                st.session_state.selected_campaign_idx = None
                st.rerun()

        _html("---")

        # Platform stats
        campaigns = st.session_state.campaigns
        total_raised = sum(c.total_raised for c in campaigns)
        total_contributors = sum(c.contributor_count for c in campaigns)

        _html(f"""
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #5c6184;
                    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;">
            Platform Stats
        </div>
        <div style="display: grid; gap: 0.6rem;">
            <div style="background: rgba(108,92,231,0.06); border-radius: 8px; padding: 0.6rem 0.8rem;">
                <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 700; color: #e8eaf6;">
                    {format_eth(total_raised)} ETH
                </div>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184; text-transform: uppercase;">
                    Total Raised
                </div>
            </div>
            <div style="background: rgba(0,230,118,0.06); border-radius: 8px; padding: 0.6rem 0.8rem;">
                <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 700; color: #e8eaf6;">
                    {total_contributors:,}
                </div>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184; text-transform: uppercase;">
                    Contributors
                </div>
            </div>
            <div style="background: rgba(255,171,0,0.06); border-radius: 8px; padding: 0.6rem 0.8rem;">
                <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 700; color: #e8eaf6;">
                    {len(campaigns)}
                </div>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184; text-transform: uppercase;">
                    Active Campaigns
                </div>
            </div>
        </div>
        """)

        _html("<br>")
        _html("""
        <div style="text-align: center; padding: 0.5rem;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #3a3f5c;">
                Built with ❤️ on L2s
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.5rem; color: #2a2f4c; margin-top: 0.2rem;">
                v0.1.0-alpha
            </div>
        </div>
        """)


# ═══════════════════════════════════════════════════════════════
#                    CAMPAIGN CARD COMPONENT
# ═══════════════════════════════════════════════════════════════

def render_campaign_card(campaign: Campaign, idx: int):
    """Render a single campaign card."""
    progress = campaign.progress
    status_label, status_class = STATUS_LABELS[campaign.status]
    emoji = CATEGORY_EMOJIS.get(campaign.category, "✨")
    progress_class = "success" if progress >= 100 else ""
    net_color = SUPPORTED_NETWORKS.get(campaign.network, {}).get("color", "#6c5ce7")

    _html(f"""
    <div class="campaign-card" style="animation: fadeInUp 0.5s ease forwards; animation-delay: {idx * 0.08}s; opacity: 0;">
        <div style="height: 8px; background: linear-gradient(90deg, {net_color}, {net_color}88); opacity: 0.7;"></div>
        <div class="campaign-card-body">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                <span class="campaign-card-category">{emoji} {campaign.category}</span>
                <span class="{status_class}">{status_label}</span>
            </div>
            <div class="campaign-card-title">{campaign.title}</div>
            <div class="campaign-card-desc">{campaign.description[:120]}...</div>

            <div class="progress-container">
                <div class="progress-fill {progress_class}" style="width: {min(progress, 100)}%;"></div>
            </div>

            <div class="campaign-stats">
                <div class="campaign-stat-item">
                    <div class="campaign-stat-value">{format_eth(campaign.total_raised)} ETH</div>
                    <div class="campaign-stat-label">of {format_eth(campaign.goal_amount)} ETH</div>
                </div>
                <div class="campaign-stat-item">
                    <div class="campaign-stat-value">{campaign.contributor_count}</div>
                    <div class="campaign-stat-label">Backers</div>
                </div>
                <div class="campaign-stat-item">
                    <div class="campaign-stat-value">{format_time_remaining(campaign.time_remaining)}</div>
                    <div class="campaign-stat-label">Remaining</div>
                </div>
            </div>

            <div style="margin-top: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: {net_color};">
                    {campaign.network}
                </span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #5c6184;">
                    {int(progress)}% funded
                </span>
            </div>
        </div>
    </div>
    """)


# ═══════════════════════════════════════════════════════════════
#                    PAGE: DISCOVER
# ═══════════════════════════════════════════════════════════════

def page_discover():
    campaigns = st.session_state.campaigns

    # Hero section
    _html("""
    <div class="hero-container">
        <div class="hero-title">Fund what matters.<br>On-chain. Transparent. Global.</div>
        <div class="hero-subtitle">
            FundFlow is the decentralized crowdfunding platform built on Layer 2s.
            No borders. No middlemen. Just people helping people — with every transaction
            verified on the blockchain.
        </div>
    </div>
    """)

    # Quick stats bar
    total_raised = sum(c.total_raised for c in campaigns)
    total_backers = sum(c.contributor_count for c in campaigns)
    funded_count = sum(1 for c in campaigns if c.status == CampaignStatus.SUCCESSFUL)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _html(f"""
        <div class="stat-card">
            <div class="stat-value">{format_eth(total_raised)}</div>
            <div class="stat-label">ETH Raised</div>
        </div>""")
    with c2:
        _html(f"""
        <div class="stat-card">
            <div class="stat-value">{total_backers:,}</div>
            <div class="stat-label">Total Backers</div>
        </div>""")
    with c3:
        _html(f"""
        <div class="stat-card">
            <div class="stat-value">{len(campaigns)}</div>
            <div class="stat-label">Campaigns</div>
        </div>""")
    with c4:
        _html(f"""
        <div class="stat-card">
            <div class="stat-value">{funded_count}</div>
            <div class="stat-label">Fully Funded</div>
        </div>""")

    _html("<br>")

    # Filters
    _html("""
    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700;
                color: #e8eaf6; margin-bottom: 0.25rem;">
        Discover Campaigns
    </div>
    <div style="font-family: 'Outfit', sans-serif; font-size: 0.9rem; color: #5c6184; margin-bottom: 1.5rem;">
        Browse and support causes that matter to you
    </div>
    """)

    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        search = st.text_input("🔍 Search campaigns", placeholder="Search by title or description...", label_visibility="collapsed")
    with fc2:
        category_filter = st.selectbox("Category", ["All Categories"] + CATEGORIES, label_visibility="collapsed")
    with fc3:
        sort_by = st.selectbox("Sort by", ["Trending", "Newest", "Most Funded", "Ending Soon"], label_visibility="collapsed")

    # Filter campaigns
    filtered = campaigns
    if search:
        search_lower = search.lower()
        filtered = [c for c in filtered if search_lower in c.title.lower() or search_lower in c.description.lower()]
    if category_filter != "All Categories":
        filtered = [c for c in filtered if c.category == category_filter]

    # Sort
    if sort_by == "Most Funded":
        filtered.sort(key=lambda c: c.total_raised, reverse=True)
    elif sort_by == "Newest":
        filtered.sort(key=lambda c: c.created_at, reverse=True)
    elif sort_by == "Ending Soon":
        filtered.sort(key=lambda c: c.time_remaining)
    else:  # Trending — mix of raised amount and contributor count
        filtered.sort(key=lambda c: c.total_raised * c.contributor_count, reverse=True)

    # Render campaign grid
    if not filtered:
        _html("""
        <div style="text-align: center; padding: 3rem; color: #5c6184;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
            <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; color: #9fa8da;">No campaigns found</div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">Try adjusting your filters or search terms</div>
        </div>
        """)
        return

    # Grid layout: 3 columns
    for row_start in range(0, len(filtered), 3):
        cols = st.columns(3)
        for col_idx, col in enumerate(cols):
            campaign_idx = row_start + col_idx
            if campaign_idx < len(filtered):
                campaign = filtered[campaign_idx]
                with col:
                    render_campaign_card(campaign, campaign_idx)
                    # Find original index for navigation
                    original_idx = campaigns.index(campaign)
                    if st.button(
                        "View Details →",
                        key=f"view_{original_idx}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_campaign_idx = original_idx
                        st.session_state.current_page = "campaign_detail"
                        st.rerun()
                    _html("<br>")


# ═══════════════════════════════════════════════════════════════
#                  PAGE: CAMPAIGN DETAIL
# ═══════════════════════════════════════════════════════════════

def page_campaign_detail():
    idx = st.session_state.selected_campaign_idx
    if idx is None or idx >= len(st.session_state.campaigns):
        st.session_state.current_page = "discover"
        st.rerun()
        return

    campaign = st.session_state.campaigns[idx]
    status_label, status_class = STATUS_LABELS[campaign.status]
    emoji = CATEGORY_EMOJIS.get(campaign.category, "✨")
    net_color = SUPPORTED_NETWORKS.get(campaign.network, {}).get("color", "#6c5ce7")
    progress = campaign.progress

    # Back button
    if st.button("← Back to Discover", key="back_btn"):
        st.session_state.current_page = "discover"
        st.session_state.selected_campaign_idx = None
        st.rerun()

    _html("<br>")

    # Campaign header
    _html(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
        <span class="campaign-card-category">{emoji} {campaign.category}</span>
        <span class="{status_class}">{status_label}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: {net_color};
                     background: {net_color}15; padding: 0.2rem 0.6rem; border-radius: 20px;">
            ⛓️ {campaign.network}
        </span>
    </div>
    """)

    _html(f"""
    <div style="font-family: 'Space Grotesk'; font-size: 2.2rem; font-weight: 700; color: #e8eaf6;
                line-height: 1.2; margin-bottom: 0.5rem;">
        {campaign.title}
    </div>
    <div style="font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #5c6184;">
        by {short_address(campaign.creator)} · Created {datetime.fromtimestamp(campaign.created_at).strftime('%b %d, %Y')}
    </div>
    """)

    _html("<br>")

    # Main layout: 2 columns
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        # Description
        _html(f"""
        <div style="background: #141622; border: 1px solid #1e2235; border-radius: 16px; padding: 1.5rem;">
            <div style="font-family: 'Space Grotesk'; font-size: 1rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.75rem;">
                About this Campaign
            </div>
            <div style="font-family: 'Outfit'; font-size: 0.9rem; color: #9fa8da; line-height: 1.7;">
                {campaign.description}
            </div>
        </div>
        """)

        _html("<br>")

        # Tabs: milestones, contributions, updates, endorsements
        tab1, tab2, tab3, tab4 = st.tabs(["📍 Milestones", "💰 Contributions", "📢 Updates", "🤝 Endorsements"])

        with tab1:
            for i, ms in enumerate(campaign.milestones):
                icon = "✅" if ms.completed else "⏳" if i == 0 else "⬜"
                released = " · Funds Released" if ms.funds_released else ""
                color = "#00e676" if ms.completed else "#5c6184"
                _html(f"""
                <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem 0;
                            border-bottom: 1px solid #1e2235;">
                    <span style="font-size: 1.2rem;">{icon}</span>
                    <div>
                        <div style="font-family: 'Space Grotesk'; font-size: 0.9rem; color: {color}; font-weight: 500;">
                            Milestone {i+1}: {ms.description}
                        </div>
                        <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184; margin-top: 0.2rem;">
                            {ms.percentage}% of funds{released}
                        </div>
                    </div>
                </div>
                """)

        with tab2:
            if campaign.contributions:
                for contrib in sorted(campaign.contributions, key=lambda c: c.timestamp, reverse=True)[:15]:
                    tier_name = TIER_NAMES[contrib.tier]
                    tier_color = TIER_COLORS[contrib.tier]
                    msg = f' — "{contrib.message}"' if contrib.message else ""
                    dt = datetime.fromtimestamp(contrib.timestamp).strftime("%b %d, %H:%M")
                    _html(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center;
                                padding: 0.6rem 0; border-bottom: 1px solid #1e223522;">
                        <div>
                            <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #9fa8da;">
                                {short_address(contrib.contributor)}
                            </span>
                            <span style="font-family: 'Outfit'; font-size: 0.8rem; color: #5c6184;">{msg}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-family: 'Space Grotesk'; font-size: 0.85rem; font-weight: 600; color: #e8eaf6;">
                                {format_eth(contrib.amount)} ETH
                            </div>
                            <div style="font-family: 'JetBrains Mono'; font-size: 0.55rem; color: {tier_color};">
                                {tier_name} · {dt}
                            </div>
                        </div>
                    </div>
                    """)
            else:
                st.info("No contributions yet. Be the first!")

        with tab3:
            if campaign.updates:
                for upd in reversed(campaign.updates):
                    dt = datetime.fromtimestamp(upd["timestamp"]).strftime("%b %d, %Y")
                    _html(f"""
                    <div style="background: #0f1118; border-left: 3px solid #6c5ce7;
                                border-radius: 0 10px 10px 0; padding: 1rem 1.25rem; margin-bottom: 0.75rem;">
                        <div style="font-family: 'Outfit'; font-size: 0.9rem; color: #9fa8da; line-height: 1.5;">
                            {upd["content"]}
                        </div>
                        <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184; margin-top: 0.5rem;">
                            {dt}
                        </div>
                    </div>
                    """)
            else:
                st.info("No updates posted yet.")

        with tab4:
            if campaign.endorsements:
                for addr, msg in campaign.endorsements.items():
                    _html(f"""
                    <div class="endorsement-card">
                        <div class="endorsement-text">"{msg}"</div>
                        <div class="endorsement-author">— {short_address(addr)}</div>
                    </div>
                    """)
            else:
                st.info("No endorsements yet.")

    with right_col:
        # Funding progress card
        progress_color = "#00e676" if progress >= 100 else "#6c5ce7"
        _html(f"""
        <div style="background: #141622; border: 1px solid #1e2235; border-radius: 16px; padding: 1.5rem;">
            <div style="font-family: 'Space Grotesk'; font-size: 2rem; font-weight: 700; color: #e8eaf6;">
                {format_eth(campaign.total_raised)} <span style="font-size: 1rem; color: #5c6184;">ETH</span>
            </div>
            <div style="font-family: 'Outfit'; font-size: 0.85rem; color: #5c6184; margin-bottom: 1rem;">
                raised of {format_eth(campaign.goal_amount)} ETH goal
            </div>

            <div class="progress-container" style="height: 10px; margin-bottom: 1rem;">
                <div class="progress-fill" style="width: {min(progress, 100)}%; background: linear-gradient(90deg, {progress_color}, {progress_color}aa);"></div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; margin-bottom: 1.5rem;">
                <div style="text-align: center;">
                    <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 700; color: #e8eaf6;">
                        {int(progress)}%
                    </div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184; text-transform: uppercase;">
                        Funded
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 700; color: #e8eaf6;">
                        {campaign.contributor_count}
                    </div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184; text-transform: uppercase;">
                        Backers
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 700; color: #e8eaf6;">
                        {format_time_remaining(campaign.time_remaining)}
                    </div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184; text-transform: uppercase;">
                        Left
                    </div>
                </div>
            </div>
        </div>
        """)

        _html("<br>")

        # Contribute form
        _html("""
        <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.5rem;">
            💎 Back This Campaign
        </div>
        """)

        with st.container():
            amount = st.number_input(
                "Amount (ETH)",
                min_value=0.001,
                max_value=100.0,
                value=0.1,
                step=0.01,
                format="%.4f",
                key="contribute_amount",
            )
            message = st.text_input("Message (optional)", placeholder="Leave a message of support...", key="contribute_msg")

            tier = get_tier(amount)
            tier_name = TIER_NAMES[tier]
            tier_color = TIER_COLORS[tier]

            _html(f"""
            <div style="background: rgba(108,92,231,0.06); border-radius: 8px; padding: 0.6rem 0.8rem;
                        margin: 0.5rem 0; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'Outfit'; font-size: 0.8rem; color: #9fa8da;">Your badge tier:</span>
                <span style="font-family: 'Space Grotesk'; font-weight: 700; color: {tier_color};">
                    🏅 {tier_name}
                </span>
            </div>
            """)

            if campaign.is_active:
                if USE_CHAIN_DATA and st.session_state.data_mode == "chain":
                    # Real MetaMask transaction
                    client = st.session_state.web3_client
                    if client and client.is_connected:
                        tx_data = client.encode_contribute(
                            campaign_address=campaign.address,
                            message=message or "",
                            value_wei=client.wei(amount),
                        )
                        render_contribute_button(tx_data, amount, height=160)
                    else:
                        st.error("Web3 client not connected")
                else:
                    # Mock transaction for demo mode
                    if st.button("🚀 Contribute Now", use_container_width=True, key="contribute_btn"):
                        if not st.session_state.connected_wallet:
                            st.warning("Please connect your wallet first!")
                        else:
                            with st.spinner("Processing transaction..."):
                                time.sleep(1.5)  # Simulate tx
                            st.success(f"🎉 Successfully contributed {format_eth(amount)} ETH!")
                            st.balloons()
            else:
                _html("""
                <div style="background: rgba(255,82,82,0.1); border-radius: 10px; padding: 0.75rem;
                            text-align: center; font-family: 'Outfit'; font-size: 0.85rem; color: #ff5252;">
                    This campaign is no longer accepting contributions
                </div>
                """)

        _html("<br>")

        # Share & endorse
        _html("""
        <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.5rem;">
            🤝 Endorse Campaign
        </div>
        """)
        endorse_msg = st.text_area("Your endorsement", placeholder="Share why you trust this campaign...", key="endorse_msg", height=80)
        if USE_CHAIN_DATA and st.session_state.data_mode == "chain":
            if endorse_msg:
                client = st.session_state.web3_client
                if client and client.is_connected:
                    tx_data = client.encode_endorse(
                        campaign_address=campaign.address,
                        message=endorse_msg,
                    )
                    render_endorse_button(tx_data, height=120)
            else:
                st.caption("Write your endorsement above to submit")
        else:
            if st.button("Submit Endorsement", use_container_width=True, key="endorse_btn"):
                if not st.session_state.connected_wallet:
                    st.warning("Please connect your wallet first!")
                elif not endorse_msg:
                    st.warning("Please write an endorsement message.")
                else:
                    st.success("✅ Endorsement submitted!")

        _html("<br>")

        # ── Campaign Creator Controls ─────────────────────────────
        # Only visible if connected wallet is the campaign creator
        wallet = st.session_state.connected_wallet
        is_creator = wallet and wallet.lower() == campaign.creator.lower()

        if is_creator:
            _html("""
            <div style="background: linear-gradient(135deg, rgba(108,92,231,0.1), rgba(0,230,118,0.05));
                        border: 1px solid #6c5ce7; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.25rem;">
                    ⚙️ Campaign Management
                </div>
                <div style="font-family: 'Outfit'; font-size: 0.75rem; color: #5c6184; margin-bottom: 1rem;">
                    You are the creator of this campaign
                </div>
            </div>
            """)

            # Show current milestone status
            if campaign.milestones:
                # Find the milestone that needs action:
                # Priority 1: completed but NOT withdrawn yet → show withdraw button
                # Priority 2: not completed yet → show complete button
                current_ms_idx = None
                needs_withdraw = False

                for i, ms in enumerate(campaign.milestones):
                    if ms.completed and not ms.funds_released:
                        current_ms_idx = i
                        needs_withdraw = True
                        break
                if current_ms_idx is None:
                    for i, ms in enumerate(campaign.milestones):
                        if not ms.completed:
                            current_ms_idx = i
                            needs_withdraw = False
                            break

                all_withdrawn = all(ms.funds_released for ms in campaign.milestones)

                if all_withdrawn:
                    _html("""
                    <div style="background: rgba(0,230,118,0.08); border: 1px solid rgba(0,230,118,0.2);
                                border-radius: 10px; padding: 0.8rem; text-align: center; margin-bottom: 0.75rem;">
                        <div style="font-family: 'Space Grotesk'; font-size: 0.9rem; color: #00e676;">
                            ✅ All milestones completed & funds withdrawn
                        </div>
                    </div>
                    """)
                elif current_ms_idx is not None:
                    current_ms = campaign.milestones[current_ms_idx]
                    ms_status = "✅ Completed" if current_ms.completed else "⏳ Pending"
                    ms_funds = "💸 Withdrawn" if current_ms.funds_released else "🔒 Locked"
                    _html(f"""
                    <div style="background: #141622; border: 1px solid #1e2235; border-radius: 10px;
                                padding: 0.8rem; margin-bottom: 0.75rem;">
                        <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184;
                                    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem;">
                            Current Milestone ({current_ms_idx + 1}/{len(campaign.milestones)})
                        </div>
                        <div style="font-family: 'Space Grotesk'; font-size: 0.95rem; color: #e8eaf6; font-weight: 600;">
                            {current_ms.description}
                        </div>
                        <div style="font-family: 'Outfit'; font-size: 0.8rem; color: #9fa8da; margin-top: 0.3rem;">
                            {current_ms.percentage}% of funds · {ms_status} · {ms_funds}
                        </div>
                    </div>
                    """)

                    client = st.session_state.web3_client

                    if needs_withdraw:
                        # Step 2: Withdraw funds for completed milestone
                        pct = current_ms.percentage
                        est_amount = campaign.total_raised * (pct / 100)
                        _html(f"""
                        <div style="font-family: 'Outfit'; font-size: 0.8rem; color: #00e676; margin-bottom: 0.3rem;">
                            Milestone completed! Withdraw {pct}% of funds (~{format_eth(est_amount)} ETH):
                        </div>
                        """)
                        if client and client.is_connected:
                            tx_data = client.encode_withdraw_milestone(campaign.address)
                            render_send_transaction(
                                tx_data=tx_data,
                                label=f"💸 Withdraw Milestone {current_ms_idx + 1} ({pct}%)",
                                tx_label="Milestone Withdrawal",
                                height=140,
                            )
                    else:
                        # Step 1: Complete milestone
                        _html(f"""
                        <div style="font-family: 'Outfit'; font-size: 0.8rem; color: #9fa8da; margin-bottom: 0.3rem;">
                            Mark milestone "{current_ms.description}" as complete:
                        </div>
                        """)
                        if client and client.is_connected:
                            tx_data = client.encode_complete_milestone(campaign.address)
                            render_send_transaction(
                                tx_data=tx_data,
                                label=f"✅ Complete Milestone {current_ms_idx + 1}",
                                tx_label="Milestone Completion",
                                height=140,
                            )
                        else:
                            st.warning("Web3 not connected")

                    # Refresh tip
                    _html("""
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184; margin-top: 0.3rem;">
                        💡 After completing a transaction, click "🔄 Refresh Data" in the sidebar to see updated state.
                    </div>
                    """)

            _html("<br>")

            # Post update
            _html("""
            <div style="font-family: 'Space Grotesk'; font-size: 0.95rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.3rem;">
                📢 Post Update
            </div>
            """)
            update_content = st.text_area("Update content", placeholder="Share progress with your backers...", key="update_content", height=70)
            if update_content:
                client = st.session_state.web3_client
                if client and client.is_connected:
                    tx_data = client.encode_post_update(campaign.address, update_content)
                    render_send_transaction(
                        tx_data=tx_data,
                        label="📢 Post Update",
                        tx_label="Campaign Update",
                        height=120,
                    )

            _html("<br>")

            # Cancel campaign (only if no funds withdrawn)
            with st.expander("⚠️ Cancel Campaign"):
                st.warning("Cancelling allows all contributors to claim refunds. This cannot be undone.")
                if campaign.status == CampaignStatus.ACTIVE or campaign.status == CampaignStatus.SUCCESSFUL:
                    client = st.session_state.web3_client
                    if client and client.is_connected:
                        tx_data = client.encode_cancel_campaign(campaign.address)
                        render_send_transaction(
                            tx_data=tx_data,
                            label="❌ Cancel Campaign",
                            tx_label="Campaign Cancellation",
                            height=120,
                        )

        # ── Contributor Controls (refund if failed/cancelled) ─────
        elif wallet and campaign.status in (CampaignStatus.FAILED, CampaignStatus.CANCELLED):
            _html("""
            <div style="background: rgba(255,82,82,0.08); border: 1px solid rgba(255,82,82,0.2);
                        border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 600; color: #ff5252; margin-bottom: 0.5rem;">
                    🔄 Claim Refund
                </div>
                <div style="font-family: 'Outfit'; font-size: 0.8rem; color: #9fa8da; margin-bottom: 0.75rem;">
                    This campaign has been cancelled/failed. You can reclaim your contribution.
                </div>
            </div>
            """)
            client = st.session_state.web3_client
            if client and client.is_connected:
                tx_data = client.encode_claim_refund(campaign.address)
                render_send_transaction(
                    tx_data=tx_data,
                    label="🔄 Claim Refund",
                    tx_label="Refund",
                    height=140,
                )

        _html("<br>")

        # Contract info
        explorer = SUPPORTED_NETWORKS.get(campaign.network, {}).get("explorer", "")
        _html(f"""
        <div style="background: #0f1118; border: 1px solid #1e2235; border-radius: 10px; padding: 1rem;">
            <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184; text-transform: uppercase;
                        letter-spacing: 0.08em; margin-bottom: 0.5rem;">
                Contract Details
            </div>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #9fa8da; word-break: break-all;">
                {campaign.address}
            </div>
            <div style="font-family: 'Outfit'; font-size: 0.75rem; color: #6c5ce7; margin-top: 0.5rem;">
                <a href="{explorer}/address/{campaign.address}" target="_blank" style="color: #6c5ce7; text-decoration: none;">
                    View on Explorer ↗
                </a>
            </div>
        </div>
        """)


# ═══════════════════════════════════════════════════════════════
#                   PAGE: CREATE CAMPAIGN
# ═══════════════════════════════════════════════════════════════

def page_create():
    _html("""
    <div style="font-family: 'Space Grotesk'; font-size: 2rem; font-weight: 700; color: #e8eaf6; margin-bottom: 0.25rem;">
        ➕ Create a Campaign
    </div>
    <div style="font-family: 'Outfit'; font-size: 0.9rem; color: #5c6184; margin-bottom: 2rem;">
        Launch your crowdfunding campaign on the blockchain. All contributions are transparent and verifiable.
    </div>
    """)

    if not st.session_state.connected_wallet:
        _html("""
        <div style="background: rgba(255,171,0,0.08); border: 1px solid rgba(255,171,0,0.2);
                    border-radius: 16px; padding: 2rem; text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">👛</div>
            <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #ffab00;">
                Connect your wallet to create a campaign
            </div>
            <div style="font-family: 'Outfit'; font-size: 0.85rem; color: #5c6184; margin-top: 0.5rem;">
                Use the sidebar to connect your wallet
            </div>
        </div>
        """)
        return

    with st.form("create_campaign_form"):
        _html("""
        <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.5rem;">
            Campaign Details
        </div>
        """)

        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Campaign Title *", placeholder="Give your campaign a clear, compelling title")
            category = st.selectbox("Category *", CATEGORIES)
            goal = st.number_input("Funding Goal (ETH) *", min_value=0.01, max_value=10000.0, value=1.0, step=0.1)
        with c2:
            duration = st.slider("Duration (days) *", 1, 365, 30)
            network = st.selectbox("Deploy Network", list(SUPPORTED_NETWORKS.keys()))
            image_url = st.text_input("Campaign Image URL", placeholder="https://... or IPFS hash")

        description = st.text_area(
            "Campaign Description *",
            placeholder="Describe your campaign in detail. What are you raising funds for? How will the money be used? Why should people support this?",
            height=150,
        )

        _html("<br>")
        _html("""
        <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.5rem;">
            Milestones
        </div>
        <div style="font-family: 'Outfit'; font-size: 0.8rem; color: #5c6184; margin-bottom: 0.75rem;">
            Funds are released as you complete milestones. Percentages must total 100%.
        </div>
        """)

        mc1, mc2 = st.columns([3, 1])
        with mc1:
            ms1_desc = st.text_input("Milestone 1 *", value="Planning & Setup", key="ms1_desc")
            ms2_desc = st.text_input("Milestone 2 *", value="Core Execution", key="ms2_desc")
            ms3_desc = st.text_input("Milestone 3 *", value="Completion & Reporting", key="ms3_desc")
        with mc2:
            ms1_pct = st.number_input("% Funds", value=20, min_value=1, max_value=99, key="ms1_pct")
            ms2_pct = st.number_input("% Funds", value=50, min_value=1, max_value=99, key="ms2_pct")
            ms3_pct = st.number_input("% Funds", value=30, min_value=1, max_value=99, key="ms3_pct")

        total_pct = ms1_pct + ms2_pct + ms3_pct
        if total_pct != 100:
            st.warning(f"⚠️ Milestone percentages sum to {total_pct}%. They must total 100%.")

        _html("<br>")

        # Cost breakdown
        fee_pct = 1.5
        est_gas = 0.002  # estimated gas for contract deployment

        _html(f"""
        <div style="background: #0f1118; border: 1px solid #1e2235; border-radius: 12px; padding: 1rem;">
            <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184; text-transform: uppercase;
                        letter-spacing: 0.08em; margin-bottom: 0.5rem;">
                Cost Breakdown
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; font-family: 'Outfit'; font-size: 0.85rem;">
                <span style="color: #9fa8da;">Platform Fee</span>
                <span style="color: #e8eaf6;">{fee_pct}% of raised amount</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; font-family: 'Outfit'; font-size: 0.85rem;">
                <span style="color: #9fa8da;">Est. Deploy Gas</span>
                <span style="color: #e8eaf6;">~{est_gas} ETH</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; font-family: 'Outfit'; font-size: 0.85rem;">
                <span style="color: #9fa8da;">Network</span>
                <span style="color: #e8eaf6;">{network}</span>
            </div>
        </div>
        """)

        _html("<br>")

        submitted = st.form_submit_button("🚀 Launch Campaign", use_container_width=True)

        if submitted:
            if not title or not description:
                st.error("Please fill in all required fields.")
            elif total_pct != 100:
                st.error("Milestone percentages must sum to 100%.")
            else:
                if USE_CHAIN_DATA and st.session_state.data_mode == "chain":
                    client = st.session_state.web3_client
                    if client and client.is_connected:
                        tx_data = client.encode_create_campaign(
                            title=title,
                            description=description,
                            goal_wei=client.wei(goal),
                            duration_days=duration,
                            category=category,
                            milestones=[ms1_desc, ms2_desc, ms3_desc],
                            milestone_percentages=[ms1_pct, ms2_pct, ms3_pct],
                            image_uri=image_url or "",
                        )
                        _html("<br>")
                        render_send_transaction(
                            tx_data=tx_data,
                            label="Deploy Campaign Contract",
                            tx_label="Campaign Deployment",
                            height=200,
                        )
                    else:
                        st.error("Web3 client not connected. Check config.py settings.")
                else:
                    with st.spinner("Deploying campaign contract..."):
                        time.sleep(2)
                    st.success("🎉 Campaign created successfully!")
                    st.balloons()
                    _html(f"""
                    <div style="background: rgba(0,230,118,0.08); border: 1px solid rgba(0,230,118,0.2);
                                border-radius: 12px; padding: 1.2rem; margin-top: 1rem;">
                        <div style="font-family: 'Space Grotesk'; font-size: 1rem; font-weight: 600; color: #00e676;">
                            Campaign Deployed! 🎯
                        </div>
                        <div style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #9fa8da; margin-top: 0.5rem;">
                            Contract: {generate_mock_address()}
                        </div>
                        <div style="font-family: 'Outfit'; font-size: 0.8rem; color: #5c6184; margin-top: 0.3rem;">
                            Share this campaign to start receiving contributions!
                        </div>
                    </div>
                    """)


# ═══════════════════════════════════════════════════════════════
#                    PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════

def page_dashboard():
    _html("""
    <div style="font-family: 'Space Grotesk'; font-size: 2rem; font-weight: 700; color: #e8eaf6; margin-bottom: 0.25rem;">
        📊 My Dashboard
    </div>
    <div style="font-family: 'Outfit'; font-size: 0.9rem; color: #5c6184; margin-bottom: 2rem;">
        Track your campaigns and contributions
    </div>
    """)

    if not st.session_state.connected_wallet:
        _html("""
        <div style="background: rgba(255,171,0,0.08); border: 1px solid rgba(255,171,0,0.2);
                    border-radius: 16px; padding: 2rem; text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">👛</div>
            <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #ffab00;">
                Connect your wallet to view your dashboard
            </div>
        </div>
        """)
        return

    # Mock dashboard data
    my_campaigns = st.session_state.campaigns[:2]  # pretend user created first 2
    my_contributions_total = 2.45
    my_badges_count = len(st.session_state.badges[:8])

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("My Campaigns", len(my_campaigns))
    with c2:
        st.metric("Total Contributed", f"{my_contributions_total} ETH")
    with c3:
        st.metric("NFT Badges", my_badges_count)
    with c4:
        st.metric("Campaigns Backed", 6)

    _html("<br>")

    tab1, tab2, tab3 = st.tabs(["📋 My Campaigns", "💰 My Contributions", "📈 Analytics"])

    with tab1:
        for campaign in my_campaigns:
            status_label, status_class = STATUS_LABELS[campaign.status]
            progress = campaign.progress
            _html(f"""
            <div style="background: #141622; border: 1px solid #1e2235; border-radius: 16px;
                        padding: 1.25rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 600; color: #e8eaf6;">
                        {campaign.title}
                    </div>
                    <span class="{status_class}">{status_label}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-fill" style="width: {min(progress, 100)}%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;
                            font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #5c6184;">
                    <span>{format_eth(campaign.total_raised)} / {format_eth(campaign.goal_amount)} ETH</span>
                    <span>{campaign.contributor_count} backers</span>
                    <span>{format_time_remaining(campaign.time_remaining)} left</span>
                </div>
            </div>
            """)

    with tab2:
        # Mock contribution history
        mock_contribs = [
            {"campaign": "Earthquake Relief — Türkiye", "amount": 0.5, "date": "Jan 15, 2026", "tier": "Gold"},
            {"campaign": "Open Source DeFi Analytics", "amount": 1.0, "date": "Jan 10, 2026", "tier": "Platinum"},
            {"campaign": "Help Maria's Cancer Treatment", "amount": 0.25, "date": "Jan 5, 2026", "tier": "Silver"},
            {"campaign": "Community Garden — Detroit", "amount": 0.1, "date": "Dec 28, 2025", "tier": "Silver"},
            {"campaign": "Ocean Plastic Cleanup — Bali", "amount": 0.5, "date": "Dec 20, 2025", "tier": "Gold"},
            {"campaign": "Youth Boxing Academy", "amount": 0.1, "date": "Dec 15, 2025", "tier": "Silver"},
        ]

        for c in mock_contribs:
            tier_idx = TIER_NAMES.index(c["tier"]) if c["tier"] in TIER_NAMES else 0
            tier_color = TIER_COLORS[tier_idx]
            _html(f"""
            <div style="display: flex; justify-content: space-between; align-items: center;
                        padding: 0.75rem 0; border-bottom: 1px solid #1e223522;">
                <div>
                    <div style="font-family: 'Space Grotesk'; font-size: 0.9rem; font-weight: 500; color: #e8eaf6;">
                        {c["campaign"]}
                    </div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184;">{c["date"]}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-family: 'Space Grotesk'; font-size: 0.9rem; font-weight: 600; color: #e8eaf6;">
                        {c["amount"]} ETH
                    </div>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: {tier_color};">
                        🏅 {c["tier"]}
                    </div>
                </div>
            </div>
            """)

    with tab3:
        # Contribution over time chart
        dates = [datetime.now() - timedelta(days=x) for x in range(90, 0, -1)]
        cumulative = [0]
        for i in range(1, len(dates)):
            bump = random.uniform(0, 0.08) if random.random() > 0.6 else 0
            cumulative.append(cumulative[-1] + bump)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=cumulative,
            mode='lines',
            fill='tozeroy',
            line=dict(color='#6c5ce7', width=2),
            fillcolor='rgba(108,92,231,0.1)',
        ))
        fig.update_layout(
            title="My Contribution History",
            title_font=dict(family="Space Grotesk", size=16, color="#e8eaf6"),
            xaxis_title="", yaxis_title="Cumulative ETH",
            plot_bgcolor="#08090d", paper_bgcolor="#08090d",
            font=dict(color="#9fa8da", family="Outfit"),
            xaxis=dict(gridcolor="#1e2235", linecolor="#1e2235"),
            yaxis=dict(gridcolor="#1e2235", linecolor="#1e2235"),
            margin=dict(l=20, r=20, t=50, b=20),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Category breakdown
        cat_data = {"Medical": 0.75, "Technology": 1.0, "Emergency": 0.5, "Community": 0.1, "Environment": 0.1}
        fig2 = go.Figure(data=[go.Pie(
            labels=list(cat_data.keys()),
            values=list(cat_data.values()),
            hole=0.55,
            marker=dict(colors=["#6c5ce7", "#00e676", "#ffab00", "#18ffff", "#e84393"]),
            textfont=dict(color="#e8eaf6", family="Outfit"),
        )])
        fig2.update_layout(
            title="Contributions by Category",
            title_font=dict(family="Space Grotesk", size=16, color="#e8eaf6"),
            plot_bgcolor="#08090d", paper_bgcolor="#08090d",
            font=dict(color="#9fa8da", family="Outfit"),
            margin=dict(l=20, r=20, t=50, b=20),
            height=350,
            showlegend=True,
            legend=dict(font=dict(color="#9fa8da")),
        )
        st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#                    PAGE: TOKEN SWAP
# ═══════════════════════════════════════════════════════════════

def page_swap():
    _html("""
    <div style="font-family: 'Space Grotesk'; font-size: 2rem; font-weight: 700; color: #e8eaf6; margin-bottom: 0.25rem;">
        🔄 Token Swap
    </div>
    <div style="font-family: 'Outfit'; font-size: 0.9rem; color: #5c6184; margin-bottom: 2rem;">
        Swap tokens instantly before contributing. Powered by DEX aggregation.
    </div>
    """)

    # Center the swap widget
    _, center, _ = st.columns([1, 2, 1])

    with center:
        _html("""
        <div class="swap-container">
            <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #e8eaf6;
                        text-align: center; margin-bottom: 1.5rem;">
                Swap Tokens
            </div>
        </div>
        """)

        # From token
        _html("""
        <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184;
                    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem;">
            You Pay
        </div>
        """)

        fc1, fc2 = st.columns([2, 1])
        with fc1:
            from_amount = st.number_input(
                "Amount", min_value=0.0, value=1.0, step=0.1,
                format="%.6f", key="swap_from_amount", label_visibility="collapsed"
            )
        with fc2:
            token_list = list(POPULAR_TOKENS.keys())
            from_token = st.selectbox("From", token_list, index=0, key="swap_from_token", label_visibility="collapsed")

        from_usd = from_amount * POPULAR_TOKENS[from_token]["price_usd"]
        _html(f"""
        <div style="font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #5c6184; margin: -0.5rem 0 0.5rem 0.2rem;">
            ≈ ${from_usd:,.2f}
        </div>
        """)

        # Swap direction arrow
        _html("""
        <div style="text-align: center; font-size: 1.5rem; color: #6c5ce7; margin: 0.5rem 0; cursor: pointer;">
            ⇅
        </div>
        """)

        # To token
        _html("""
        <div style="font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #5c6184;
                    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem;">
            You Receive
        </div>
        """)

        tc1, tc2 = st.columns([2, 1])
        with tc2:
            to_token = st.selectbox("To", token_list, index=1, key="swap_to_token", label_visibility="collapsed")

        # Get quote
        quote = get_swap_quote(from_token, to_token, from_amount)

        with tc1:
            _html(f"""
            <div style="background: #0f1118; border: 1px solid #1e2235; border-radius: 10px; padding: 0.75rem;
                        font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #e8eaf6;">
                {quote['output']:.6f}
            </div>
            """)

        to_usd = quote["output"] * POPULAR_TOKENS[to_token]["price_usd"]
        _html(f"""
        <div style="font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #5c6184; margin: 0.3rem 0 1rem 0.2rem;">
            ≈ ${to_usd:,.2f}
        </div>
        """)

        # Quote details
        if from_amount > 0 and from_token != to_token:
            impact_color = "#00e676" if quote["price_impact"] < 1 else "#ffab00" if quote["price_impact"] < 3 else "#ff5252"
            _html(f"""
            <div style="background: #0f1118; border: 1px solid #1e2235; border-radius: 10px; padding: 0.8rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;
                            font-family: 'Outfit'; font-size: 0.8rem;">
                    <span style="color: #5c6184;">Rate</span>
                    <span style="color: #9fa8da;">1 {from_token} = {quote['rate']:.6f} {to_token}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;
                            font-family: 'Outfit'; font-size: 0.8rem;">
                    <span style="color: #5c6184;">Swap Fee (0.3%)</span>
                    <span style="color: #9fa8da;">{quote['fee']:.6f} {to_token} (${quote['fee_usd']:.2f})</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;
                            font-family: 'Outfit'; font-size: 0.8rem;">
                    <span style="color: #5c6184;">Price Impact</span>
                    <span style="color: {impact_color};">{quote['price_impact']}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 0.25rem 0;
                            font-family: 'Outfit'; font-size: 0.8rem;">
                    <span style="color: #5c6184;">Est. Gas</span>
                    <span style="color: #9fa8da;">~{quote['gas_estimate']} ETH</span>
                </div>
            </div>
            """)

        if st.button("🔄 Swap Tokens", use_container_width=True, key="swap_btn"):
            if not st.session_state.connected_wallet:
                st.warning("Please connect your wallet first!")
            elif from_token == to_token:
                st.warning("Please select different tokens.")
            elif from_amount <= 0:
                st.warning("Please enter an amount.")
            else:
                with st.spinner("Executing swap..."):
                    time.sleep(1.5)
                st.success(f"✅ Swapped {from_amount} {from_token} → {quote['output']:.6f} {to_token}")

        # DEX info
        _html("""
        <div style="text-align: center; margin-top: 1rem; font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #3a3f5c;">
            Powered by Uniswap V3 · Best route via DEX aggregation
        </div>
        """)


# ═══════════════════════════════════════════════════════════════
#                    PAGE: NFT BADGES
# ═══════════════════════════════════════════════════════════════

def page_badges():
    _html("""
    <div style="font-family: 'Space Grotesk'; font-size: 2rem; font-weight: 700; color: #e8eaf6; margin-bottom: 0.25rem;">
        🏅 NFT Contribution Badges
    </div>
    <div style="font-family: 'Outfit'; font-size: 0.9rem; color: #5c6184; margin-bottom: 2rem;">
        Every contribution earns you an on-chain badge. Collect them all!
    </div>
    """)

    if not st.session_state.connected_wallet:
        _html("""
        <div style="background: rgba(255,171,0,0.08); border: 1px solid rgba(255,171,0,0.2);
                    border-radius: 16px; padding: 2rem; text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">👛</div>
            <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #ffab00;">
                Connect your wallet to view your badges
            </div>
        </div>
        """)
        return

    # Tier explanation
    _html("""
    <div style="background: #141622; border: 1px solid #1e2235; border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 600; color: #e8eaf6; margin-bottom: 0.75rem;">
            Badge Tiers
        </div>
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
    """)

    tier_thresholds = ["< 0.01 ETH", "0.01+ ETH", "0.1+ ETH", "0.5+ ETH", "1+ ETH", "5+ ETH"]
    tier_html = ""
    for i, (name, color, thresh) in enumerate(zip(TIER_NAMES, TIER_COLORS, tier_thresholds)):
        tier_html += f"""
        <div style="text-align: center; flex: 1; min-width: 100px;">
            <div style="font-size: 1.5rem;">{'⭐' * min(i+1, 5)}{'💎' if i == 5 else ''}</div>
            <div style="font-family: 'Space Grotesk'; font-size: 0.85rem; font-weight: 700; color: {color};">{name}</div>
            <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #5c6184;">{thresh}</div>
        </div>
        """
    _html(tier_html + "</div></div>")

    # Display badges
    if st.session_state.data_mode == "chain" and st.session_state.web3_client:
        client = st.session_state.web3_client
        wallet = st.session_state.connected_wallet
        if wallet and client.is_connected:
            badges = client.get_badges_for_owner(wallet)
        else:
            badges = []
    else:
        badges = st.session_state.badges[:12]  # show first 12

    _html(f"""
    <div style="font-family: 'Space Grotesk'; font-size: 1.2rem; font-weight: 600; color: #e8eaf6; margin-bottom: 1rem;">
        Your Collection ({len(badges)} badges)
    </div>
    """)

    for row_start in range(0, len(badges), 4):
        cols = st.columns(4)
        for col_idx, col in enumerate(cols):
            badge_idx = row_start + col_idx
            if badge_idx < len(badges):
                badge = badges[badge_idx]
                tier_name = TIER_NAMES[badge.tier]
                tier_color = TIER_COLORS[badge.tier]
                tier_class = tier_name.lower()
                stars = "⭐" * min(badge.tier + 1, 5) + ("💎" if badge.tier == 5 else "")
                dt = datetime.fromtimestamp(badge.minted_at).strftime("%b %d, %Y")

                with col:
                    _html(f"""
                    <div class="badge-card" style="animation: fadeInUp 0.5s ease forwards;
                                                    animation-delay: {badge_idx * 0.1}s; opacity: 0;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{stars}</div>
                        <div class="badge-tier {tier_class}">{tier_name}</div>
                        <div style="font-family: 'Space Grotesk'; font-size: 1rem; font-weight: 600; color: #e8eaf6; margin: 0.3rem 0;">
                            {format_eth(badge.amount)} ETH
                        </div>
                        <div style="font-family: 'Outfit'; font-size: 0.75rem; color: #5c6184;
                                    display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden;">
                            {badge.campaign_title}
                        </div>
                        <div style="font-family: 'JetBrains Mono'; font-size: 0.6rem; color: #3a3f5c; margin-top: 0.3rem;">
                            #{badge.token_id} · {dt}
                        </div>
                    </div>
                    """)
                    _html("<br>")


# ═══════════════════════════════════════════════════════════════
#                        MAIN APP
# ═══════════════════════════════════════════════════════════════

def main():
    render_sidebar()

    page = st.session_state.current_page

    if page == "discover":
        page_discover()
    elif page == "campaign_detail":
        page_campaign_detail()
    elif page == "create":
        page_create()
    elif page == "dashboard":
        page_dashboard()
    elif page == "swap":
        page_swap()
    elif page == "badges":
        page_badges()
    else:
        page_discover()


if __name__ == "__main__":
    main()