from brownie import FundMe, network, config, MockV3Aggregator
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)

# above line imports the get account fucntion from our helpful_scripts.py file
# having __init__.py in the same folder will say python that it can import from other scripts and packages in this project
from web3 import Web3


def deploy_fund_me():
    account = get_account()
    # since the fundme contract has changed (changing aggregatorv3interface content to global)
    # if we are on a persistent network like rinkeby, use the associated address
    # otherwise, deploy mocks
    # price_feed_address = "0x8A753747A1Fa494EC906cE90E9f37563A8AF630e"  # by this we are still hard coding the address here
    # we'd like to parameterize where we get these addresses from

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # above line says if we are not in local blockchain networks,
        # pull price info from config file
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]

    # what if we are not on a development chain? then we have to deploy a mock
    # on all of the live networks we are working with, there is a version of price_feed_address
    # on our development chain, there wont be because it will start as blank, so we can deploy our own version
    # to do that, we need a solidity code associated with it
    # create test folder under contracts and mock ones will go there
    else:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address
        # we need to get mockv3aggregators address, and say just use the most recent V3 aggregator address

    fund_me = FundMe.deploy(
        price_feed_address,  # by adding beside rinkeby address,
        # you can actually pass variables to contructors
        # anything in constructor function in fundme.sol file, you can pass through brownie in deploy script
        {"from": account},
        # since deploy is gonna make state change to blockchain, we always need to add an account
        publish_source=config["networks"][network.show_active()].get("verify"),
        # we changed above here to verify against which chain we are on, development or mock
    )
    # deploy will make state change to blockchain
    # print(f"Contract deployed to {fund_me.address}")
    # fund_me.address is the address fund_me

    return fund_me


def main():
    deploy_fund_me()
