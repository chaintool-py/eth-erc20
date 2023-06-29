# standard imports
import logging
import time

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.connection import RPCConnection
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address

# local imports
from static_token import StaticToken
from eth_erc20.unittest import TestInterface

logg = logging.getLogger(__name__)


class TestStaticToken(EthTesterCase, TestInterface):

    def setUp(self):
        super(TestStaticToken, self).setUp()
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.conn)
        c = StaticToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        self.symbol = 'FOO'
        self.name = 'Foo Token'
        self.decimals = 16
        self.initial_supply = 1 << 24
        (tx_hash, o) = c.constructor(self.accounts[0], self.name, self.symbol, self.decimals, self.initial_supply)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)
        self.address = to_checksum_address(r['contract_address'])
        logg.debug('published statictoken on address {} with hash {}'.format(self.address, tx_hash))
