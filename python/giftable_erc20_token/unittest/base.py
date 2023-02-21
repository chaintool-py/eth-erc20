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
from giftable_erc20_token import GiftableToken

logg = logging.getLogger(__name__)


class TestGiftableToken(EthTesterCase):

    expire = 0

    def setUp(self):
        super(TestGiftableToken, self).setUp()
        self.conn = RPCConnection.connect(self.chain_spec, 'default')
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.conn)
        c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        self.symbol = 'FOO'
        self.name = 'Foo Token'
        self.decimals = 16
        (tx_hash, o) = c.constructor(self.accounts[0], self.name, self.symbol, self.decimals, expire=self.expire)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)
        self.address = to_checksum_address(r['contract_address'])
        logg.debug('published on address {} with hash {}'.format(self.address, tx_hash))

        self.initial_supply = 1 << 40
        (tx_hash, o) = c.mint_to(self.address, self.accounts[0], self.accounts[0], self.initial_supply)
        r = self.conn.do(o)
        o = receipt(tx_hash)
        r = self.conn.do(o)
        self.assertEqual(r['status'], 1)


class TestGiftableExpireToken(TestGiftableToken):

    expire = int(time.time()) + 100000

    def setUp(self):
        super(TestGiftableExpireToken, self).setUp()
