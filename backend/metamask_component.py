"""
╔═══════════════════════════════════════════════════════════════╗
║   FundFlow — MetaMask Integration for Streamlit               ║
║   JavaScript injection for wallet operations                  ║
║                                                               ║
║   KEY FIX: Streamlit components.html() runs inside an iframe. ║
║   MetaMask injects window.ethereum into the TOP frame only.   ║
║   We use getProvider() to traverse frames and find it.        ║
╚═══════════════════════════════════════════════════════════════╝
"""

import json
import streamlit as st
import streamlit.components.v1 as components

# ═══════════════════════════════════════════════════════════════
#                  NETWORK CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════

NETWORKS = {
    "Arbitrum Sepolia": {
        "chainId": "0x66eee",
        "chainName": "Arbitrum Sepolia",
        "rpcUrls": ["https://sepolia-rollup.arbitrum.io/rpc"],
        "blockExplorerUrls": ["https://sepolia.arbiscan.io"],
        "nativeCurrency": {"name": "ETH", "symbol": "ETH", "decimals": 18},
    },
    "Base Sepolia": {
        "chainId": "0x14a34",
        "chainName": "Base Sepolia",
        "rpcUrls": ["https://sepolia.base.org"],
        "blockExplorerUrls": ["https://sepolia.basescan.org"],
        "nativeCurrency": {"name": "ETH", "symbol": "ETH", "decimals": 18},
    },
    "Arbitrum One": {
        "chainId": "0xa4b1",
        "chainName": "Arbitrum One",
        "rpcUrls": ["https://arb1.arbitrum.io/rpc"],
        "blockExplorerUrls": ["https://arbiscan.io"],
        "nativeCurrency": {"name": "ETH", "symbol": "ETH", "decimals": 18},
    },
    "Base": {
        "chainId": "0x2105",
        "chainName": "Base",
        "rpcUrls": ["https://mainnet.base.org"],
        "blockExplorerUrls": ["https://basescan.org"],
        "nativeCurrency": {"name": "ETH", "symbol": "ETH", "decimals": 18},
    },
    "Optimism": {
        "chainId": "0xa",
        "chainName": "OP Mainnet",
        "rpcUrls": ["https://mainnet.optimism.io"],
        "blockExplorerUrls": ["https://optimistic.etherscan.io"],
        "nativeCurrency": {"name": "ETH", "symbol": "ETH", "decimals": 18},
    },
}

# ═══════════════════════════════════════════════════════════════
#     PROVIDER DETECTION (iframe-safe)
#
#     MetaMask injects window.ethereum into the top-level page.
#     Streamlit components.html() creates an iframe, so we need
#     to traverse up the frame chain to find the provider.
# ═══════════════════════════════════════════════════════════════

_PROVIDER_JS = """
<script>
function getProvider() {
    // Try current window first
    if (typeof window.ethereum !== 'undefined') return window.ethereum;
    // Try parent frame (Streamlit app frame)
    try { if (window.parent && window.parent.ethereum) return window.parent.ethereum; } catch(e) {}
    // Try top-level frame (where MetaMask injects)
    try { if (window.top && window.top.ethereum) return window.top.ethereum; } catch(e) {}
    // Try all parent frames in chain
    try {
        let w = window;
        while (w !== w.parent) {
            w = w.parent;
            if (w.ethereum) return w.ethereum;
        }
    } catch(e) {}
    return null;
}
</script>
"""


# ═══════════════════════════════════════════════════════════════
#                  WALLET CONNECT
# ═══════════════════════════════════════════════════════════════

