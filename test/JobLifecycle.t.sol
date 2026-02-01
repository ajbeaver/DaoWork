// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/DaoWork.sol";

contract JobLifecycleTest is Test {
    DaoWork dao;

    // allow this test contract to receive ETH
    receive() external payable {}

    function setUp() public {
        dao = new DaoWork();
        vm.deal(address(this), 10 ether);
    }

    function test_cannot_finalize_nonexistent_job() public {
        (bool ok,) = address(dao).call(
            abi.encodeWithSignature("finalize(uint256)", 1)
        );

        assertFalse(ok);
    }

    function test_cannot_finalize_job_twice() public {
        uint256 jobId = dao.createJob{value: 1 ether}();
        bytes32 receipt = keccak256("work");

        dao.submitWork(jobId, receipt);
        dao.finalize(jobId);

        (bool ok,) = address(dao).call(
            abi.encodeWithSignature("finalize(uint256)", jobId)
        );

        assertFalse(ok);
    }

    function test_only_creator_can_finalize() public {
        uint256 jobId = dao.createJob{value: 1 ether}();
        bytes32 receipt = keccak256("work");

        dao.submitWork(jobId, receipt);

        vm.prank(address(0xA11CE));
        (bool ok,) = address(dao).call(
            abi.encodeWithSignature("finalize(uint256)", jobId)
        );
        assertFalse(ok);

        dao.finalize(jobId);

        (ok,) = address(dao).call(
            abi.encodeWithSignature("finalize(uint256)", jobId)
        );
        assertFalse(ok);
    }

    function test_cannot_create_job_without_stake() public {
        (bool ok,) = address(dao).call(
            abi.encodeWithSignature("createJob()")
        );

        assertFalse(ok);
    }

    function test_posting_job_increases_credit() public {
        uint256 beforeCredit = dao.credit(address(this));

        dao.createJob{value: 1 ether}();

        uint256 afterCredit = dao.credit(address(this));

        assertEq(afterCredit, beforeCredit + 1 ether);
    }

    function test_withdraw_reduces_credit_and_transfers_eth() public {
        dao.createJob{value: 2 ether}();

        uint256 beforeCredit = dao.credit(address(this));
        uint256 beforeBalance = address(this).balance;

        dao.withdraw(1 ether);

        uint256 afterCredit = dao.credit(address(this));
        uint256 afterBalance = address(this).balance;

        assertEq(afterCredit, beforeCredit - 1 ether);
        assertEq(afterBalance, beforeBalance + 1 ether);
    }

    function test_cannot_withdraw_more_than_credit() public {
        dao.createJob{value: 1 ether}();

        (bool ok,) = address(dao).call(
            abi.encodeWithSignature("withdraw(uint256)", 2 ether)
        );

        assertFalse(ok);
    }

    function test_cannot_submit_work_for_nonexistent_job() public {
        (bool ok,) = address(dao).call(
            abi.encodeWithSignature(
                "submitWork(uint256,bytes32)",
                0,
                bytes32("fake")
            )
        );

        assertFalse(ok);
    }

    function test_cannot_submit_empty_receipt() public {
        uint256 jobId = dao.createJob{value: 1 ether}();

        (bool ok,) = address(dao).call(
            abi.encodeWithSignature(
                "submitWork(uint256,bytes32)",
                jobId,
                bytes32(0)
            )
        );

        assertFalse(ok);
    }

    function test_can_submit_work_for_valid_job() public {
        uint256 jobId = dao.createJob{value: 1 ether}();

        bytes32 receipt = keccak256("x plus y equals z");

        dao.submitWork(jobId, receipt);

        // if this did not revert, the test passes
        assertTrue(true);
    }

    function test_cannot_submit_work_twice_for_same_job() public {
        uint256 jobId = dao.createJob{value: 1 ether}();

        bytes32 receipt = keccak256("first");

        dao.submitWork(jobId, receipt);

        (bool ok,) = address(dao).call(
            abi.encodeWithSignature(
                "submitWork(uint256,bytes32)",
                jobId,
                keccak256("second")
            )
        );

        assertFalse(ok);
    }

    function test_cannot_finalize_without_work() public {
        uint256 jobId = dao.createJob{value: 1 ether}();

        (bool ok,) = address(dao).call(
            abi.encodeWithSignature("finalize(uint256)", jobId)
        );

        assertFalse(ok);
    }

    function test_cannot_submit_work_after_finalization() public {
        uint256 jobId = dao.createJob{value: 1 ether}();
        bytes32 receipt = keccak256("work");

        dao.submitWork(jobId, receipt);
        dao.finalize(jobId);

        (bool ok,) = address(dao).call(
            abi.encodeWithSignature(
                "submitWork(uint256,bytes32)",
                jobId,
                keccak256("late work")
            )
        );

        assertFalse(ok);
    }
    function testFuzz_cannot_finalize_invalid_jobId(uint256 jobId) public {
        vm.assume(jobId >= dao.nextJobId());

        (bool ok,) = address(dao).call(
            abi.encodeWithSignature("finalize(uint256)", jobId)
        );

        assertFalse(ok);
    }
    function testFuzz_withdraw_respects_credit_bounds(uint256 amount) public {
        dao.createJob{value: 1 ether}();

        uint256 credit = dao.credit(address(this));

        if (amount > credit) {
            (bool ok,) = address(dao).call(
                abi.encodeWithSignature("withdraw(uint256)", amount)
            );
            assertFalse(ok);
        } else {
            uint256 beforeBalance = address(this).balance;
            dao.withdraw(amount);
            assertEq(address(this).balance, beforeBalance + amount);
        }
    }
}
