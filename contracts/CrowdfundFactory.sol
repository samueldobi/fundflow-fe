// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./CrowdfundCampaign.sol";
import "./ContributorBadge.sol";

/**
 * @title CrowdfundFactory
 * @notice Factory for creating and managing crowdfunding campaigns
 *
 * GAS FIXES (vs original):
 *
 * 1. BadgeNFT is deployed SEPARATELY and passed via constructor.
 *    Before: Constructor deployed the entire ContributorBadge contract
 *    inline, adding ~2-3M gas to Factory deployment.
 *    Now: Deploy BadgeNFT first (separate tx), pass address to Factory.
 *
 * 2. Categories are NOT added in constructor anymore.
 *    Before: 9× _addCategory() in constructor = 18 SSTORE ops = ~360K gas.
 *    Now: Call initCategories() once after deployment (separate tx).
 *    This splits the cost across 2 cheaper transactions instead of
 *    1 massive one that can hit gas limits.
 *
 * 3. Added batchAddCategories() for gas-efficient bulk category setup.
 *
 * DEPLOYMENT ORDER:
 *   Step 1: Deploy ContributorBadge                    (~1.5M gas)
 *   Step 2: Deploy CrowdfundFactory(feeRecipient, badgeAddr)  (~1.5M gas)
 *   Step 3: Call badgeNFT.transferOwnership(factoryAddr) on Badge
 *   Step 4: Call factory.initCategories()               (~400K gas)
 *   Total: ~3.4M gas across 4 txs vs ~6M+ in 1 tx that fails
 */
contract CrowdfundFactory {

    ContributorBadge public immutable badgeNFT;

    address[] public allCampaigns;
    mapping(address => address[]) public campaignsByCreator;
    mapping(string => address[]) public campaignsByCategory;

    uint256 public constant PLATFORM_FEE_BPS = 150; // 1.5%
    address public platformFeeRecipient;
    address public owner;

    string[] public categories;
    mapping(string => bool) public validCategory;
    bool public categoriesInitialized;

    // ── Events ───────────────────────────────────────────────────

    event CampaignCreated(
        address indexed campaignAddress,
        address indexed creator,
        string title,
        uint256 goalAmount,
        uint256 deadline,
        string category
    );
    event CategoryAdded(string category);
    event PlatformFeeRecipientUpdated(address newRecipient);

    // ── Modifiers ────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // ── Constructor (lightweight — no Badge deploy, no categories) ─

    constructor(address _feeRecipient, address _badgeNFT) {
        require(_feeRecipient != address(0), "Zero fee recipient");
        require(_badgeNFT != address(0), "Zero badge address");
        owner = msg.sender;
        platformFeeRecipient = _feeRecipient;
        badgeNFT = ContributorBadge(_badgeNFT);
    }

    // ── Post-deploy initialization (separate tx) ─────────────────

    /**
     * @notice Initialize default categories. Call once after deployment.
     * @dev Separated from constructor to reduce deployment gas.
     */
    function initCategories() external onlyOwner {
        require(!categoriesInitialized, "Already initialized");
        categoriesInitialized = true;

        _addCategory("Medical");
        _addCategory("Education");
        _addCategory("Emergency");
        _addCategory("Community");
        _addCategory("Creative");
        _addCategory("Technology");
        _addCategory("Environment");
        _addCategory("Sports");
        _addCategory("Other");
    }

    // ── Campaign creation ────────────────────────────────────────

    function createCampaign(
        string calldata _title,
        string calldata _description,
        uint256 _goalAmount,
        uint256 _durationDays,
        string calldata _category,
        string[] calldata _milestones,
        uint256[] calldata _milestonePercentages,
        string calldata _imageURI
    ) external returns (address) {
        require(_goalAmount > 0, "Goal must be > 0");
        require(_durationDays > 0 && _durationDays <= 365, "Invalid duration");
        require(validCategory[_category], "Invalid category");
        require(
            _milestones.length == _milestonePercentages.length,
            "Milestone mismatch"
        );

        uint256 totalPct;
        for (uint256 i = 0; i < _milestonePercentages.length; i++) {
            totalPct += _milestonePercentages[i];
        }
        require(totalPct == 100, "Milestones must sum to 100%");

        uint256 deadline = block.timestamp + (_durationDays * 1 days);

        CrowdfundCampaign campaign = new CrowdfundCampaign(
            msg.sender,
            _title,
            _description,
            _goalAmount,
            deadline,
            _category,
            _milestones,
            _milestonePercentages,
            _imageURI,
            address(badgeNFT),
            platformFeeRecipient,
            PLATFORM_FEE_BPS
        );

        address campaignAddr = address(campaign);
        allCampaigns.push(campaignAddr);
        campaignsByCreator[msg.sender].push(campaignAddr);
        campaignsByCategory[_category].push(campaignAddr);

        badgeNFT.grantMinter(campaignAddr);

        emit CampaignCreated(
            campaignAddr,
            msg.sender,
            _title,
            _goalAmount,
            deadline,
            _category
        );

        return campaignAddr;
    }

    // ── View functions ───────────────────────────────────────────

    function getCampaignCount() external view returns (uint256) {
        return allCampaigns.length;
    }

    function getCampaignsByCreator(
        address _creator
    ) external view returns (address[] memory) {
        return campaignsByCreator[_creator];
    }

    function getCampaignsByCategory(
        string calldata _category
    ) external view returns (address[] memory) {
        return campaignsByCategory[_category];
    }

    function getAllCampaigns() external view returns (address[] memory) {
        return allCampaigns;
    }

    function getCategories() external view returns (string[] memory) {
        return categories;
    }

    // ── Admin functions ──────────────────────────────────────────

    function addCategory(string calldata _category) external onlyOwner {
        _addCategory(_category);
    }

    /**
     * @notice Batch add multiple categories in one tx
     */
    function batchAddCategories(string[] calldata _cats) external onlyOwner {
        for (uint256 i = 0; i < _cats.length; i++) {
            _addCategory(_cats[i]);
        }
    }

    function updateFeeRecipient(address _newRecipient) external onlyOwner {
        require(_newRecipient != address(0), "Zero address");
        platformFeeRecipient = _newRecipient;
        emit PlatformFeeRecipientUpdated(_newRecipient);
    }

    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Zero address");
        owner = _newOwner;
    }

    // ── Internal ─────────────────────────────────────────────────

    function _addCategory(string memory _category) internal {
        require(!validCategory[_category], "Category exists");
        categories.push(_category);
        validCategory[_category] = true;
        emit CategoryAdded(_category);
    }
}
