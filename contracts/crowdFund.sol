// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CrowdFundingPlatform is ReentrancyGuard, Pausable, Ownable {
    
    // Platform fee: 5% = 500 basis points
    uint256 public constant PLATFORM_FEE_BPS = 500;
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public constant MAX_CONTRIBUTORS_PER_CAMPAIGN = 500;
    uint256 public constant ADMIN_TIME_LOCK = 24 hours;
    
    // Configurable parameters
    uint256 public minContribution = 0.001 ether;
    uint256 public campaignCreationFee = 0.01 ether;
    
    // Time lock state
    uint256 public pauseProposedAt;
    bool public pauseProposed;
    
    // Safe wallet address for receiving platform fees
    address public immutable platformSafeWallet;
    
    // Campaign counter
    uint256 public campaignCounter;
    
    // Platform statistics
    uint256 public activeCampaignsCount;
    uint256 public fundedCampaignsCount;
    uint256 public totalValueLocked;
    
    // Campaign statuses
    enum CampaignStatus {
        Active,
        Funded,
        Finalized,
        Expired,
        Cancelled
    }
    
    // Optimized struct with packed storage
    struct Campaign {
        address creator;              // 20 bytes
        address beneficiary;          // 20 bytes
        uint96 targetAmount;          // 12 bytes (max ~79 billion ETH)
        uint96 totalContributed;      // 12 bytes
        uint32 deadline;              // 4 bytes (valid until year 2106)
        uint32 createdAt;             // 4 bytes
        uint32 contributorCount;      // 4 bytes
        CampaignStatus status;        // 1 byte
        bool fundsWithdrawn;          // 1 byte
    }
    
    // Mappings
    mapping(uint256 => Campaign) public campaigns;
    mapping(uint256 => mapping(address => uint256)) public contributions;
    mapping(uint256 => mapping(address => bool)) public hasContributed;
    
    // Events
    event CampaignCreated(
        uint256 indexed campaignId,
        address indexed creator,
        address indexed beneficiary,
        uint256 targetAmount,
        uint256 totalRequired,
        uint256 deadline
    );
    
    event ContributionReceived(
        uint256 indexed campaignId,
        address indexed contributor,
        uint256 amount,
        uint256 totalContributed
    );
    
    event CampaignFunded(uint256 indexed campaignId, uint256 totalAmount);
    
    event FundsDistributed(
        uint256 indexed campaignId,
        address indexed beneficiary,
        uint256 beneficiaryAmount,
        uint256 platformFee,
        address platformSafe
    );
    
    event RefundIssued(
        uint256 indexed campaignId,
        address indexed contributor,
        uint256 amount
    );
    
    event CampaignCancelled(uint256 indexed campaignId, string reason);
    
    event CampaignStatusChanged(
        uint256 indexed campaignId,
        CampaignStatus oldStatus,
        CampaignStatus newStatus
    );
    
    event MinContributionUpdated(uint256 oldAmount, uint256 newAmount);
    event CampaignCreationFeeUpdated(uint256 oldFee, uint256 newFee);
    event PauseProposed(uint256 proposedAt, uint256 effectiveAt);
    event PauseCancelled();
    event EmergencyPauseExecuted(address indexed executor);
    
    // Modifiers
    modifier campaignExists(uint256 _campaignId) {
        require(_campaignId < campaignCounter, "Campaign does not exist");
        _;
    }
    
    modifier onlyCampaignCreator(uint256 _campaignId) {
        require(
            campaigns[_campaignId].creator == msg.sender,
            "Not campaign creator"
        );
        _;
    }
    
    constructor(address _platformSafeWallet, address initialOwner) 
        Ownable(initialOwner) 
    {
        require(_platformSafeWallet != address(0), "Invalid Safe wallet");
        require(initialOwner != address(0), "Invalid owner");
        platformSafeWallet = _platformSafeWallet;
    }
    
    /**
     * @notice Create a new crowdfunding campaign
     */
    function createCampaign(
        uint256 _targetAmount,
        address _beneficiary,
        uint256 _durationDays
    ) external payable whenNotPaused returns (uint256) {
        require(_targetAmount > 0, "Target must be > 0");
        require(_targetAmount < type(uint96).max, "Target too high");
        require(_beneficiary != address(0), "Invalid beneficiary");
        require(_durationDays > 0 && _durationDays <= 365, "Invalid duration");
        require(msg.value >= campaignCreationFee, "Insufficient fee");
        
        uint256 campaignId;
        unchecked {
            campaignId = campaignCounter++;
        }
        
        uint32 deadline = uint32(block.timestamp + (_durationDays * 1 days));
        
        campaigns[campaignId] = Campaign({
            creator: msg.sender,
            beneficiary: _beneficiary,
            targetAmount: uint96(_targetAmount),
            totalContributed: 0,
            deadline: deadline,
            status: CampaignStatus.Active,
            fundsWithdrawn: false,
            createdAt: uint32(block.timestamp),
            contributorCount: 0
        });
        
        unchecked {
            activeCampaignsCount++;
        }
        
        // Send creation fee to platform Safe
        if (campaignCreationFee > 0) {
            (bool success, ) = platformSafeWallet.call{value: campaignCreationFee}("");
            require(success, "Fee transfer failed");
        }
        
        emit CampaignCreated(
            campaignId,
            msg.sender,
            _beneficiary,
            _targetAmount,
            calculateTotalRequired(_targetAmount),
            deadline
        );
        
        return campaignId;
    }
    
    /**
     * @notice Contribute to a campaign
     */
    function contribute(uint256 _campaignId)
        external
        payable
        campaignExists(_campaignId)
        nonReentrant
        whenNotPaused
    {
        require(msg.value >= minContribution, "Below minimum");
        
        Campaign storage campaign = campaigns[_campaignId];
        
        require(campaign.status == CampaignStatus.Active, "Not active");
        require(block.timestamp < campaign.deadline, "Expired");
        
        // Track new contributor
        if (!hasContributed[_campaignId][msg.sender]) {
            require(
                campaign.contributorCount < MAX_CONTRIBUTORS_PER_CAMPAIGN,
                "Max contributors reached"
            );
            hasContributed[_campaignId][msg.sender] = true;
            unchecked {
                campaign.contributorCount++;
            }
        }
        
        contributions[_campaignId][msg.sender] += msg.value;
        
        uint256 newTotal;
        unchecked {
            newTotal = uint256(campaign.totalContributed) + msg.value;
        }
        require(newTotal < type(uint96).max, "Contribution overflow");
        
        campaign.totalContributed = uint96(newTotal);
        
        unchecked {
            totalValueLocked += msg.value;
        }
        
        emit ContributionReceived(
            _campaignId,
            msg.sender,
            msg.value,
            newTotal
        );
        
        // Check if funded
        uint256 totalRequired = calculateTotalRequired(campaign.targetAmount);
        if (newTotal >= totalRequired) {
            _updateCampaignStatus(campaign, CampaignStatus.Funded);
            emit CampaignFunded(_campaignId, newTotal);
        }
    }
    
    /**
     * @notice Calculate total amount required (target + platform fee)
     */
    function calculateTotalRequired(uint256 _targetAmount)
        public
        pure
        returns (uint256)
    {
        unchecked {
            return _targetAmount + ((_targetAmount * PLATFORM_FEE_BPS) / BASIS_POINTS);
        }
    }
    
    /**
     * @notice Calculate platform fee from target amount
     */
    function calculatePlatformFee(uint256 _targetAmount)
        public
        pure
        returns (uint256)
    {
        unchecked {
            return (_targetAmount * PLATFORM_FEE_BPS) / BASIS_POINTS;
        }
    }
    
    /**
     * @notice Finalize campaign and distribute funds
     */
    function finalizeCampaign(uint256 _campaignId)
        external
        campaignExists(_campaignId)
        nonReentrant
        whenNotPaused
    {
        Campaign storage campaign = campaigns[_campaignId];
        
        require(campaign.status == CampaignStatus.Funded, "Not funded");
        require(!campaign.fundsWithdrawn, "Already withdrawn");
        require(
            msg.sender == campaign.creator || msg.sender == campaign.beneficiary,
            "Not authorized"
        );
        
        campaign.fundsWithdrawn = true;
        _updateCampaignStatus(campaign, CampaignStatus.Finalized);
        
        uint256 platformFee = calculatePlatformFee(campaign.targetAmount);
        uint256 beneficiaryAmount = campaign.targetAmount;
        uint256 totalToDistribute = uint256(campaign.totalContributed);
        
        unchecked {
            totalValueLocked -= totalToDistribute;
        }
        
        // Transfer to beneficiary
        (bool successBeneficiary, ) = campaign.beneficiary.call{value: beneficiaryAmount}("");
        require(successBeneficiary, "Beneficiary transfer failed");
        
        // Transfer to platform
        (bool successPlatform, ) = platformSafeWallet.call{value: platformFee}("");
        require(successPlatform, "Platform transfer failed");
        
        emit FundsDistributed(
            _campaignId,
            campaign.beneficiary,
            beneficiaryAmount,
            platformFee,
            platformSafeWallet
        );
    }
    
    /**
     * @notice Request refund if campaign expired or cancelled
     */
    function refund(uint256 _campaignId)
        external
        campaignExists(_campaignId)
        nonReentrant
        whenNotPaused
    {
        Campaign storage campaign = campaigns[_campaignId];
        
        require(block.timestamp >= campaign.deadline, "Still active");
        require(
            campaign.status == CampaignStatus.Active || 
            campaign.status == CampaignStatus.Cancelled ||
            campaign.status == CampaignStatus.Expired,
            "Not refundable"
        );
        
        // Update status to Expired on first refund
        if (campaign.status == CampaignStatus.Active) {
            _updateCampaignStatus(campaign, CampaignStatus.Expired);
        }
        
        uint256 contributedAmount = contributions[_campaignId][msg.sender];
        require(contributedAmount > 0, "No contribution");
        
        contributions[_campaignId][msg.sender] = 0;
        
        unchecked {
            totalValueLocked -= contributedAmount;
        }
        
        (bool success, ) = msg.sender.call{value: contributedAmount}("");
        require(success, "Refund failed");
        
        emit RefundIssued(_campaignId, msg.sender, contributedAmount);
    }
    
    /**
     * @notice Cancel campaign (only creator)
     */
    function cancelCampaign(uint256 _campaignId, string calldata _reason)
        external
        campaignExists(_campaignId)
        onlyCampaignCreator(_campaignId)
    {
        Campaign storage campaign = campaigns[_campaignId];
        require(campaign.status == CampaignStatus.Active, "Not active");
        require(!campaign.fundsWithdrawn, "Funds withdrawn");
        
        _updateCampaignStatus(campaign, CampaignStatus.Cancelled);
        
        emit CampaignCancelled(_campaignId, _reason);
    }
    
    /**
     * @notice Internal function to update campaign status
     */
    function _updateCampaignStatus(Campaign storage campaign, CampaignStatus _newStatus) 
        internal 
    {
        CampaignStatus oldStatus = campaign.status;
        
        if (oldStatus == _newStatus) return;
        
        // Update counters
        if (oldStatus == CampaignStatus.Active && activeCampaignsCount > 0) {
            unchecked {
                activeCampaignsCount--;
            }
        } else if (oldStatus == CampaignStatus.Funded && fundedCampaignsCount > 0) {
            unchecked {
                fundedCampaignsCount--;
            }
        }
        
        if (_newStatus == CampaignStatus.Active) {
            unchecked {
                activeCampaignsCount++;
            }
        } else if (_newStatus == CampaignStatus.Funded) {
            unchecked {
                fundedCampaignsCount++;
            }
        }
        
        campaign.status = _newStatus;
        
        emit CampaignStatusChanged(uint256(uint160(address(this))), oldStatus, _newStatus);
    }
    
    // ==================== VIEW FUNCTIONS ====================
    
    /**
     * @notice Get campaign details
     */
    function getCampaign(uint256 _campaignId)
        external
        view
        campaignExists(_campaignId)
        returns (
            address creator,
            address beneficiary,
            uint256 targetAmount,
            uint256 totalContributed,
            uint256 deadline,
            CampaignStatus status,
            bool fundsWithdrawn,
            uint256 createdAt,
            uint256 contributorCount
        )
    {
        Campaign memory c = campaigns[_campaignId];
        return (
            c.creator,
            c.beneficiary,
            c.targetAmount,
            c.totalContributed,
            c.deadline,
            c.status,
            c.fundsWithdrawn,
            c.createdAt,
            c.contributorCount
        );
    }
    
    /**
     * @notice Get detailed campaign info
     */
    function getCampaignDetails(uint256 _campaignId)
        external
        view
        campaignExists(_campaignId)
        returns (
            uint256 targetAmount,
            uint256 totalContributed,
            uint256 totalRequired,
            uint256 platformFee,
            uint256 remainingAmount,
            uint256 progressPercentage,
            bool isExpired,
            CampaignStatus status
        )
    {
        Campaign memory c = campaigns[_campaignId];
        targetAmount = c.targetAmount;
        totalContributed = c.totalContributed;
        totalRequired = calculateTotalRequired(c.targetAmount);
        platformFee = calculatePlatformFee(c.targetAmount);
        remainingAmount = totalRequired > c.totalContributed 
            ? totalRequired - c.totalContributed 
            : 0;
        
        if (totalRequired > 0) {
            unchecked {
                progressPercentage = (c.totalContributed * 100) / totalRequired;
            }
        }
        
        isExpired = block.timestamp >= c.deadline;
        status = c.status;
    }
    
    /**
     * @notice Get contribution amount for a contributor
     */
    function getContribution(uint256 _campaignId, address _contributor)
        external
        view
        returns (uint256)
    {
        return contributions[_campaignId][_contributor];
    }
    
    /**
     * @notice Get campaign progress percentage
     */
    function getCampaignProgress(uint256 _campaignId)
        public
        view
        campaignExists(_campaignId)
        returns (uint256)
    {
        Campaign memory c = campaigns[_campaignId];
        uint256 totalRequired = calculateTotalRequired(c.targetAmount);
        if (totalRequired == 0) return 0;
        
        unchecked {
            return (c.totalContributed * 100) / totalRequired;
        }
    }
    
    /**
     * @notice Check if campaign has expired
     */
    function isCampaignExpired(uint256 _campaignId)
        external
        view
        campaignExists(_campaignId)
        returns (bool)
    {
        return block.timestamp >= campaigns[_campaignId].deadline;
    }
    
    /**
     * @notice Get campaigns in a range (pagination)
     */
    function getCampaigns(uint256 _startId, uint256 _count)
        external
        view
        returns (
            address[] memory creators,
            uint256[] memory targetAmounts,
            uint256[] memory totalContributed,
            CampaignStatus[] memory statuses
        )
    {
        require(_count > 0 && _count <= 50, "Count 1-50");
        require(_startId < campaignCounter, "Invalid start");
        
        uint256 endId = _startId + _count;
        if (endId > campaignCounter) {
            endId = campaignCounter;
        }
        
        uint256 resultCount = endId - _startId;
        
        creators = new address[](resultCount);
        targetAmounts = new uint256[](resultCount);
        totalContributed = new uint256[](resultCount);
        statuses = new CampaignStatus[](resultCount);
        
        for (uint256 i = 0; i < resultCount; ) {
            Campaign memory c = campaigns[_startId + i];
            creators[i] = c.creator;
            targetAmounts[i] = c.targetAmount;
            totalContributed[i] = c.totalContributed;
            statuses[i] = c.status;
            
            unchecked { i++; }
        }
    }
    
    /**
     * @notice Check if address has contributed
     */
    function hasUserContributed(uint256 _campaignId, address _user)
        external
        view
        returns (bool)
    {
        return hasContributed[_campaignId][_user];
    }
    
    /**
     * @notice Get platform statistics
     */
    function getPlatformStats()
        external
        view
        returns (
            uint256 totalCampaigns,
            uint256 activeCampaigns,
            uint256 fundedCampaigns,
            uint256 platformTVL
        )
    {
        return (
            campaignCounter,
            activeCampaignsCount,
            fundedCampaignsCount,
            totalValueLocked
        );
    }
    
    // ==================== ADMIN FUNCTIONS ====================
    
    function setMinContribution(uint256 _newMinContribution) external onlyOwner {
        require(_newMinContribution > 0, "Must be > 0");
        require(_newMinContribution <= 1 ether, "Too high");
        
        uint256 oldAmount = minContribution;
        minContribution = _newMinContribution;
        
        emit MinContributionUpdated(oldAmount, _newMinContribution);
    }
    
    function setCampaignCreationFee(uint256 _newFee) external onlyOwner {
        require(_newFee <= 1 ether, "Fee too high");
        
        uint256 oldFee = campaignCreationFee;
        campaignCreationFee = _newFee;
        
        emit CampaignCreationFeeUpdated(oldFee, _newFee);
    }
    
    function proposePause() external onlyOwner {
        require(!pauseProposed, "Already proposed");
        require(!paused(), "Already paused");
        
        pauseProposed = true;
        pauseProposedAt = block.timestamp;
        
        emit PauseProposed(pauseProposedAt, pauseProposedAt + ADMIN_TIME_LOCK);
    }
    
    function executePause() external onlyOwner {
        require(pauseProposed, "Not proposed");
        require(
            block.timestamp >= pauseProposedAt + ADMIN_TIME_LOCK,
            "Time lock active"
        );
        
        pauseProposed = false;
        _pause();
    }
    
    function cancelPause() external onlyOwner {
        require(pauseProposed, "No pause proposed");
        
        pauseProposed = false;
        pauseProposedAt = 0;
        
        emit PauseCancelled();
    }
    
    function emergencyPause() external onlyOwner {
        require(!paused(), "Already paused");
        
        _pause();
        emit EmergencyPauseExecuted(msg.sender);
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
}
