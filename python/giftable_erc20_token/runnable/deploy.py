#!python3

"""Deploys giftable token

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
import time
from enum import Enum

# external imports
import chainlib.eth.cli
from chainlib.eth.tx import receipt
from chainlib.settings import ChainSettings
from chainlib.eth.cli.log import process_log
from chainlib.eth.settings import process_settings
from chainlib.eth.cli.arg import (
        Arg,
        ArgFlag,
        process_args,
        )
from chainlib.eth.cli.config import (
        Config,
        process_config,
        )


# local imports
from giftable_erc20_token import GiftableToken

logg = logging.getLogger()


def process_config_local(config, arg, args, flags):
    config.add(args.token_name, '_TOKEN_NAME', False)
    config.add(args.token_symbol, '_TOKEN_SYMBOL', False)
    config.add(args.token_decimals, '_TOKEN_DECIMALS', False)
    return config


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.WALLET

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('--name', dest='token_name', required=True, type=str, help='Token name')
argparser.add_argument('--symbol', dest='token_symbol', required=True, type=str, help='Token symbol')
argparser.add_argument('--decimals', dest='token_decimals', default=18, type=int, help='Token decimals')
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
    signer_address = settings.get('SENDER_ADDRESS')
    conn = settings.get('CONN')

    c = GiftableToken(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('GAS_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )

    (tx_hash_hex, o) = c.constructor(
            signer_address,
            config.get('_TOKEN_NAME'),
            config.get('_TOKEN_SYMBOL'),
            config.get('_TOKEN_DECIMALS'),
            )
    if settings.get('RPC_SEND'):
        conn.do(o)
        if settings.get('WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
                sys.exit(1)
            # TODO: pass through translator for keys (evm tester uses underscore instead of camelcase)
            address = r['contractAddress']

            print(address)
        else:
            print(tx_hash_hex)
    else:
        print(o)


if __name__ == '__main__':
    main()
