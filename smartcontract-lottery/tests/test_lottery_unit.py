from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest


def test_get_entrance_fee():  # writing a get entrance fee test that will work on local development network
    if (
        network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS
    ):  # since we only want to test this if we local environment
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()  # this gives us our lottery contract
    # Act
    # below is calculation of expected amount
    # 2,000 eth / usd
    # usdEntryFee is 50
    # 2000/1 == 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = (
        lottery.getEntranceFee()
    )  # we want to make sure entrance fee is what we expect it to be
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # we want to make sure that people cannot enter by paying entrence fee before lottery is started
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act / Assert
    # since lottery has not started and it will revert, we use exceptions
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():  # we want to see if we can correctly add players into players array
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():  # to see if we end the lottery
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)  # to end the lottery we need to send some LINK
    lottery.endLottery({"from": account})
    assert (
        lottery.lottery_state() == 2
    )  # since we change the state of lottery to end it, we need to check if the state is changed


def test_can_pick_winner_correctly():  # to check if we can pick a random winner
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    transaction = lottery.endLottery(
        {"from": account}
    )  # this txn carries events section, which we pick below function and requestId from
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777  # this is the random number we set manually for callBackWithRandomness function
    get_contract(
        "vrf_coordinator"
    ).callBackWithRandomness(  # we have to pretend like we are a chainlink node to call callBackWithRandomness
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )  # this is us dummying getting a response from a chainlink node and this is how we mock repsonses in our tests
    # 777 % 3 = 0
    assert (
        lottery.recentWinner() == account
    )  # to see if account is winner since mod result is 0
    assert lottery.balance() == 0  # to see if all the money is transferred
    assert account.balance() == starting_balance_of_account + balance_of_lottery