def render_wallet_connect(height: int = 160):
    """Render MetaMask connect/disconnect button."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Outfit', -apple-system, sans-serif;
                background: transparent; margin: 0; padding: 0.5rem;
            }}
            .connect-btn {{
                background: linear-gradient(135deg, #6c5ce7, #a29bfe);
                color: white; border: none; border-radius: 10px;
                padding: 0.65rem 1.25rem; font-family: 'Space Grotesk', sans-serif;
                font-weight: 600; font-size: 0.85rem; cursor: pointer;
                width: 100%; transition: all 0.3s;
            }}
            .connect-btn:hover {{
                box-shadow: 0 4px 20px rgba(108,92,231,0.4);
                transform: translateY(-1px);
            }}
            .disconnect-btn {{
                background: transparent; color: #ff5252;
                border: 1px solid #2a2f4c; border-radius: 10px;
                padding: 0.5rem 1rem; font-family: 'Space Grotesk', sans-serif;
                font-weight: 500; font-size: 0.75rem; cursor: pointer;
                width: 100%; margin-top: 0.5rem; display: none;
            }}
        </style>
    </head>
    <body>
        {_PROVIDER_JS}
        <script>
        async function connectWallet() {{
            const statusEl = document.getElementById('wallet-status');
            const provider = getProvider();

            if (!provider) {{
                statusEl.innerHTML = '<span style="color: #ff5252;">MetaMask not detected. Make sure the extension is installed and this page is not in incognito mode.</span>';
                return;
            }}

            try {{
                statusEl.innerHTML = '<span style="color: #ffab00;">Connecting...</span>';

                const accounts = await provider.request({{ method: 'eth_requestAccounts' }});
                const chainId = await provider.request({{ method: 'eth_chainId' }});
                const account = accounts[0];

                const balance = await provider.request({{
                    method: 'eth_getBalance', params: [account, 'latest']
                }});
                const balEth = (parseInt(balance, 16) / 1e18).toFixed(4);

                statusEl.innerHTML = `
                    <div style="background: rgba(0,230,118,0.06); border: 1px solid rgba(0,230,118,0.15);
                                border-radius: 10px; padding: 0.8rem; text-align: center;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #00e676;">
                            ${{account.slice(0,6)}}...${{account.slice(-4)}}
                        </div>
                        <div style="font-size: 0.7rem; color: #5c6184; margin-top: 0.3rem;">
                            Balance: ${{balEth}} ETH · Chain: ${{parseInt(chainId, 16)}}
                        </div>
                    </div>
                `;
                document.getElementById('connect-btn').style.display = 'none';
                document.getElementById('disconnect-btn').style.display = 'block';

                sessionStorage.setItem('ff_wallet', account);
                sessionStorage.setItem('ff_chain', chainId);
                sessionStorage.setItem('ff_balance', balEth);

                // Bridge to Streamlit Python: set query params on parent URL
                try {{
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('wallet', account);
                    url.searchParams.delete('disconnected');
                    window.parent.location.href = url.toString();
                }} catch(e) {{ console.log('Could not set parent query params:', e); }}

            }} catch (err) {{
                if (err.code === 4001) {{
                    statusEl.innerHTML = '<span style="color: #ffab00;">Connection rejected.</span>';
                }} else {{
                    statusEl.innerHTML = `<span style="color: #ff5252;">Error: ${{err.message}}</span>`;
                }}
            }}
        }}

        // Auto-detect existing connection
        (async () => {{
            const provider = getProvider();
            if (provider) {{
                try {{
                    const accounts = await provider.request({{ method: 'eth_accounts' }});
                    if (accounts.length > 0) {{
                        const account = accounts[0];
                        const chainId = await provider.request({{ method: 'eth_chainId' }});
                        const balance = await provider.request({{
                            method: 'eth_getBalance', params: [account, 'latest']
                        }});
                        const balEth = (parseInt(balance, 16) / 1e18).toFixed(4);

                        sessionStorage.setItem('ff_wallet', account);
                        sessionStorage.setItem('ff_chain', chainId);
                        sessionStorage.setItem('ff_balance', balEth);

                        // Sync to Streamlit (only redirect if param not already set)
                        try {{
                            const url = new URL(window.parent.location.href);
                            if (url.searchParams.get('wallet') !== account) {{
                                url.searchParams.set('wallet', account);
                                url.searchParams.delete('disconnected');
                                window.parent.location.href = url.toString();
                            }}
                        }} catch(e) {{}}

                        document.getElementById('wallet-status').innerHTML = `
                            <div style="background: rgba(0,230,118,0.06); border: 1px solid rgba(0,230,118,0.15);
                                        border-radius: 10px; padding: 0.8rem; text-align: center;">
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #00e676;">
                                    ${{account.slice(0,6)}}...${{account.slice(-4)}}
                                </div>
                                <div style="font-size: 0.7rem; color: #5c6184; margin-top: 0.3rem;">
                                    Balance: ${{balEth}} ETH · Chain: ${{parseInt(chainId, 16)}}
                                </div>
                            </div>
                        `;
                        document.getElementById('connect-btn').style.display = 'none';
                        document.getElementById('disconnect-btn').style.display = 'block';
                    }}

                    provider.on('accountsChanged', () => location.reload());
                    provider.on('chainChanged', () => location.reload());
                }} catch(e) {{}}
            }}
        }})();

        function disconnectWallet() {{
            sessionStorage.removeItem('ff_wallet');
            sessionStorage.removeItem('ff_chain');
            sessionStorage.removeItem('ff_balance');
            // Clear wallet from URL and trigger Streamlit rerun
            try {{
                const url = new URL(window.parent.location.href);
                url.searchParams.delete('wallet');
                url.searchParams.set('disconnected', '1');
                window.parent.location.href = url.toString();
            }} catch(e) {{
                document.getElementById('wallet-status').innerHTML = '<span style="color: #5c6184;">Disconnected</span>';
                document.getElementById('connect-btn').style.display = 'block';
                document.getElementById('disconnect-btn').style.display = 'none';
            }}
        }}
        </script>

        <div id="wallet-status" style="margin-bottom: 0.5rem; font-size: 0.8rem; color: #5c6184;"></div>
        <button id="connect-btn" class="connect-btn" onclick="connectWallet()">
            Connect MetaMask
        </button>
        <button id="disconnect-btn" class="disconnect-btn" onclick="disconnectWallet()">
            Disconnect
        </button>
    </body>
    </html>
    """
    components.html(html, height=height, scrolling=False)


