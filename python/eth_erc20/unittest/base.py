# standard imports
import logging

# external imports
from chainlib.eth.unittest.ethtester import EthTesterCase
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import OverrideGasOracle
from chainlib.eth.tx import (
        transaction,
        receipt,
        )
from hexathon import strip_0x

# local imports
from eth_erc20 import ERC20

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger(__name__)


class TestInterface:

    def test_balance(self):
        c = ERC20(self.chain_spec)
        o = c.balance_of(self.address, self.accounts[0], sender_address=self.accounts[0])
        r = self.conn.do(o)
        balance = ERC20.parse_balance(r)
        self.assertEqual(self.initial_supply, balance)


    def test_supply(self):
        c = ERC20(self.chain_spec)
        o = c.total_supply(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        supply = ERC20.parse_total_supply(r)
        self.assertEqual(self.initial_supply, supply)


    def test_name(self):
        c = ERC20(self.chain_spec)
        o = c.name(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        name = ERC20.parse_name(r)
        self.assertEqual(self.name, name)


    def test_symbol(self):
        c = ERC20(self.chain_spec)
        o = c.symbol(self.address, sender_address=self.accounts[0])
        r = self.conn.do(o)
        symbol = ERC20.parse_symbol(r)
        self.assertEqual(self.symbol, symbol)


    def test_direct_transfer(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.conn)
        gas_oracle = OverrideGasOracle(limit=100000, conn=self.conn)
        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)

        (tx_hash, o) = c.transfer(self.address, self.accounts[0], self.accounts[1], 1000)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.balance_of(self.address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, self.initial_supply - 1000)

        o = c.balance_of(self.address, self.accounts[1], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, 1000)

        o = transaction(tx_hash)
        r = self.rpc.do(o)
        data = c.parse_transfer_request(r['data'])
        self.assertEqual(data[0], strip_0x(self.accounts[1]))
        self.assertEqual(data[1], 1000)


    def test_transfer_from(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.conn)
        gas_oracle = OverrideGasOracle(limit=100000, conn=self.conn)
        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash, o) = c.approve(self.address, self.accounts[0], self.accounts[1], 1000)
        self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.allowance(self.address, self.accounts[0], self.accounts[1], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        allowance = c.parse_allowance(r)
        self.assertEqual(allowance, 1000)

        o = transaction(tx_hash)
        r = self.rpc.do(o)
        data = c.parse_approve_request(r['data'])
        self.assertEqual(data[0], strip_0x(self.accounts[1]))
        self.assertEqual(data[1], 1000)

        nonce_oracle = RPCNonceOracle(self.accounts[1], conn=self.conn)
        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash, o) = c.transfer_from(self.address, self.accounts[1], self.accounts[0], self.accounts[2], 1001)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)

        o = transaction(tx_hash)
        r = self.rpc.do(o)
        data = c.parse_transfer_from_request(r['data'])
        self.assertEqual(data[0], strip_0x(self.accounts[0]))
        self.assertEqual(data[1], strip_0x(self.accounts[2]))
        self.assertEqual(data[2], 1001)

        (tx_hash, o) = c.transfer_from(self.address, self.accounts[1], self.accounts[0], self.accounts[2], 1000)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)

        o = c.balance_of(self.address, self.accounts[0], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, self.initial_supply - 1000)

        o = c.balance_of(self.address, self.accounts[2], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        balance = c.parse_balance(r)
        self.assertEqual(balance, 1000)


    def test_revoke_approve(self):
        nonce_oracle = RPCNonceOracle(self.accounts[0], conn=self.conn)
        gas_oracle = OverrideGasOracle(limit=100000, conn=self.conn)
        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash, o) = c.approve(self.address, self.accounts[0], self.accounts[1], 1000)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)
        
        (tx_hash, o) = c.approve(self.address, self.accounts[0], self.accounts[1], 999)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)
     
        (tx_hash, o) = c.approve(self.address, self.accounts[0], self.accounts[1], 0)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 1)
 
        o = c.allowance(self.address, self.accounts[0], self.accounts[1], sender_address=self.accounts[0])
        r = self.rpc.do(o)
        allowance = c.parse_allowance(r)
        self.assertEqual(allowance, 0)

        nonce_oracle = RPCNonceOracle(self.accounts[1], conn=self.conn)
        c = ERC20(self.chain_spec, signer=self.signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
        (tx_hash, o) = c.transfer_from(self.address, self.accounts[1], self.accounts[0], self.accounts[2], 1)
        r = self.rpc.do(o)
        o = receipt(tx_hash)
        r = self.rpc.do(o)
        self.assertEqual(r['status'], 0)
