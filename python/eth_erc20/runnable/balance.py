#!python3

"""Token balance query script

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import sys
import os
import json
import argparse
import logging

# third-party imports
from hexathon import (
        add_0x,
        strip_0x,
        even,
        )
import sha3
from eth_abi import encode_single

# external imports
from chainlib.eth.address import to_checksum
from chainlib.jsonrpc import (
        jsonrpc_template,
        jsonrpc_result,
        )
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.gas import (
        OverrideGasOracle,
        balance,
        )
from chainlib.chain import ChainSpec

# local imports
from eth_erc20 import ERC20

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

default_abi_dir = os.environ.get('ETH_ABI_DIR', '/usr/share/local/cic/solidity/abi')
default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default=default_eth_provider, type=str, help='Web3 provider url (http only)')
argparser.add_argument('-a', '--token-address', dest='a', required=True, type=str, help='Token address. If not set, will return gas balance')
argparser.add_argument('-f', '--format', dest='f', type=str, default='terminal', help='Output format [terminal (default), raw, brief]')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('address', type=str, help='Account address')
args = argparser.parse_args()


if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

conn = EthHTTPConnection(args.p)
gas_oracle = OverrideGasOracle(conn)

address = to_checksum(args.address)
if not args.u and address != add_0x(args.address):
    raise ValueError('invalid checksum address')

token_address = args.a

fmt = args.f

chain_spec = ChainSpec.from_chain_str(args.i)


def main():
    r = None
    decimals = 18
    g = ERC20(chain_spec=chain_spec)
    # determine decimals
    decimals_o = g.decimals(token_address)
    r = conn.do(decimals_o)
    decimals = int(strip_0x(r), 16)
    logg.info('decimals {}'.format(decimals))

    name_o = g.name(token_address)
    r = conn.do(name_o)
    token_name = g.parse_name(r)
    logg.info('name {}'.format(token_name))

    symbol_o = g.symbol(token_address)
    r = conn.do(symbol_o)
    token_symbol = g.parse_symbol(r)
    logg.info('symbol {}'.format(token_symbol))


    # get balance
    balance_o = g.balance(token_address, address)
    r = conn.do(balance_o)
   
    hx = strip_0x(r)
    balance_value = int(hx, 16)
    logg.debug('balance {} = {} decimals {}'.format(even(hx), balance_value, decimals))

    balance_str = str(balance_value)
    balance_len = len(balance_str)
    if fmt == 'terminal':
        sys.stdout.write('{} ({}): '.format(token_name, token_symbol))
    if fmt == 'raw':
        print(balance_str)
    else:
        if balance_len < decimals + 1:
            print('0.{}'.format(balance_str.zfill(decimals)))
        else:
            offset = balance_len-decimals
            print('{}.{}'.format(balance_str[:offset],balance_str[offset:]))


if __name__ == '__main__':
    main()
