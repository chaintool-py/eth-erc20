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
from chainlib.eth.cli.log import process_log
from chainlib.eth.settings import process_settings
from chainlib.settings import ChainSettings

# local imports
from eth_erc20 import ERC20


def process_config_local(config, arg, args, flags):
    recipient = None
    address = config.get('_POSARG')
    if address:
        recipient = add_0x(address)
    else:
        recipient = stdin_arg()
    config.add(recipient, '_RECIPIENT', False)
    return config


logg = logging.getLogger()

arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_READ | arg_flags.EXEC | arg_flags.SENDER

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('address', type=str, help='Ethereum address of recipient')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags, positional_name='address')
config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    token_address = settings.get('EXEC')
    conn = settings.get('CONN')
    sender_address = settings.get('SENDER_ADDRESS')
    g = ERC20(
            chain_spec=settings.get('CHAIN_SPEC'),
            gas_oracle=settings.get('GAS_ORACLE'),
            )

    # determine decimals
    decimals_o = g.decimals(token_address, sender_address=sender_address)
    r = conn.do(decimals_o)
    decimals = int(strip_0x(r), 16)
    logg.info('decimals {}'.format(decimals))

    name_o = g.name(token_address, sender_address=sender_address)
    r = conn.do(name_o)
    token_name = g.parse_name(r)
    logg.info('name {}'.format(token_name))

    symbol_o = g.symbol(token_address, sender_address=sender_address)
    r = conn.do(symbol_o)
    token_symbol = g.parse_symbol(r)
    logg.info('symbol {}'.format(token_symbol))

    # get balance
    balance_o = g.balance(token_address, settings.get('RECIPIENT'), sender_address=sender_address)
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