# ═══════════════════════════════════════════════════════════════
#                  NETWORK SWITCH
# ═══════════════════════════════════════════════════════════════

def render_network_switch(network_name: str, height: int = 80):
    """Render a network switch button."""
    net = NETWORKS.get(network_name)
    if not net:
        return
    net_json = json.dumps(net)
    chain_id = int(net.get("chainId", "0x0"), 16)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Outfit', sans-serif; background: transparent; margin: 0; padding: 0.5rem; }}
            .switch-btn {{
                background: transparent; color: #9fa8da; border: 1px solid #1e2235;
                border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.75rem; cursor: pointer;
                width: 100%; font-family: 'JetBrains Mono', monospace;
            }}
            .switch-btn:hover {{ border-color: #6c5ce7; color: #a29bfe; }}
        </style>
    </head>
    <body>
        {_PROVIDER_JS}
        <script>
        async function switchNetwork() {{
            const provider = getProvider();
            if (!provider) return;
            const netConfig = {net_json};
            try {{
                await provider.request({{
                    method: 'wallet_switchEthereumChain',
                    params: [{{ chainId: netConfig.chainId }}]
                }});
                document.getElementById('network-status').innerHTML =
                    '<span style="color: #00e676;">Switched to {network_name}</span>';
            }} catch (switchError) {{
                if (switchError.code === 4902) {{
                    try {{
                        await provider.request({{
                            method: 'wallet_addEthereumChain',
                            params: [netConfig]
                        }});
                        document.getElementById('network-status').innerHTML =
                            '<span style="color: #00e676;">Added {network_name}</span>';
                    }} catch (addError) {{
                        document.getElementById('network-status').innerHTML =
                            `<span style="color: #ff5252;">${{addError.message}}</span>`;
                    }}
                }} else {{
                    document.getElementById('network-status').innerHTML =
                        `<span style="color: #ff5252;">${{switchError.message}}</span>`;
                }}
            }}
        }}
        </script>
        <button class="switch-btn" onclick="switchNetwork()">
            Switch to {network_name} (Chain {chain_id})
        </button>
        <div id="network-status" style="margin-top: 0.3rem; font-size: 0.7rem;"></div>
    </body>
    </html>
    """
    components.html(html, height=height, scrolling=False)


# ═══════════════════════════════════════════════════════════════
#                  SEND TRANSACTION
# ═══════════════════════════════════════════════════════════════

def render_send_transaction(tx_data: dict, label: str = "Confirm", tx_label: str = "Transaction", height: int = 180):
    """Render a transaction send button that triggers MetaMask signing."""
    tx_json = json.dumps(tx_data)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Outfit', sans-serif; background: transparent; margin: 0; padding: 0.5rem; }}
            .tx-btn {{
                background: linear-gradient(135deg, #6c5ce7, #a29bfe);
                color: white; border: none; border-radius: 10px;
                padding: 0.65rem 1.25rem; font-family: 'Space Grotesk', sans-serif;
                font-weight: 600; font-size: 0.85rem; cursor: pointer; width: 100%;
                transition: all 0.3s;
            }}
            .tx-btn:hover {{
                box-shadow: 0 4px 20px rgba(108,92,231,0.4);
                transform: translateY(-1px);
            }}
        </style>
    </head>
    <body>
        {_PROVIDER_JS}
        <script>
        async function sendTransaction() {{
            const statusEl = document.getElementById('tx-status');
            const provider = getProvider();
            const txData = {tx_json};

            if (!provider) {{
                statusEl.innerHTML = '<span style="color: #ff5252;">MetaMask not found</span>';
                return;
            }}

            try {{
                statusEl.innerHTML = '<span style="color: #ffab00;">Checking network...</span>';

                // FORCE SWITCH to correct chain before any transaction
                const requiredChain = txData.chainId || '0x66eee'; // default Arbitrum Sepolia
                const currentChain = await provider.request({{ method: 'eth_chainId' }});

                if (currentChain !== requiredChain) {{
                    statusEl.innerHTML = '<span style="color: #ffab00;">Switching to correct network...</span>';
                    try {{
                        await provider.request({{
                            method: 'wallet_switchEthereumChain',
                            params: [{{ chainId: requiredChain }}]
                        }});
                    }} catch (switchErr) {{
                        // Chain not added — add it
                        if (switchErr.code === 4902) {{
                            try {{
                                await provider.request({{
                                    method: 'wallet_addEthereumChain',
                                    params: [{{
                                        chainId: requiredChain,
                                        chainName: 'Arbitrum Sepolia',
                                        rpcUrls: ['https://sepolia-rollup.arbitrum.io/rpc'],
                                        blockExplorerUrls: ['https://sepolia.arbiscan.io'],
                                        nativeCurrency: {{ name: 'ETH', symbol: 'ETH', decimals: 18 }}
                                    }}]
                                }});
                            }} catch (addErr) {{
                                statusEl.innerHTML = `<span style="color: #ff5252;">Could not add network: ${{addErr.message}}</span>`;
                                return;
                            }}
                        }} else if (switchErr.code === 4001) {{
                            statusEl.innerHTML = '<span style="color: #ff5252;">You must switch to Arbitrum Sepolia to continue.</span>';
                            return;
                        }} else {{
                            statusEl.innerHTML = `<span style="color: #ff5252;">Network switch failed: ${{switchErr.message}}</span>`;
                            return;
                        }}
                    }}

                    // Verify switch happened
                    const newChain = await provider.request({{ method: 'eth_chainId' }});
                    if (newChain !== requiredChain) {{
                        statusEl.innerHTML = '<span style="color: #ff5252;">Network switch failed. Please manually switch to Arbitrum Sepolia in MetaMask.</span>';
                        return;
                    }}
                }}

                statusEl.innerHTML = '<span style="color: #ffab00;">Waiting for signature...</span>';

                // Connect wallet if not already
                const accounts = await provider.request({{ method: 'eth_requestAccounts' }});
                if (accounts.length === 0) {{
                    statusEl.innerHTML = '<span style="color: #ff5252;">Please connect wallet in MetaMask</span>';
                    return;
                }}

                const tx = {{
                    from: accounts[0],
                    to: txData.to,
                    data: txData.data,
                    value: txData.value || '0x0',
                }};

                const txHash = await provider.request({{
                    method: 'eth_sendTransaction',
                    params: [tx]
                }});

                statusEl.innerHTML = `
                    <div style="background: rgba(0,230,118,0.08); border: 1px solid rgba(0,230,118,0.2);
                                border-radius: 8px; padding: 0.6rem; margin-top: 0.3rem;">
                        <div style="font-size: 0.8rem; color: #00e676;">
                            {tx_label} sent!
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
                                    color: #9fa8da; word-break: break-all; margin-top: 0.2rem;">
                            ${{txHash}}
                        </div>
                    </div>
                `;
                sessionStorage.setItem('ff_last_tx', txHash);

            }} catch (err) {{
                if (err.code === 4001) {{
                    statusEl.innerHTML = '<span style="color: #ffab00;">Transaction rejected.</span>';
                }} else {{
                    statusEl.innerHTML = `<span style="color: #ff5252;">${{err.message}}</span>`;
                }}
            }}
        }}
        </script>
        <button class="tx-btn" onclick="sendTransaction()">{label}</button>
        <div id="tx-status" style="margin-top: 0.5rem; font-size: 0.8rem;"></div>
    </body>
    </html>
    """
    components.html(html, height=height, scrolling=False)


# ═══════════════════════════════════════════════════════════════
#              CONVENIENCE WRAPPERS
# ═══════════════════════════════════════════════════════════════

def render_contribute_button(tx_data: dict, amount_eth: float, height: int = 180):
    """Convenience wrapper for contribution transactions."""
    render_send_transaction(
        tx_data=tx_data,
        label=f"Contribute {amount_eth:.4f} ETH",
        tx_label="Contribution",
        height=height,
    )


def render_endorse_button(tx_data: dict, height: int = 120):
    """Convenience wrapper for endorsement transactions."""
    render_send_transaction(
        tx_data=tx_data,
        label="Submit Endorsement",
        tx_label="Endorsement",
        height=height,
    )


# ═══════════════════════════════════════════════════════════════
#              WALLET STATE READER
# ═══════════════════════════════════════════════════════════════

def read_wallet_state_js(height: int = 1) -> None:
    """Inject invisible JS that reads wallet state from sessionStorage."""
    html = """
    <script>
    (function() {
        const wallet = sessionStorage.getItem('ff_wallet');
        const chain = sessionStorage.getItem('ff_chain');
        const balance = sessionStorage.getItem('ff_balance');
        const el = document.createElement('div');
        el.id = 'ff-wallet-data';
        el.style.display = 'none';
        el.dataset.wallet = wallet || '';
        el.dataset.chain = chain || '';
        el.dataset.balance = balance || '0';
        document.body.appendChild(el);
    })();
    </script>
    """
    components.html(html, height=height, scrolling=False)


# ═══════════════════════════════════════════════════════════════
#              FAUCET LINK
# ═══════════════════════════════════════════════════════════════

def render_faucet_link(network: str, height: int = 50):
    """Show testnet faucet link."""
    faucets = {
        "Arbitrum Sepolia": "https://www.alchemy.com/faucets/arbitrum-sepolia",
        "Base Sepolia": "https://www.alchemy.com/faucets/base-sepolia",
        "Sepolia": "https://www.alchemy.com/faucets/ethereum-sepolia",
    }
    url = faucets.get(network, "")
    if url:
        html = f"""
        <div style="text-align: center; padding: 0.3rem;">
            <a href="{url}" target="_blank"
               style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
                      color: #6c5ce7; text-decoration: none;">
                Get free test ETH for {network}
            </a>
        </div>
        """
        components.html(html, height=height, scrolling=False)