from BlockchainConnector import BlockchainConnector
from Database import ContractsDatabase
from Bot import open_tunnel
from params import *


def main():
    connector = BlockchainConnector()
    balance = connector.get_balance()
    print(balance)

    # block_info = connector.get_latest_block()
    # print(block_info)

    # key = private_key
    connector.load_contract()
    contract = connector.contract
    connector.key_to_account()
    # if connector.account:
    #     print("exists")
    # else:
    #     print("not exist")
    # if contract:
    #     print("exists")
    # else:
    #     print("not exist")
    # print(connector.account.address)
    # owner = contract.functions.owner().call()
    # print("owner:", owner)

    db = ContractsDatabase()
    db.insert_contract(contract_address)
    print(db.get_user_by_uid(21345346))
    print(db.get_last_contract())
    open_tunnel()


if __name__ == '__main__':
    main()
