"""Mints and gifts tokens to a given address

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

# external imports
import chainlib.eth.cli
from chainlib.eth.tx import receipt
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.address import to_checksum_address
from hexathon import (
        strip_0x,
        add_0x,
        )
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
    config.add(config.get('_POSARG'), '_VALUE', False)
    return config


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.WALLET | arg_flags.EXEC

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('value', type=str, help='Token value to send')
args = argparser.parse_args()

logg = process_log(args, logg)

config = Config()
config = process_config(config, arg, args, flags, positional_name='value')
config = process_config_local(config, arg, args, flags)
logg.debug('config loaded:\n{}'.format(config))

settings = ChainSettings()
settings = process_settings(settings, config)
logg.debug('settings loaded:\n{}'.format(settings))


def main():
    token_address = settings.get('EXEC')
    signer_address = settings.get('SENDER_ADDRESS')
    recipient = settings.get('RECIPIENT')
    value = settings.get('VALUE')
    conn = settings.get('CONN')

    c = GiftableToken(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('GAS_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )

    (tx_hash_hex, o) = c.mint_to(
            token_address,
            signer_address,
            recipient,
            value,
            )
    if settings.get('RPC_SEND'):
        conn.do(o)
        if settings.get('WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert. Wish I had more to tell you')
                sys.exit(1)

        logg.info('mint to {} tx {}'.format(recipient, tx_hash_hex))

        print(tx_hash_hex)
    else:
        print(o)


if __name__ == '__main__':
    main()
