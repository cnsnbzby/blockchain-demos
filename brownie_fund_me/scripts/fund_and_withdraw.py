from brownie import FundMe
from scripts.helpful_scripts import get_account


def fund():
    fund_me = FundMe[-1]  # the most recent deployment
    account = get_account()
    entrance_fee = fund_me.getEntranceFee()
    print(entrance_fee)
    print(f"The current entry fee is {entrance_fee}")
    print("Funding")
    fund_me.fund(
        {"from": account, "value": entrance_fee}
    )  # sending a value of entrance_fee from account
    # any low level transaction data we want to send
    # with our transactions and function calls, we add above bracket piece


def withdraw():  # withdraw function for owner to withdraw
    fund_me = FundMe[-1]
    account = get_account()
    fund_me.withdraw({"from": account})


def main():
    fund()
    withdraw()
