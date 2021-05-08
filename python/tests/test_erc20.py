# standard imports
import logging
import os 

# external imports
from hexathon import (
        strip_0x,
        add_0x,
        )
from chainlib.eth.address import to_checksum_address
from chainlib.eth.tx import (
        unpack,
        TxFormat,
        )
from chainlib.eth.pytest import *

# local imports
from eth_erc20 import ERC20

logg = logging.getLogger()

contract_address = to_checksum_address('0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef')
benefactor_address = to_checksum_address('0xefdeadbeefdeadbeefdeadbeefdeadbeefdeadbe')


# TODO: use unittest instead
def test_erc20_balance(
    default_chain_spec,
        ):
    e = ERC20(default_chain_spec,)

    holder_address = to_checksum_address('0xbeefdeadbeefdeadbeefdeadbeefdeadbeefdead')
    o = e.balance_of(contract_address, holder_address)
    assert len(o['params'][0]['data']) == 64 + 8 + 2
    assert o['params'][0]['data'][:10] == add_0x('70a08231')


def test_erc20_decimals(
        default_chain_spec,
        ):
    e = ERC20(default_chain_spec)

    o = e.decimals(contract_address)
    assert o['params'][0]['data'] == add_0x('313ce567')


def test_erc20_transfer(
        keystore,
        signer,
        default_chain_spec,
        ):
    e = ERC20(default_chain_spec, signer=signer)

    addresses = keystore.list()
    (tx_hash_hex, o) = e.transfer(contract_address, addresses[0], benefactor_address, 1024)


def test_erc20_parse_transfer_request(
        keystore,
        signer,
        default_chain_spec,
        ):

    e = ERC20(default_chain_spec, signer=signer)

    addresses = keystore.list()
    (tx_hash_hex, o) = e.transfer(contract_address, addresses[0], benefactor_address, 1024, tx_format=TxFormat.RLP_SIGNED)
    b = bytes.fromhex(strip_0x(o))

    #chain_spec = ChainSpec('evm', 'foo', 1, 'bar')
    tx = unpack(b, default_chain_spec)
    r = ERC20.parse_transfer_request(tx['data'])
    assert r[0] == benefactor_address
    assert r[1] == 1024
