# we are on this test because we want the code to be able to work independent of the network we are working on

from scripts.helpful_scripts import (
    get_account,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)  # method to import functions from other scripts
from scripts.deploy import (
    deploy_fund_me,
)  # method to import functions from other scripts
from brownie import (
    network,
    accounts,
    exceptions,
)  # to say what exception we are expecting to see
import pytest


def test_can_fund_and_withdraw():
    account = get_account()
    fund_me = deploy_fund_me()
    entrance_fee = fund_me.getEntranceFee()
    print(entrance_fee)
    tx = fund_me.fund({"from": account, "value": entrance_fee})
    tx.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    # we want to check that the address and the amount we funded is being adequetly recorded
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == 0


def test_only_owner_can_withdraw():
    # to skip the test if we are not on a local network, check the network:
    if (
        network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS
    ):  # skip if we are not in the local bc env list
        pytest.skip("only for local testing")
    fund_me = deploy_fund_me()
    bad_actor = accounts.add()
    with pytest.raises(exceptions.VirtualMachineError):
        # for the things we want to revert in reality but see in test we use exceptions
        # here we say if this reverts it is ok
        # we want it to revert when it calls below line because withdraw function is onlyOwner allowed function
        fund_me.withdraw({"from": bad_actor})
