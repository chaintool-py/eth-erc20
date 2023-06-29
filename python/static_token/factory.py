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
from static_token.data import data_dir

logg = logging.getLogger(__name__)


class StaticToken(TxFactory):

    __abi = None
    __bytecode = None

    def constructor(self, sender_address, name, symbol, decimals, supply, tx_format=TxFormat.JSONRPC):
        code = StaticToken.bytecode()
        enc = ABIContractEncoder()
        enc.string(name)
        enc.string(symbol)
        enc.uint256(decimals)
        enc.uint256(supply)
        code += enc.get()
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.finalize(tx, tx_format)


    @staticmethod
    def gas(code=None):
        return 2000000


    @staticmethod
    def abi():
        if StaticToken.__abi == None:
            f = open(os.path.join(data_dir, 'StaticToken.json'), 'r')
            StaticToken.__abi = json.load(f)
            f.close()
        return StaticToken.__abi


    @staticmethod
    def bytecode():
        if StaticToken.__bytecode == None:
            f = open(os.path.join(data_dir, 'StaticToken.bin'))
            StaticToken.__bytecode = f.read()
            f.close()
        return StaticToken.__bytecode
