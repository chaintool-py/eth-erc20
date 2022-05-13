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
from chainlib.eth.cli.arg import (
        Arg,
        ArgFlag,
        process_args,
        )
from chainlib.eth.cli.config import (
        Config,
        process_config,
        )
from chainlib.eth.address import to_checksum_address
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.gas import (
        OverrideGasOracle,
        balance,
        )
from chainlib.chain import ChainSpec
from chainlib.eth.settings import process_settings
from chainlib.settings import ChainSettings
from chainlib.eth.cli.log import process_log

# local imports
from eth_erc20 import ERC20

logg = logging.getLogger()


def process_config_local(config, arg, args, flags):
    config.add(args.item, '_ITEM', False)
    return config


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_READ | arg_flags.EXEC

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('item', type=str, nargs='?', help='display only given data item')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags)
config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    token_address = settings.get('EXEC')
    item = config.get('_ITEM')
    conn = settings.get('CONN')
    g = ERC20(
            chain_spec=settings.get('CHAIN_SPEC'),
            gas_oracle=settings.get('GAS_ORACLE'),
            )


    if not item or item == 'name':
        name_o = g.name(token_address)
        r = conn.do(name_o)
        token_name = g.parse_name(r)
        s = ''
        if not item or not args.raw:
            s = 'Name: '
        s += token_name
        print(s)
        if item == 'name':
            sys.exit(0)

    if not item or item == 'symbol':
        symbol_o = g.symbol(token_address)
        r = conn.do(symbol_o)
        token_symbol = g.parse_symbol(r)
        s = ''
        if not item or not args.raw:
            s = 'Symbol: '
        s += token_symbol
        print(s)
        if item == 'symbol':
            sys.exit(0)

    if not item or item == 'decimals':
        decimals_o = g.decimals(token_address)
        r = conn.do(decimals_o)
        decimals = int(strip_0x(r), 16)
        s = ''
        if not item or not args.raw:
            s = 'Decimals: '
        s += str(decimals)
        print(s)
        if item == 'decimals':
            sys.exit(0)

    if not item or item == 'supply':
        supply_o = g.total_supply(token_address)
        r = conn.do(supply_o)
        supply = int(strip_0x(r), 16)
        s = ''
        if not item or not args.raw:
            s = 'Supply: '
        s += str(supply)
        print(s)
        if item == 'supply':
            sys.exit(0)


if __name__ == '__main__':
    main()
