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

# third-party imports
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore.dict import DictKeystore
from hexathon import (
        add_0x,
        strip_0x,
        )
from chainlib.eth.connection import EthHTTPConnection
from chainlib.jsonrpc import jsonrpc_template
from chainlib.eth.nonce import (
        RPCNonceOracle,
        OverrideNonceOracle,
        )
from chainlib.eth.gas import (
        RPCGasOracle,
        OverrideGasOracle,
        )
from chainlib.chain import ChainSpec
from chainlib.eth.runnable.util import decode_for_puny_humans

# local imports
from eth_erc20 import ERC20

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

default_abi_dir = '/usr/local/share/cic/solidity/abi'
argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-a', '--token-address', required='True', dest='a', type=str, help='Token address')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('-u', '--unsafe', dest='u', action='store_true', help='Auto-convert address to checksum adddress')
argparser.add_argument('-s', '--send', dest='s', action='store_true', help='Send to network')
argparser.add_argument('--nonce', type=int, help='Override nonce')
argparser.add_argument('--gas-price', dest='gas_price', type=int, help='Override gas price')
argparser.add_argument('--gas-limit', dest='gas_limit', type=int, help='Override gas limit')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('recipient', type=str, help='Recipient account address')
argparser.add_argument('amount', type=int, help='Amount of tokens to mint and gift')
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
logg.error('pass {}'.format(passphrase_env))
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

conn = EthHTTPConnection(args.p)

nonce_oracle = None
if args.nonce != None:
    nonce_oracle = OverrideNonceOracle(signer_address, args.nonce)
else:
    nonce_oracle = RPCNonceOracle(signer_address, conn)

def _max_gas(code=None):
    return 8000000

gas_oracle = None
if args.gas_price != None or args.gas_limit != None:
    gas_oracle = OverrideGasOracle(price=args.gas_price, limit=args.gas_limit)
else:
    gas_oracle = RPCGasOracle(conn, code_callback=_max_gas)

chain_spec = ChainSpec.from_chain_str(args.i)
chain_id = chain_spec.network_id()

value = args.amount

send = args.s

g = ERC20(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)


def balance(token_address, address):
    o = g.balance(token_address, address)
    r = conn.do(o)
    hx = strip_0x(r)
    return int(hx, 16)


def main():
    recipient = args.recipient
    if not args.u and recipient != add_0x(args.recipient):
        raise ValueError('invalid checksum address')

    if logg.isEnabledFor(logging.DEBUG):
        logg.debug('sender {} balance after: {}'.format(signer_address, balance(args.a, signer_address)))
        logg.debug('recipient {} balance after: {}'.format(recipient, balance(args.a, recipient)))

    (tx_hash_hex, o) = g.transfer(args.a, signer_address, recipient, value)

    if send:
        conn.do(o)
        if block_last:
            r = conn.wait(tx_hash_hex)
            if logg.isEnabledFor(logging.DEBUG):
                logg.debug('sender {} balance after: {}'.format(signer_address, balance(args.a, signer_address)))
                logg.debug('recipient {} balance after: {}'.format(recipient, balance(args.a, recipient)))
            if r['status'] == 0:
                logg.critical('VM revert. Wish I could tell you more')
                sys.exit(1)
        print(tx_hash_hex)

    else:
        if logg.isEnabledFor(logging.INFO):
            io_str = io.StringIO()
            decode_for_puny_humans(o['params'][0], chain_spec, io_str)
            print(io_str.getvalue())
        else:
            print(o['params'][0])


if __name__ == '__main__':
    main()
