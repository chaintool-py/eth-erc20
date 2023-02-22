# standard imports
import os
import unittest
import json
import logging
import datetime

# external imports
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from chainlib.eth.block import (
        block_latest,
        block_by_number,
    )

# local imports
from giftable_erc20_token import GiftableToken
from giftable_erc20_token.unittest import TestGiftableExpireToken

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

testdir = os.path.dirname(__file__)


class TestExpire(TestGiftableExpireToken):

    def setUp(self):
        super(TestExpire, self).setUp()


    def test_expires(self):
        mint_amount = self.initial_supply
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)

        (tx_hash, o) = c.transfer(self.address, self.accounts[0], self.accounts[1], int(mint_amount / 2))
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        self.backend.time_travel(self.expire + 60)
        o = block_latest()
        r = self.rpc.do(o)
        o = block_by_number(r)
        r = self.rpc.do(o)
        self.assertGreaterEqual(r['timestamp'], self.expire)
        
        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.transfer(self.address, self.accounts[0], self.accounts[1], 1)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)
        
        nonce_oracle = RPCNonceOracle(self.accounts[1], self.rpc)
        c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.transfer(self.address, self.accounts[1], self.accounts[0], 1)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)

        o = c.balance_of(self.address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, int(mint_amount / 2))

        o = c.balance_of(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance += c.parse_balance(r)
        self.assertEqual(balance, mint_amount)

        o = c.total_supply(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        supply = c.parse_balance(r)
        self.assertEqual(supply, mint_amount)


    def test_burn(self):
        mint_amount = self.initial_supply
        nonce_oracle = RPCNonceOracle(self.accounts[1], self.rpc)
        c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.burn(self.address, self.accounts[1], int(mint_amount / 4))
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)

        nonce_oracle = RPCNonceOracle(self.accounts[0], self.rpc)
        c = GiftableToken(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle)
        (tx_hash, o) = c.burn(self.address, self.accounts[0], int(mint_amount / 4))
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.burned(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        burned = c.parse_balance(r)
        self.assertEqual(burned, int(mint_amount / 4))

        o = c.balance_of(self.address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, mint_amount - burned)

        o = c.total_supply(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, mint_amount - burned)

        o = c.total_minted(self.address, sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, mint_amount)


if __name__ == '__main__':
    unittest.main()
