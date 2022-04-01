from brownie import SimpleStorage, accounts, config

# SimpleStorage object is actually just an array
# printing SimpleStorage as below will print out <brownie.network.contract.ContractContainer object at 0x1127a4dc0>
# def read_contract():
#    print(SimpleStorage)
# printed out object is works as an array
# printing SimpleStorage as below will print out 0x14870B4225FE1bE22cE0FF1A22c52118c95C4CB6, which is the contract just deployed
# you could also see this under build-deployments-4 folder
# def read_contract():
#    print(SimpleStorage[0])
# brownie knows this because under deployments folder we have this contract just deployed
# which allows us to directly interact with this contract


def read_contract():
    simple_storage = SimpleStorage[-1]  # [-1] would give the most recent deployment
    # we already know that we need abi and address of the contract to interact with it
    # brownie already has those in deployments folder
    print(simple_storage.retrieve())


def main():
    read_contract()
