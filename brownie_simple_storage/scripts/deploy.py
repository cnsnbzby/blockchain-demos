from brownie import accounts, config, SimpleStorage, network

# with brownie we can directly import .sol content, as with simplestorage example here
# network keyword allows us to interact with different networks
# import os # this we use with os.getenv below

# accounts package of brownie natively understands how to deal with accounts


def deploy_simple_storage():  # def is how you define a function in python
    # in this case function is called deploy_simple_storage
    # account = accounts[0]
    # above we pick the first account in ganache local network, this only works for ganache cli
    # account = accounts.load("deneme1") # here we select deneme1 account among the mainnet/fakenet accounts we created
    # you can add new account called deneme1 by typing "brownie accounts new deneme1" in terminal
    # then see all accounts byt typing "brownie accounts list" in terminal"
    # "brownie accounts delete deneme1" to delete
    # account = accounts.add(os.getenv("PRIVATE_KEY")) # if we are using os, this (we used with import os) calls the account by private key
    # account = accounts.add(config["wallets"]["from_key"]) # this does the same as os.getenv, but this uses config in brownie
    # print(account)
    account = get_account()

    simple_storage = SimpleStorage.deploy({"from": account})
    # we always need to say which account is going to deploy this contract
    # this is how we deploy it to the chain, unlike in web3 brownie automatically knows if it is a txn or a call

    stored_value = simple_storage.retrieve()
    # we know that this is a view function which does not make a transaction
    # and only retrieve whats inside, which is 0 in this examples case
    # since it is a view function, we dont have to put account at the end, brownie knows its a call
    print(stored_value)  # this prints out 0
    transaction = simple_storage.store(13, {"from": account})
    # to update 0, we store 15,
    # since we are doing a txn, in brownie we have to add who we gonna txn from by adding "from":account part
    # as in deploy function above
    # transaction.wait(1)
    # similar to web3.py case, by wait function we select how many blocks we wanna wait
    updated_stored_value = simple_storage.retrieve()
    # calling retrieve again to see if its updated
    print(updated_stored_value)

    # above set thought us how to deploy to local chain with ganache
    # we need to automate above process and make sure that contracts are doing what we want them to do
    # this is why running and automating tests are so important


def get_account():
    # here we natively check if we are working on development network or not
    # typing "brownie networks list" in terminal will give the list
    # of all networks brownie knows to deploy
    if network.show_active() == "development":
        # development networks are the ones like ganache
        return accounts[0]
    else:  # else than developments are mainnets/fakenets (like rinkeby)
        return accounts.add(config["wallets"]["from_key"])


def main():
    deploy_simple_storage()
