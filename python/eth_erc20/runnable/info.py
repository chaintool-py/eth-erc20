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
args = argparser.parse_args()
config = chainlib.eth.cli.Config.from_args(args, arg_flags)

rpc = chainlib.eth.cli.Rpc()
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))

token_address = config.get('_EXEC_ADDRESS')


def main():
    g = ERC20(chain_spec=chain_spec, gas_oracle=rpc.get_gas_oracle())

    name_o = g.name(token_address)
    r = conn.do(name_o)
    token_name = g.parse_name(r)
    print('Name: {}'.format(token_name))

    symbol_o = g.symbol(token_address)
    r = conn.do(symbol_o)
    token_symbol = g.parse_symbol(r)
    print('Symbol: {}'.format(token_symbol))

    decimals_o = g.decimals(token_address)
    r = conn.do(decimals_o)
    decimals = int(strip_0x(r), 16)
    print('Decimals: {}'.format(decimals))

    supply_o = g.total_supply(token_address)
    r = conn.do(supply_o)
    supply = int(strip_0x(r), 16)
    print('Total supply: {}'.format(supply))


if __name__ == '__main__':
    main()
