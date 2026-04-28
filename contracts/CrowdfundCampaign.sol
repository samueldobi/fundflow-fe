// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./ContributorBadge.sol";

/**
 * @title CrowdfundCampaign
 * @notice Individual crowdfunding campaign with milestone-based fund release,
 *         refund capability, contribution tiers, and NFT badge minting
 */
contract CrowdfundCampaign {
    // ═══════════════════════════════════════════════════════════════
    //                          ENUMS
    // ═══════════════════════════════════════════════════════════════

    enum CampaignStatus {
        Active,
        Successful,
        Failed,
        Cancelled
    }

    enum ContributionTier {
        Supporter,    // < 0.01 ETH
        Bronze,       // 0.01 - 0.1 ETH
        Silver,       // 0.1 - 0.5 ETH
        Gold,         // 0.5 - 1 ETH
        Platinum,     // 1 - 5 ETH
        Diamond       // > 5 ETH
    }

    // ═══════════════════════════════════════════════════════════════
    //                         STRUCTS
    // ═══════════════════════════════════════════════════════════════

    struct Milestone {
        string description;
        uint256 percentage; // percentage of funds released
        bool completed;
        bool fundsReleased;
    }

    struct Contribution {
        address contributor;
        uint256 amount;
        uint256 timestamp;
        string message;
        bool refunded;
    }

    // ═══════════════════════════════════════════════════════════════
    //                          STORAGE
    // ═══════════════════════════════════════════════════════════════

    // Campaign info
    address public creator;
    string public title;
    string public description;
    string public imageURI;
    string public category;
    uint256 public goalAmount;
    uint256 public deadline;
    uint256 public totalRaised;
    uint256 public totalWithdrawn;
    uint256 public createdAt;
    CampaignStatus public status;

    // Platform fee
    address public platformFeeRecipient;
    uint256 public platformFeeBps;
    bool public platformFeePaid;

    // Milestones
    Milestone[] public milestones;
    uint256 public currentMilestone;

    // Contributions
    Contribution[] public contributions;
    mapping(address => uint256) public contributorTotals;
    mapping(address => bool) public hasContributed;
    address[] public contributors;
    uint256 public contributorCount;

    // Badge NFT
    ContributorBadge public badgeNFT;

    // Social: endorsements
    mapping(address => string) public endorsements;
    address[] public endorsers;

    // Updates from creator
    string[] public updates;
    uint256[] public updateTimestamps;

    // ═══════════════════════════════════════════════════════════════
    //                          EVENTS
    // ═══════════════════════════════════════════════════════════════

    event ContributionMade(
        address indexed contributor,
        uint256 amount,
        string message,
        ContributionTier tier
    );
    event MilestoneCompleted(uint256 indexed milestoneIndex, string description);
    event FundsWithdrawn(uint256 amount, uint256 milestoneIndex);
    event RefundIssued(address indexed contributor, uint256 amount);
    event CampaignCancelled();
    event CampaignSuccessful();
    event CampaignFailed();
    event UpdatePosted(string content, uint256 timestamp);
    event EndorsementAdded(address indexed endorser, string message);

    // ═══════════════════════════════════════════════════════════════
    //                        MODIFIERS
    // ═══════════════════════════════════════════════════════════════

    modifier onlyCreator() {
        require(msg.sender == creator, "Not creator");
        _;
    }

    modifier campaignActive() {
        require(status == CampaignStatus.Active, "Campaign not active");
        require(block.timestamp <= deadline, "Campaign expired");
        _;
    }

    // ═══════════════════════════════════════════════════════════════
    //                       CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════

    constructor(
        address _creator,
        string memory _title,
        string memory _description,
        uint256 _goalAmount,
        uint256 _deadline,
        string memory _category,
        string[] memory _milestoneDescriptions,
        uint256[] memory _milestonePercentages,
        string memory _imageURI,
        address _badgeNFT,
        address _platformFeeRecipient,
        uint256 _platformFeeBps
    ) {
        creator = _creator;
        title = _title;
        description = _description;
        goalAmount = _goalAmount;
        deadline = _deadline;
        category = _category;
        imageURI = _imageURI;
        createdAt = block.timestamp;
        status = CampaignStatus.Active;

        badgeNFT = ContributorBadge(_badgeNFT);
        platformFeeRecipient = _platformFeeRecipient;
        platformFeeBps = _platformFeeBps;

        for (uint256 i = 0; i < _milestoneDescriptions.length; i++) {
            milestones.push(
                Milestone({
                    description: _milestoneDescriptions[i],
                    percentage: _milestonePercentages[i],
                    completed: false,
                    fundsReleased: false
                })
            );
        }
    }

    // ═══════════════════════════════════════════════════════════════
    //                      CONTRIBUTE
    // ═══════════════════════════════════════════════════════════════

    /**
     * @notice Contribute ETH to this campaign
     * @param _message Optional message with contribution
     */
    function contribute(string calldata _message) external payable campaignActive {
        require(msg.value > 0, "Must send ETH");

        // Track contribution
        contributions.push(
            Contribution({
                contributor: msg.sender,
                amount: msg.value,
                timestamp: block.timestamp,
                message: _message,
                refunded: false
            })
        );

        if (!hasContributed[msg.sender]) {
            hasContributed[msg.sender] = true;
            contributors.push(msg.sender);
            contributorCount++;
        }

        contributorTotals[msg.sender] += msg.value;
        totalRaised += msg.value;

        // Determine tier and mint badge NFT
        ContributionTier tier = _getTier(msg.value);
        badgeNFT.mintBadge(
            msg.sender,
            address(this),
            title,
            msg.value,
            uint8(tier)
        );

        emit ContributionMade(msg.sender, msg.value, _message, tier);

        // Check if goal reached
        if (totalRaised >= goalAmount && status == CampaignStatus.Active) {
            status = CampaignStatus.Successful;
            emit CampaignSuccessful();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    //                  MILESTONE & WITHDRAWAL
    // ═══════════════════════════════════════════════════════════════

    /**
     * @notice Mark current milestone as complete (creator only)
     */
    function completeMilestone() external onlyCreator {
        require(
            status == CampaignStatus.Successful || totalRaised > 0,
            "No funds raised"
        );
        require(currentMilestone < milestones.length, "All milestones done");
        require(!milestones[currentMilestone].completed, "Already completed");

        milestones[currentMilestone].completed = true;
        emit MilestoneCompleted(
            currentMilestone,
            milestones[currentMilestone].description
        );
    }

    /**
     * @notice Withdraw funds for completed milestone (creator only)
     */
    function withdrawMilestone() external onlyCreator {
        require(currentMilestone < milestones.length, "All withdrawn");
        require(milestones[currentMilestone].completed, "Milestone not complete");
        require(!milestones[currentMilestone].fundsReleased, "Already released");

        uint256 milestoneAmount = (totalRaised *
            milestones[currentMilestone].percentage) / 100;

        // Deduct platform fee on first withdrawal
        if (!platformFeePaid) {
            uint256 fee = (totalRaised * platformFeeBps) / 10000;
            platformFeePaid = true;
            milestoneAmount -= fee;
            (bool feeSent, ) = platformFeeRecipient.call{value: fee}("");
            require(feeSent, "Fee transfer failed");
        }

        milestones[currentMilestone].fundsReleased = true;
        totalWithdrawn += milestoneAmount;
        currentMilestone++;

        (bool sent, ) = creator.call{value: milestoneAmount}("");
        require(sent, "Transfer failed");

        emit FundsWithdrawn(milestoneAmount, currentMilestone - 1);
    }

    // ═══════════════════════════════════════════════════════════════
    //                        REFUNDS
    // ═══════════════════════════════════════════════════════════════

    /**
     * @notice Claim refund if campaign failed or was cancelled
     */
    function claimRefund() external {
        require(
            status == CampaignStatus.Failed ||
                status == CampaignStatus.Cancelled,
            "Not refundable"
        );
        require(contributorTotals[msg.sender] > 0, "No contribution");

        uint256 refundAmount = contributorTotals[msg.sender];
        contributorTotals[msg.sender] = 0;

        // Mark individual contributions as refunded
        for (uint256 i = 0; i < contributions.length; i++) {
            if (
                contributions[i].contributor == msg.sender &&
                !contributions[i].refunded
            ) {
                contributions[i].refunded = true;
            }
        }

        (bool sent, ) = msg.sender.call{value: refundAmount}("");
        require(sent, "Refund failed");

        emit RefundIssued(msg.sender, refundAmount);
    }

    /**
     * @notice Finalize campaign as failed if deadline passed and goal not met
     */
    function finalizeFailed() external {
        require(block.timestamp > deadline, "Not expired");
        require(status == CampaignStatus.Active, "Not active");
        require(totalRaised < goalAmount, "Goal was met");

        status = CampaignStatus.Failed;
        emit CampaignFailed();
    }

    /**
     * @notice Cancel campaign (creator only, before any withdrawals)
     */
    function cancelCampaign() external onlyCreator {
        require(totalWithdrawn == 0, "Funds already withdrawn");
        require(
            status == CampaignStatus.Active ||
                status == CampaignStatus.Successful,
            "Cannot cancel"
        );

        status = CampaignStatus.Cancelled;
        emit CampaignCancelled();
    }

    // ═══════════════════════════════════════════════════════════════
    //                    SOCIAL FEATURES
    // ═══════════════════════════════════════════════════════════════

    /**
     * @notice Add an endorsement to the campaign
     */
    function endorse(string calldata _message) external {
        require(bytes(_message).length > 0, "Empty message");
        require(bytes(endorsements[msg.sender]).length == 0, "Already endorsed");

        endorsements[msg.sender] = _message;
        endorsers.push(msg.sender);

        emit EndorsementAdded(msg.sender, _message);
    }

    /**
     * @notice Post an update (creator only)
     */
    function postUpdate(string calldata _content) external onlyCreator {
        require(bytes(_content).length > 0, "Empty update");
        updates.push(_content);
        updateTimestamps.push(block.timestamp);
        emit UpdatePosted(_content, block.timestamp);
    }

    // ═══════════════════════════════════════════════════════════════
    //                     VIEW FUNCTIONS
    // ═══════════════════════════════════════════════════════════════

    function getCampaignInfo()
        external
        view
        returns (
            address _creator,
            string memory _title,
            string memory _description,
            string memory _imageURI,
            string memory _category,
            uint256 _goalAmount,
            uint256 _totalRaised,
            uint256 _deadline,
            uint256 _contributorCount,
            CampaignStatus _status,
            uint256 _createdAt
        )
    {
        return (
            creator,
            title,
            description,
            imageURI,
            category,
            goalAmount,
            totalRaised,
            deadline,
            contributorCount,
            status,
            createdAt
        );
    }

    function getMilestones() external view returns (Milestone[] memory) {
        return milestones;
    }

    function getContributions() external view returns (Contribution[] memory) {
        return contributions;
    }

    function getContributors() external view returns (address[] memory) {
        return contributors;
    }

    function getEndorsers() external view returns (address[] memory) {
        return endorsers;
    }

    function getUpdates()
        external
        view
        returns (string[] memory, uint256[] memory)
    {
        return (updates, updateTimestamps);
    }

    function getTimeRemaining() external view returns (uint256) {
        if (block.timestamp >= deadline) return 0;
        return deadline - block.timestamp;
    }

    function getProgress() external view returns (uint256) {
        if (goalAmount == 0) return 0;
        return (totalRaised * 100) / goalAmount;
    }

    // ═══════════════════════════════════════════════════════════════
    //                   INTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════

    function _getTier(
        uint256 _amount
    ) internal pure returns (ContributionTier) {
        if (_amount >= 5 ether) return ContributionTier.Diamond;
        if (_amount >= 1 ether) return ContributionTier.Platinum;
        if (_amount >= 0.5 ether) return ContributionTier.Gold;
        if (_amount >= 0.1 ether) return ContributionTier.Silver;
        if (_amount >= 0.01 ether) return ContributionTier.Bronze;
        return ContributionTier.Supporter;
    }

    receive() external payable {
        revert("Use contribute()");
    }
}
