import json
import solcx  # py-solc-x is fork of py-solc and it helps with compiling
from web3 import Web3
import os  # later used to access private key
from dotenv import load_dotenv  # dotenv is to pull .env file directly

load_dotenv()  # looks for .env file and automatically imports

solcx.install_solc("v0.6.0")

from solcx import (
    compile_standard,
)  # compile_standard is the main function to compile this code

with open(
    "./SimpleStorage.sol", "r"
) as file:  # opening the file in the same folder with deploy.py
    # "r" means we are gonna only read from it
    # we are gonna call it file
    simple_storage_file = file.read()  # .read() means we are gonna read all the content
    # and put everything in simple_storage_file variable
    # print(simple_storage_file)

# Solidity source code
compiled_sol = compile_standard(  # saving compiled code to a variable called compiled_sol
    {
        "language": "Solidity",
        "sources": {
            "SimpleStorage.sol": {"content": simple_storage_file}
        },  # source is *.sol file and content is coming from file.read
        "settings": {
            "outputSelection": {  # to choose what we output when we compile this code
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                    # abi: application binary interface, long json object
                }
            }
        },
    },
    solc_version="0.6.0",
)
# print(compiled_sol)

# below is to print out compiled code to a file
with open("compiled_code.json", "w") as file:  # w for writing
    json.dump(
        compiled_sol, file
    )  # this takes compiled_sol json variable and dumps it into "file" by keeping it in json syntax

# we need bytecode to deploy, get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
# here we walk down the json file
# evm is for ethereum virtual machine and its bytecode is only understood by evm

# we need abi to deploy, get abi
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

# after getting bytecode and abi, the question is where we are going to deploy it to, which blockchain?

# ganache is used as a fake blockchain to deploy our contracts, it will be our javascript VM in remix eth
# to connect to blockchain we need http/rpc provider
# in remix metamask is our http provider

# for connecting to ganache
# w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
# for connecting to infura
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/766520b5b8aa46c2bccdab31b6e0cecd")
)

# to have info about providers go to providers page in web3.py website
# chain_id = 1337  # network id, id of the blockchain for ganache
chain_id = 4  # network id, id of the blockchain for rinkeby
my_address = "0x66633D666fE37b38c2D9e9Aca13C396b0ead151C"
# address to deploy from # this is a fake address as ones remix gives us
# private_key = "0x1772c3a28a04a28a1f11b0fdb1a6c30d61f8b7d77cd70f4e1cc5e82a2beb96bb"
# private key to sign our transactions
# always put 0x in front of keys and addresses
# above is private key before hiding it with os
private_key = os.getenv("PRIVATE_KEY")
# getting private key from .env file and preventing hard coding
# .env file is where people typically store environmental variables

# Creating the contract in Python
SimpleStorage = w3.eth.contract(
    abi=abi, bytecode=bytecode
)  # this is our contract object
# we need to build our transaction to deploy
# by deploying a contract we are making a state change
# print(SimpleStorage) prints out class 'web3._utils.datatypes.Contract'>, check documentation to explore

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)  # getting the latest nonce
# print(nonce)

# In order to deploy our contract
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction

# Submit the transaction that deploys the contract
# below we build the transaction
# creating simplestorage contract
transaction = SimpleStorage.constructor().buildTransaction(  # SimpleStorage here is contract object
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# environment variables are variables we set in terminal and command lines

# Signing the txn
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying Contract!")
# Sending the transaction to local blockchain! local in this/our case!
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Wait for the transaction to be mined, and get the transaction receipt
# waiting for block confirmation
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Done! Contract deployed to", tx_receipt.contractAddress)

# above we deployed a contract but how do we actually interact with a contract?

# while working with contract, we always need 2 things,
# -contract address
# -contract ABI

# we need to make a contract object to work with contracts
# below creating new simple_storage contract object to interact with it
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# not to check address each time, address could be derived from receipt as above
# since we compiled, we have abi already

# when making transactions in blockchain there are two ways
# call -> simulate making a call and getting a return value, as view case in remix
# transact -> actually make a state change, building a transaction and sending a transaction
# sth like retrieve, where we dont want to make a state change, we just use .call() function
print("Initial Stored value", simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call()) #
# print(simple_storage.functions.retrieve().call()) #
# if above 3 lines are executed in this order, stored value willnot change to zero and last call will still give zero
# because "call" does not make a state change, so second line does not change number from 0 to 15.
# Calling is just a simulation

# below is building a transaction to actually store some value into this contract
store_transaction = simple_storage.functions.store(13).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,  # nonce can only be used once for each transaction
        # this txn has to have different nonce than the one above
    }
)

# signing a transaction
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

# sending a txn
send_store_txn = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("Updating stored value...")

# waiting for txn to be finished
txn_receipt = w3.eth.wait_for_transaction_receipt(send_store_txn)
print("Updated!")

print(simple_storage.functions.retrieve().call())
