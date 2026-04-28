


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Base64.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title ContributorBadge
 * @notice Soulbound-style NFT badges minted for each contribution
 *
 * GAS FIX: Tier metadata (names, colors, glows) moved from string[6]
 * storage arrays to pure functions. Saves ~360K deployment gas.
 * Storage arrays: 18 SSTORE ops × ~20K gas = ~360K gas.
 * Pure functions: compiled into bytecode, free to call at runtime.
 */
contract ContributorBadge is ERC721 {
    using Strings for uint256;

    struct Badge {
        address campaign;
        string campaignTitle;
        uint256 amount;
        uint8 tier;
        uint256 mintedAt;
    }

    uint256 private _nextTokenId;
    address public owner;
    mapping(uint256 => Badge) public badges;
    mapping(address => uint256[]) public badgesByOwner;
    mapping(address => bool) public authorizedMinters;

    event BadgeMinted(
        uint256 indexed tokenId,
        address indexed recipient,
        address indexed campaign,
        uint8 tier
    );

    constructor() ERC721("FundFlow Contributor Badge", "FFBADGE") {
        owner = msg.sender;
    }

    // ── Tier data: pure functions = zero storage cost ────────────

    function _tierName(uint8 _tier) internal pure returns (string memory) {
        if (_tier == 0) return "Supporter";
        if (_tier == 1) return "Bronze";
        if (_tier == 2) return "Silver";
        if (_tier == 3) return "Gold";
        if (_tier == 4) return "Platinum";
        if (_tier == 5) return "Diamond";
        revert("Invalid tier");
    }

    function _tierColor(uint8 _tier) internal pure returns (string memory) {
        if (_tier == 0) return "#8B9DAF";
        if (_tier == 1) return "#CD7F32";
        if (_tier == 2) return "#C0C0C0";
        if (_tier == 3) return "#FFD700";
        if (_tier == 4) return "#E5E4E2";
        if (_tier == 5) return "#B9F2FF";
        revert("Invalid tier");
    }

    function _tierGlow(uint8 _tier) internal pure returns (string memory) {
        if (_tier == 0) return "#4A5568";
        if (_tier == 1) return "#8B5E1A";
        if (_tier == 2) return "#808080";
        if (_tier == 3) return "#B8960F";
        if (_tier == 4) return "#9CA3AF";
        if (_tier == 5) return "#67E8F9";
        revert("Invalid tier");
    }

    // ── Ownership ────────────────────────────────────────────────

    /**
     * @notice Transfer ownership to the Factory contract after deployment.
     * @dev Call this AFTER deploying Factory: badge.transferOwnership(factoryAddr)
     */
    function transferOwnership(address _newOwner) external {
        require(msg.sender == owner, "Not owner");
        require(_newOwner != address(0), "Zero address");
        owner = _newOwner;
    }

    // ── Minting ──────────────────────────────────────────────────

    function grantMinter(address _minter) external {
        require(msg.sender == owner, "Not owner");
        authorizedMinters[_minter] = true;
    }

    function mintBadge(
        address _to,
        address _campaign,
        string calldata _campaignTitle,
        uint256 _amount,
        uint8 _tier
    ) external returns (uint256) {
        require(authorizedMinters[msg.sender], "Not authorized");
        require(_tier <= 5, "Invalid tier");

        uint256 tokenId = _nextTokenId++;

        badges[tokenId] = Badge({
            campaign: _campaign,
            campaignTitle: _campaignTitle,
            amount: _amount,
            tier: _tier,
            mintedAt: block.timestamp
        });

        badgesByOwner[_to].push(tokenId);
        _mint(_to, tokenId);

        emit BadgeMinted(tokenId, _to, _campaign, _tier);
        return tokenId;
    }

    // ── Token URI ────────────────────────────────────────────────

    function tokenURI(
        uint256 tokenId
    ) public view override returns (string memory) {
        require(tokenId < _nextTokenId, "Token does not exist");

        Badge memory badge = badges[tokenId];
        string memory svg = _generateSVG(badge);
        string memory tierName = _tierName(badge.tier);

        string memory json = string(
            abi.encodePacked(
                '{"name":"FundFlow ',
                tierName,
                ' Badge #',
                tokenId.toString(),
                '","description":"Contribution badge for ',
                badge.campaignTitle,
                '","image":"data:image/svg+xml;base64,',
                Base64.encode(bytes(svg)),
                '","attributes":[{"trait_type":"Tier","value":"',
                tierName,
                '"},{"trait_type":"Amount (Wei)","value":"',
                badge.amount.toString(),
                '"},{"trait_type":"Campaign","value":"',
                badge.campaignTitle,
                '"}]}'
            )
        );

        return
            string(
                abi.encodePacked(
                    "data:application/json;base64,",
                    Base64.encode(bytes(json))
                )
            );
    }

    // ── Views ────────────────────────────────────────────────────

    function getBadgesByOwner(
        address _owner
    ) external view returns (uint256[] memory) {
        return badgesByOwner[_owner];
    }

    function totalSupply() external view returns (uint256) {
        return _nextTokenId;
    }

    // ── SVG generation (all pure, no storage reads) ──────────────

    function _generateSVG(Badge memory badge) internal pure returns (string memory) {
        string memory color = _tierColor(badge.tier);
        string memory glow = _tierGlow(badge.tier);
        string memory tierName = _tierName(badge.tier);
        string memory amountStr = _formatEth(badge.amount);

        return string(abi.encodePacked(
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="500" viewBox="0 0 400 500">',
            '<defs><radialGradient id="bg" cx="50%" cy="30%"><stop offset="0%" stop-color="', glow,
            '" stop-opacity="0.3"/><stop offset="100%" stop-color="#0a0a0a"/></radialGradient>',
            '<filter id="glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
            '<rect width="400" height="500" rx="20" fill="url(#bg)" stroke="', color, '" stroke-width="2"/>',
            _generateBadgeArt(color, glow),
            '<text x="200" y="300" text-anchor="middle" fill="', color,
            '" font-family="monospace" font-size="28" font-weight="bold" filter="url(#glow)">', tierName, '</text>',
            '<text x="200" y="340" text-anchor="middle" fill="#888" font-family="monospace" font-size="14">', amountStr, ' ETH</text>',
            '<text x="200" y="380" text-anchor="middle" fill="#666" font-family="monospace" font-size="11">', _truncateTitle(badge.campaignTitle), '</text>',
            '<text x="200" y="470" text-anchor="middle" fill="#444" font-family="monospace" font-size="10">FUNDFLOW CONTRIBUTOR</text></svg>'
        ));
    }

    function _generateBadgeArt(string memory color, string memory glow) internal pure returns (string memory) {
        return string(abi.encodePacked(
            '<circle cx="200" cy="160" r="80" fill="none" stroke="', color, '" stroke-width="3" filter="url(#glow)"/>',
            '<circle cx="200" cy="160" r="60" fill="none" stroke="', glow, '" stroke-width="1" opacity="0.5"/>',
            '<polygon points="200,95 215,140 260,140 225,170 235,215 200,190 165,215 175,170 140,140 185,140" fill="', color, '" opacity="0.8" filter="url(#glow)"/>'
        ));
    }

    function _formatEth(uint256 _wei) internal pure returns (string memory) {
        uint256 ethWhole = _wei / 1 ether;
        uint256 ethFrac = (_wei % 1 ether) / 1e14;
        if (ethFrac == 0) return ethWhole.toString();

        string memory fracStr = ethFrac.toString();
        bytes memory padded = new bytes(4);
        bytes memory fracBytes = bytes(fracStr);
        uint256 padding = 4 - fracBytes.length;
        for (uint256 i = 0; i < 4; i++) {
            padded[i] = i < padding ? bytes1("0") : fracBytes[i - padding];
        }
        return string(abi.encodePacked(ethWhole.toString(), ".", string(padded)));
    }

    function _truncateTitle(string memory _title) internal pure returns (string memory) {
        bytes memory titleBytes = bytes(_title);
        if (titleBytes.length <= 30) return _title;
        bytes memory truncated = new bytes(27);
        for (uint256 i = 0; i < 27; i++) {
            truncated[i] = titleBytes[i];
        }
        return string(abi.encodePacked(string(truncated), "..."));
    }
}
