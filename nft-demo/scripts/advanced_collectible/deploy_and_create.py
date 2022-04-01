from scripts.helpful_scripts import (
    get_account,
    OPENSEA_URL,
    get_contract,
    fund_with_link,
)
from brownie import AdvancedCollectible, network, config


def deploy_and_create():
    account = get_account()
    # We want to be able to use the deployed contracts if we are on a testnet
    # Otherwise, we want to deploy some mocks and use those
    # Since opensea marketplace works only with rinkeby testnet, we will use rinkeby
    advanced_collectible = AdvancedCollectible.deploy(
        get_contract("vrf_coordinator"),
        # config["networks"][network.show_active()]["vrf_coordinator"],
        get_contract("link_token"),
        # config["networks"][network.show_active()]["link_token"], link token is required to get random number
        config["networks"][network.show_active()]["keyhash"],
        # these arent contracts, these can stay
        config["networks"][network.show_active()]["fee"],
        # these arent contracts, these can stay
        {"from": account},
    )
    fund_with_link(advanced_collectible.address)
    # in order to get a random number we need to fund with link token
    creating_tx = advanced_collectible.createCollectible({"from": account})
    # above will create our collectible
    creating_tx.wait(1)
    print("New token has been created!")
    return advanced_collectible, creating_tx
    # here we return creating_tx to get requestid as createCollectible emits requestid
    # details in test file, we also see we can return parameters as event


def main():
    deploy_and_create()
