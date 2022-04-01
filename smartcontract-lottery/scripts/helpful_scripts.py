# writing this file to pull from any network we'd like to

from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # accounts[0] - brownies ganache account
    # accounts.add("env") - our env variables
    # accounts.load("id") - if we added an account, you can see accounts by "brownie accounts list"
    if index:  # means if index is passed in the get_account function
        return accounts[index]
    if id:  # means if id is passed in the get_account function
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:  # if local network
        return accounts[0]
    return accounts.add(
        config["wallets"]["from_key"]
    )  # if nothings is defined, this account will return automatically


contract_to_mock = {  # mapping of contract name to type
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(
    contract_name,
):  # function for us to get a contract if its already deployed mock contract or a real one
    """This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and
    return that mock contract.
        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if (
            len(contract_type) <= 0
        ):  # checking how many mockv3s have deployed, if 0 we are gonna deploy
            # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]  # getting the latest deployed contract
        # MockV3Aggregator[-1]
    else:  # however if we are on a test net, below we get its real address and return mock contract
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI: we have the ABI from the mock
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # above line is transfering certain amount to contract address, which is lottery in this case
    # below two lines use interface option to transfer link token
    # in cases we dont have the contract but only the interface, we need to know how to use it as below
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx


def main():
    deploy_mocks()
    get_account()
    get_contract()
    fund_with_link()
