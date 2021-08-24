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
from chainlib.eth.connection import EthHTTPConnection
from chainlib.chain import ChainSpec
from chainlib.eth.runnable.util import decode_for_puny_humans
from chainlib.eth.address import to_checksum_address
import chainlib.eth.cli

# local imports
from eth_erc20 import ERC20

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

arg_flags = chainlib.eth.cli.argflag_std_write | chainlib.eth.cli.Flag.EXEC | chainlib.eth.cli.Flag.WALLET 
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_positional('amount', type=int, help='Token amount to send')
args = argparser.parse_args()
extra_args = {
    'amount': None,
        }
config = chainlib.eth.cli.Config.from_args(args, arg_flags, extra_args=extra_args, default_fee_limit=100000)

block_all = args.ww
block_last = args.w or block_all

wallet = chainlib.eth.cli.Wallet()
wallet.from_config(config)

rpc = chainlib.eth.cli.Rpc(wallet=wallet)
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))

value = config.get('_AMOUNT')

send = config.true('_RPC_SEND')


def balance(generator, token_address, address, id_generator=None):
    o = generator.balance(token_address, address, id_generator=id_generator)
    r = conn.do(o)
    token_balance = generator.parse_balance(r)
    return token_balance


def main():
    signer = rpc.get_signer()
    signer_address = rpc.get_sender_address()

    gas_oracle = rpc.get_gas_oracle()
    nonce_oracle = rpc.get_nonce_oracle()

    g = ERC20(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)

    recipient = to_checksum_address(config.get('_RECIPIENT'))
    if not config.true('_UNSAFE') and recipient != add_0x(config.get('_RECIPIENT')):
        raise ValueError('invalid checksum address for recipient')

    token_address = to_checksum_address(config.get('_EXEC_ADDRESS'))
    if not config.true('_UNSAFE') and token_address != add_0x(config.get('_EXEC_ADDRESS')):
        raise ValueError('invalid checksum address for contract')

    if logg.isEnabledFor(logging.DEBUG):
        sender_balance = balance(g, token_address, signer_address, id_generator=rpc.id_generator)
        recipient_balance = balance(g, token_address, recipient, id_generator=rpc.id_generator)
        logg.debug('sender {} balance before: {}'.format(signer_address, sender_balance))
        logg.debug('recipient {} balance before: {}'.format(recipient, recipient_balance))

    (tx_hash_hex, o) = g.transfer(token_address, signer_address, recipient, value, id_generator=rpc.id_generator)

    if send:
        conn.do(o)
        if block_last:
            r = conn.wait(tx_hash_hex)
            if logg.isEnabledFor(logging.DEBUG):
                sender_balance = balance(g, token_address, signer_address, id_generator=rpc.id_generator)
                recipient_balance = balance(g, token_address, recipient, id_generator=rpc.id_generator)
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
