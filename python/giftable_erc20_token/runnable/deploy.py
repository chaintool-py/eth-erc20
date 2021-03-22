"""Deploys giftable token, and optionally gifts a set amount to all accounts in wallet

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
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore.dict import DictKeystore
from chainlib.chain import ChainSpec
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import RPCGasOracle
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import receipt

# local imports
from giftable_erc20_token import GiftableToken

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')


argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-e', action='store_true', help='Treat all transactions as essential')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('--name', default='Giftable Token', type=str, help='Token name')
argparser.add_argument('--symbol', default='GFT', type=str, help='Token symbol')
argparser.add_argument('--decimals', default=18, type=int, help='Token decimals')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('amount', type=int, help='Initial token supply (will be owned by contract creator)')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

block_last = args.w
block_all = args.ww

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
chain_id = chain_spec.network_id()

rpc = EthHTTPConnection(args.p)
nonce_oracle = RPCNonceOracle(signer_address, rpc)
gas_oracle = RPCGasOracle(rpc, code_callback=GiftableToken.gas)

token_name = args.name
token_symbol = args.symbol
token_decimals = args.decimals


def main():
    c = GiftableToken(signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle, chain_id=chain_id)
    (tx_hash_hex, o) = c.constructor(signer_address, token_name, token_symbol, token_decimals)
    rpc.do(o)
    o = receipt(tx_hash_hex)
    r = rpc.do(o)
    if r['status'] == 0:
        sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
        sys.exit(1)
    # TODO: pass through translator for keys (evm tester uses underscore instead of camelcase)
    address = r['contractAddress']

    if block_last:
        rpc.wait(tx_hash_hex)

    print(address)

    sys.exit(0)


if __name__ == '__main__':
    main()
