# this file was created for get_account() to have its own script

from re import LOCALE
from brownie import network, config, accounts, MockV3Aggregator
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
# forked environment is basically copy of a mainnet but run in local computer,
# so we need to use local accounts for it as seen below in get account function
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
# ganache-local is not development, so it will try to pull from config file
# but we want to deploy mock for our local ganache
# so, here we extend the definition

# static variables
DECIMALS = 8
STARTING_PRICE = 100000000000  # multiplying with decimals coming from get price function will make it 18 decimals


def get_account():  # here we natively check if we are working on development or not
    # typing "brownie networks list" in terminal will give the list
    # of all networks brownie knows to deploy
    if (
        # network.show_active() == "development"
        # development networks are the ones like ganache
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    else:  # else than developments are mainnets/fakenets (like rinkeby)
        return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    if len(MockV3Aggregator) <= 0:  # checks the length and if already deployed
        MockV3Aggregator.deploy(
            DECIMALS, Web3.toWei(STARTING_PRICE, "ether"), {"from": get_account()}
        )  # toWei function will just add 18 decimals to STARTING_PRICE
    print("Mocks deployed!")
    # if already a mock is deployed to whatever network we are working on, there is no need for 2 mock, thats why if statement
    # toWei function will add 18 decimals to 2000


def main():
    deploy_mocks()
    get_account()
