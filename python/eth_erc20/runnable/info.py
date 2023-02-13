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
        stdin_arg,
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
    contract = None
    try:
        contract = config.get('_EXEC_ADDRESS')
    except KeyError:
        pass

    if contract == None:
        address = config.get('_POSARG')
        if address:
            contract = add_0x(address)
        else:
            contract = stdin_arg()

    config.add(contract, '_CONTRACT', False)
    return config


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_READ | arg_flags.EXEC | arg_flags.TAB | arg_flags.SENDER 

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('contract_address', type=str, help='Token contract address (may also be specified by -e)')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags, positional_name='contract_address')
config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    token_address = config.get('_CONTRACT')
    conn = settings.get('CONN')
    sender_address = settings.get('SENDER_ADDRESS')
    g = ERC20(
            chain_spec=settings.get('CHAIN_SPEC'),
            gas_oracle=settings.get('GAS_ORACLE'),
            )

    outkeys = config.get('_OUTARG')

    if not outkeys or 'address' in outkeys:
        name_o = g.name(token_address, sender_address=sender_address)
        r = conn.do(name_o)
        token_name = g.parse_name(r)
        s = ''
        if not config.true('_RAW'):
            s = 'Name: '
        s += token_name
        print(s)

    if not outkeys or 'symbol' in outkeys:
        symbol_o = g.symbol(token_address, sender_address=sender_address)
        r = conn.do(symbol_o)
        token_symbol = g.parse_symbol(r)
        s = ''
        if not config.true('_RAW'):
            s = 'Symbol: '
        s += token_symbol
        print(s)

    if not outkeys or 'decimals' in outkeys:
        decimals_o = g.decimals(token_address, sender_address=sender_address)
        r = conn.do(decimals_o)
        decimals = int(strip_0x(r), 16)
        s = ''
        if not config.true('_RAW'):
            s = 'Decimals: '
        s += str(decimals)
        print(s)

    if not outkeys or 'supply' in outkeys:
        supply_o = g.total_supply(token_address, sender_address=sender_address)
        r = conn.do(supply_o)
        supply = int(strip_0x(r), 16)
        s = ''
        if not config.true('_RAW'):
            s = 'Supply: '
        s += str(supply)
        print(s)


if __name__ == '__main__':
    main()
