from hexbytes import HexBytes
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.types import TxParams
from params import *


class BlockchainConnector:
    def __init__(self):
        self.account = None
        self.contract = None
        self._w3 = Web3(HTTPProvider(HTTP_provider))
        self._w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contractAddress = contract_address
        self.walletAddress = defaultWalletAddress
        self.key = private_key

    def get_balance(self, address: str = None):
        if address is None:
            return self._w3.eth.get_balance(self.walletAddress)
        else:
            return self._w3.eth.get_balance(address)

    def get_latest_block(self):
        return self._w3.eth.get_block('latest')

    def get_contract_owner(self):
        if self.contract is None:
            return None
        else:
            return self.contract.functions.owner().call()

    def key_to_account(self, key: str = None):
        if key is None:
            key_ = self.key
        else:
            key_ = key
        private_key_account = Web3.toHex(hexstr=key_)
        # return self._w3.eth.account.from_key(private_key)
        self.account = self._w3.eth.account.from_key(private_key_account)

    def load_contract(self, address: str = None):
        # return self._w3.eth.contract(address, abi=ABI)
        if address is None:
            address_ = self.contractAddress
        else:
            address_ = address
        self.contract = self._w3.eth.contract(address_, abi=ABI)

    def create_tx(self):
        nonce = self._w3.eth.get_transaction_count(self.account.address)
        tx = {
            'gas': 250000,
            'gasPrice': Web3.toWei(1, 'gwei'),
            'nonce': nonce
        }
        return tx

    def sign_tx(self, tx: TxParams):
        return self.account.signTransaction(tx)

    def send_tx(self, tx: HexBytes):
        tx_hash = self._w3.eth.send_raw_transaction(tx)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def mint_NFT(self, param):
        tx = self.create_tx()
        transaction = self.contract.functions.mintNFT(self.walletAddress, param). \
            buildTransaction(tx)
        signed_tx = self.sign_tx(transaction)
        receipt = self.send_tx(signed_tx.rawTransaction)
        print(f'Tx receipt: {receipt}')

    def ownership_transfer(self, new_wallet):
        tx = self.create_tx()
        transaction = self.contract.functions.transferOwnership(new_wallet). \
            buildTransaction(tx)
        signed_tx = self.sign_tx(transaction)
        receipt = self.send_tx(signed_tx.rawTransaction)
        self.walletAddress = new_wallet
        print(f'Tx receipt: {receipt}')
