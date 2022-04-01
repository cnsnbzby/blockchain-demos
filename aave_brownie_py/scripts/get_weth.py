from scripts.helpful_scripts import get_account
from brownie import interface, config, network, accounts
import sys


def get_weth():
    """
    Mints WETH by depositing ETH.
    """
    account = get_account()
    weth = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"]
    )  # this will help us get abi
    tx = weth.deposit(
        {"from": account, "value": 0.1 * 10 ** 18}
    )  # this will deposit 0.1 from account to defined weth
    tx.wait(1)  # waiting for txn to complete
    print("Received 0.1 WETH")


def main():
    get_weth()
