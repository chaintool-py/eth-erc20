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

# third-party imports
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore.dict import DictKeystore
from chainlib.eth.tx import receipt
from chainlib.chain import ChainSpec
from chainlib.eth.nonce import (
        RPCNonceOracle,
        OverrideNonceOracle,
        )
from chainlib.eth.gas import (
        RPCGasOracle,
        OverrideGasOracle,
        )
from chainlib.eth.connection import EthHTTPConnection

# local imports
from giftable_erc20_token import GiftableToken

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-e', action='store_true', help='Treat all transactions as essential')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-a', '--token-address', required='True', dest='a', type=str, help='Giftable token address')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('-d', action='store_true', help='Dump RPC calls to terminal and do not send')
argparser.add_argument('--gas-price', type=int, dest='gas_price', help='Override gas price')
argparser.add_argument('--nonce', type=int, help='Override transaction nonce')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('--recipient', type=str, help='Recipient account address. If not set, tokens will be gifted to the keystore account')
argparser.add_argument('value', type=int, help='Value of tokens to mint and gift')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

block_all = args.ww
block_last = args.w or block_all

passphrase_env = 'ETH_PASSPHRASE'
if args.env_prefix != None:
    passphrase_env = args.env_prefix + '_' + passphrase_env
passphrase = os.environ.get(passphrase_env)
if passphrase == None:
    logg.warning('no passphrase given')
    passphrase=''

signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_keystore_file(args.y, password=passphrase)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)

chain_spec = ChainSpec.from_chain_str(args.i)

rpc = EthHTTPConnection(args.p)
nonce_oracle = None
if args.nonce != None:
    nonce_oracle = OverrideNonceOracle(signer_address, args.nonce)
else:
    nonce_oracle = RPCNonceOracle(signer_address, rpc)

gas_oracle = None
if args.gas_price !=None:
    gas_oracle = OverrideGasOracle(price=args.gas_price, conn=rpc, code_callback=GiftableToken.gas)
else:
    gas_oracle = RPCGasOracle(rpc, code_callback=GiftableToken.gas)

dummy = args.d

token_address = args.a
recipient_address = args.recipient
if recipient_address == None:
    recipient_address = signer_address
token_value = args.value


def main():
    c = GiftableToken(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)
    (tx_hash_hex, o) = c.mint_to(token_address, signer_address, recipient_address, token_value)
    if dummy:
        print(tx_hash_hex)
        print(o)
    else:
        rpc.do(o)
        if block_last:
            r = rpc.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert. Wish I had more to tell you')
                sys.exit(1)

        logg.info('mint to {} tx {}'.format(recipient_address, tx_hash_hex))

        print(tx_hash_hex)


if __name__ == '__main__':
    main()
