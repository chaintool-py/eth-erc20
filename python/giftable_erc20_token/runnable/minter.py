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
from chainlib.eth.connection import EthHTTPConnection
from chainlib.chain import ChainSpec
from chainlib.eth.tx import receipt
from chainlib.eth.address import to_checksum_address
from hexathon import (
        strip_0x,
        add_0x,
        )

# local imports
from giftable_erc20_token import GiftableToken

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

arg_flags = chainlib.eth.cli.argflag_std_write | chainlib.eth.cli.Flag.EXEC | chainlib.eth.cli.Flag.WALLET
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_argument('--rm', action='store_true', help='Remove entry')
argparser.add_positional('minter_address', type=str, help='Address to add or remove as minter')
args = argparser.parse_args()
extra_args = {
    'rm': None,
    'minter_address': None,
    }
config = chainlib.eth.cli.Config.from_args(args, arg_flags, extra_args=extra_args, default_fee_limit=GiftableToken.gas())

wallet = chainlib.eth.cli.Wallet()
wallet.from_config(config)

rpc = chainlib.eth.cli.Rpc(wallet=wallet)
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))


def main():
    signer = rpc.get_signer()
    signer_address = rpc.get_sender_address()

    gas_oracle = rpc.get_gas_oracle()
    nonce_oracle = rpc.get_nonce_oracle()

    recipient_address_input = config.get('_RECIPIENT')
    if recipient_address_input == None:
        recipient_address_input = signer_address

    recipient_address = add_0x(to_checksum_address(recipient_address_input))
    if not config.true('_UNSAFE') and recipient_address != add_0x(recipient_address_input):
        raise ValueError('invalid checksum address for recipient')

    token_address = add_0x(to_checksum_address(config.get('_EXEC_ADDRESS')))
    if not config.true('_UNSAFE') and token_address != add_0x(config.get('_EXEC_ADDRESS')):
        raise ValueError('invalid checksum address for contract')

    minter_address = config.get('_MINTER_ADDRESS')
    c = GiftableToken(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)
    if config.get('_RM'):
        (tx_hash_hex, o) = c.remove_minter(token_address, signer_address, minter_address)
    else:
        (tx_hash_hex, o) = c.add_minter(token_address, signer_address, minter_address)

    if config.get('_RPC_SEND'):
        conn.do(o)
        if config.get('_WAIT'):
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
