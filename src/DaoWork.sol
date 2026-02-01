// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract DaoWork {
    // ---------------------------------------------------------------------
    // Job identity
    // ---------------------------------------------------------------------

    uint256 public nextJobId;

    // ---------------------------------------------------------------------
    // Job state
    // ---------------------------------------------------------------------

    mapping(uint256 => address) public creator;
    mapping(uint256 => bool) public finalized;
    mapping(uint256 => bytes32) public workReceipt;

    // ---------------------------------------------------------------------
    // Account credit
    // ---------------------------------------------------------------------

    mapping(address => uint256) public credit;

    // ---------------------------------------------------------------------
    // Job creation
    // ---------------------------------------------------------------------

    function createJob() external payable returns (uint256 jobId) {
        require(msg.value > 0, "stake required");

        jobId = nextJobId;
        nextJobId++;

        creator[jobId] = msg.sender;
        credit[msg.sender] += msg.value;
    }

    // ---------------------------------------------------------------------
    // Work submission
    // ---------------------------------------------------------------------

    function submitWork(uint256 jobId, bytes32 receipt) external {
        require(jobId < nextJobId, "job does not exist");
        require(!finalized[jobId], "job already finalized");
        require(workReceipt[jobId] == bytes32(0), "work already submitted");
        require(receipt != bytes32(0), "invalid receipt");

        workReceipt[jobId] = receipt;
    }

    // ---------------------------------------------------------------------
    // Job finalization
    // ---------------------------------------------------------------------

    function finalize(uint256 jobId) external {
        require(jobId < nextJobId, "job does not exist");
        require(msg.sender == creator[jobId], "not job creator");
        require(!finalized[jobId], "job already finalized");
        require(workReceipt[jobId] != bytes32(0), "no work submitted");

        finalized[jobId] = true;
    }

    // ---------------------------------------------------------------------
    // Credit withdrawal
    // ---------------------------------------------------------------------

    function withdraw(uint256 amount) external {
        require(credit[msg.sender] >= amount, "insufficient credit");

        credit[msg.sender] -= amount;

        (bool sent,) = msg.sender.call{value: amount}("");
        require(sent, "eth transfer failed");
    }
}
