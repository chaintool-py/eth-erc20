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

# external imports
from hexathon import (
        add_0x,
        strip_0x,
        even,
        )
import sha3

# external imports
import chainlib.eth.cli
from chainlib.eth.address import to_checksum_address
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

arg_flags = chainlib.eth.cli.argflag_std_read | chainlib.eth.cli.Flag.EXEC
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_positional('address', type=str, help='Ethereum address of recipient')
args = argparser.parse_args()
config = chainlib.eth.cli.Config.from_args(args, arg_flags)

wallet = chainlib.eth.cli.Wallet()
wallet.from_config(config)
holder_address = args.address
if wallet.get_signer_address() == None and holder_address != None:
    holder_address = wallet.from_address(holder_address)

rpc = chainlib.eth.cli.Rpc()
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))

token_address = config.get('_EXEC_ADDRESS')


def main():
    g = ERC20(chain_spec=chain_spec, gas_oracle=rpc.get_gas_oracle())

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
    balance_o = g.balance(token_address, holder_address)
    r = conn.do(balance_o)
   
    hx = strip_0x(r)
    balance_value = int(hx, 16)
    logg.debug('balance {} = {} decimals {}'.format(even(hx), balance_value, decimals))

    balance_str = str(balance_value)
    balance_len = len(balance_str)
    if config.get('_RAW'):
        print(balance_str)
    else:
        if balance_len < decimals + 1:
            print('0.{}'.format(balance_str.zfill(decimals)))
        else:
            offset = balance_len-decimals
            print('{}.{}'.format(balance_str[:offset],balance_str[offset:]))


if __name__ == '__main__':
    main()
