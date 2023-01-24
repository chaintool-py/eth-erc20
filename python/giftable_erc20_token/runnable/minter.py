"""Add minter to token contact

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
from chainlib.settings import ChainSettings
from chainlib.eth.cli.log import process_log
from chainlib.eth.settings import process_settings
from chainlib.eth.address import to_checksum_address
from chainlib.eth.cli.arg import (
        Arg,
        ArgFlag,
        process_args,
        )
from chainlib.eth.cli.config import (
        Config,
        process_config,
        )

from hexathon import (
        strip_0x,
        add_0x,
        )

# local imports
from giftable_erc20_token import GiftableToken

logg = logging.getLogger()


def process_config_local(config, arg, args, flags):
    config.add(args.rm, '_RM', False)
    config.add(add_0x(args.minter_address[0]), '_MINTER_ADDRESS', False)
    return config


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.EXEC | arg_flags.WALLET

argparser = chainlib.eth.cli.ArgumentParser()
argparser = process_args(argparser, arg, flags)
argparser.add_argument('--rm', action='store_true', help='Remove entry')
argparser.add_argument('minter_address', type=str, help='Address to add or remove as minter')
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
    signer_address = settings.get('SENDER_ADDRESS')
    conn = settings.get('CONN')

    recipient_address_input = settings.get('RECIPIENT')
    if recipient_address_input == None:
        recipient_address_input = signer_address

    recipient_address = add_0x(to_checksum_address(recipient_address_input))
    if not config.true('_UNSAFE') and recipient_address != add_0x(recipient_address_input):
        raise ValueError('invalid checksum address for recipient')

    minter_address = config.get('_MINTER_ADDRESS')
    c = GiftableToken(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('GAS_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )

    if config.get('_RM'):
        (tx_hash_hex, o) = c.remove_minter(
                settings.get('EXEC'),
                signer_address,
                minter_address,
                )
    else:
        (tx_hash_hex, o) = c.add_minter(
                settings.get('EXEC'),
                signer_address,
                minter_address,
                )

    if settings.get('RPC_SEND'):
        conn.do(o)
        if settings.get('WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert. Wish I had more to tell you')
                sys.exit(1)

        logg.info('add minter {} to {} tx {}'.format(minter_address, token_address, tx_hash_hex))

        print(tx_hash_hex)
    else:
        print(o)


if __name__ == '__main__':
    main()
