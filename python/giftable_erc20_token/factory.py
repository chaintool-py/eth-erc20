# standard imports
import os
import logging

# external imports
from chainlib.eth.tx import (
        TxFactory,
        TxFormat,
        )
from chainlib.hash import keccak256_string_to_hex
from chainlib.eth.contract import (
        ABIContractEncoder,
        ABIContractType,
        )

# local imports
from giftable_erc20_token.data import data_dir

logg = logging.getLogger(__name__)


class GiftableToken(TxFactory):

    __abi = None
    __bytecode = None

    def constructor(self, sender_address, name, symbol, decimals, tx_format=TxFormat.JSONRPC):
        code = GiftableToken.bytecode()
        enc = ABIContractEncoder()
        enc.string(name)
        enc.string(symbol)
        enc.uint256(decimals)
        code += enc.get()
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.finalize(tx, tx_format)


    @staticmethod
    def gas(code=None):
        return 2000000


    @staticmethod
    def abi():
        if GiftableToken.__abi == None:
            f = open(os.path.join(data_dir, 'GiftableToken.json'), 'r')
            GiftableToken.__abi = json.load(f)
            f.close()
        return GiftableToken.__abi


    @staticmethod
    def bytecode():
        if GiftableToken.__bytecode == None:
            f = open(os.path.join(data_dir, 'GiftableToken.bin'))
            GiftableToken.__bytecode = f.read()
            f.close()
        return GiftableToken.__bytecode


    def add_minter(self, contract_address, sender_address, address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('addMinter')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def remove_minter(self, contract_address, sender_address, address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('removeMinter')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def mint_to(self, contract_address, sender_address, address, value, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('mintTo')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        enc.address(address)
        enc.uint256(value)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


