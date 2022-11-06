#!python3

"""Token transfer script

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import os
import io
import json
import argparse
import logging

# external imports
from hexathon import (
        add_0x,
        strip_0x,
        )
import chainlib.eth.cli
from chainlib.eth.cli.log import process_log
from chainlib.eth.settings import process_settings
from chainlib.settings import ChainSettings
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
from eth_erc20 import ERC20

logg = logging.getLogger()


def process_config_local(config, arg, args, flags):
    config.add(config.get('_POSARG'), '_VALUE', False)
    return config


arg_flags = ArgFlag()
arg = Arg(arg_flags)
flags = arg_flags.STD_WRITE | arg_flags.EXEC | arg_flags.WALLET

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


def balance(conn, generator, token_address, address, id_generator=None):
    o = generator.balance(token_address, address, id_generator=id_generator)
    r = conn.do(o)
    token_balance = generator.parse_balance(r)
    return token_balance


def main():
    token_address = settings.get('EXEC')
    signer_address = settings.get('SENDER_ADDRESS')
    recipient = settings.get('RECIPIENT')
    value = settings.get('VALUE')
    conn = settings.get('CONN')
    g = ERC20(
            settings.get('CHAIN_SPEC'),
            signer=settings.get('SIGNER'),
            gas_oracle=settings.get('GAS_ORACLE'),
            nonce_oracle=settings.get('NONCE_ORACLE'),
            )
    if logg.isEnabledFor(logging.DEBUG):
        sender_balance = balance(conn, g, token_address, signer_address, id_generator=settings.get('RPC_ID_GENERATOR'))
        recipient_balance = balance(conn, g, token_address, recipient, id_generator=settings.get('RPC_ID_GENERATOR'))
        logg.debug('sender {} balance before: {}'.format(signer_address, sender_balance))
        logg.debug('recipient {} balance before: {}'.format(recipient, recipient_balance))

    (tx_hash_hex, o) = g.transfer(token_address, signer_address, recipient, value, id_generator=settings.get('RPC_ID_GENERATOR'))

    if settings.get('RPC_SEND'):
        conn.do(o)
        if settings.get('WAIT'):
            r = conn.wait(tx_hash_hex)
            if logg.isEnabledFor(logging.DEBUG):
                sender_balance = balance(conn, g, token_address, signer_address, id_generator=settings.get('RPC_ID_GENERATOR'))
                recipient_balance = balance(conn, g, token_address, recipient, id_generator=settings.get('RPC_ID_GENERATOR'))
                logg.debug('sender {} balance after: {}'.format(signer_address, sender_balance))
                logg.debug('recipient {} balance after: {}'.format(recipient, recipient_balance))
            if r['status'] == 0:
                logg.critical('VM revert. Wish I could tell you more')
                sys.exit(1)
        print(tx_hash_hex)

    else:
        print(o['params'][0])


if __name__ == '__main__':
    main()
