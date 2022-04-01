# swaping our eth for weth, which is ERC20 version of eth
# this allows easily working with other ERC20s on the aave protocol

from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
AMOUNT = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in [
        "mainnet-fork"
    ]:  # in case we need to get weth and we want to test on mainnetfork
        get_weth()
    lending_pool = get_lending_pool()
    approve_tx = approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )  # this deposit function parameters were taken from lending pool deposit method on docs.aave.com
    # erc20_address is the address of the asset
    # account.address is who is depositing
    # 0 is referral code, always zero, they dont work anymore
    tx.wait(1)
    print("Deposited!")
    # ...how much?
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # DAI in terms of ETH, below is address for conversion rate
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_dai * 95%\
    # not to pass health safety limit
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Now we will borrow!
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = (
        lending_pool.borrow(  # using borrow function of lending pool contract to borrow
            dai_address,
            Web3.toWei(amount_dai_to_borrow, "ether"),
            1,  # interest rate mode, 0 is stable, 1 is variable
            0,  # referall code
            account.address,  # who is borrowing, on behalf of
            {"from": account},
        )
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    # I made an oopsie in the video with this!!
    repay_all(Web3.toWei(amount_dai_to_borrow, "ether"), lending_pool, account)
    get_borrowable_data(lending_pool, account)
    print(
        "You just deposited, borrowed, and repayed with Aave, Brownie, and Chainlink!"
    )


def repay_all(
    amount, lending_pool, account
):  # this function is to repay everything we have
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()][
            "dai_token"
        ],  # this is the address of asset we are gonna pay
        amount,  # amount we are gonna pay
        1,  # rate mode
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)

    print("Repaid!")


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(
        price_feed_address
    )  # giving us the abi by using price feed address
    latest_price = dai_eth_price_feed.latestRoundData()[
        1
    ]  # getting latest price by using latestRoundData function
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(
    lending_pool, account
):  # this function will help us to collect all data about user
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    # all above details are returned in wei, so below we convert them to eth
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    # erc20_address is the address of token which we are actually allowing to spend
    # amount is how much we allow to spend
    # spender is who we allow to spend
    print("Approving ERC20 token...")  # to let people know what this function is doing
    erc20 = interface.IERC20(erc20_address)  # getting the erc20 token
    tx = erc20.approve(
        spender, amount, {"from": account}
    )  # approving the spender to spend stated amount
    tx.wait(1)  # waiting for one block confirmation to finish
    print("Approved!")
    return tx


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    # this lending pool address provider has the function getLendingPool which returns the address of actual lenging pool
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool  # returning lending pool abi
