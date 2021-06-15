#!python3

"""Decode raw ERC20 transaction

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
import select

# external imports
from chainlib.eth.tx import unpack
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection

# local imports
from eth_erc20.runnable.util import Decoder

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

def stdin_arg(t=0):
    h = select.select([sys.stdin], [], [], t)
    if len(h[0]) > 0:
        logg.debug('got stdin arg')
        v = h[0][0].read()
        return v.rstrip()
    return None

default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default=default_eth_provider, type=str, help='Web3 provider url (http only)')
argparser.add_argument('-n', '--no-resolve', dest='n', action='store_true', help='Do not resolve token metadata on-chain')
argparser.add_argument('-i', '--chain-id', dest='i', default='evm:ethereum:1', type=str, help='Numeric network id')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('tx', type=str, nargs='?', default=stdin_arg(), help='hex-encoded signed raw transaction')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

argp = args.tx
if argp == None:
    logg.info('no argument provided or delayed stdin, attempting another read')
    argp = stdin_arg(t=None)
    if argp == None:
        argparser.error('need first positional argument or value from stdin')

conn = EthHTTPConnection(args.p)

chain_spec = ChainSpec.from_chain_str(args.i)

no_resolve = args.n

def main():
    tx_raw = argp
    resolve_rpc = None
    if not no_resolve:
        resolve_rpc = conn
    dec = Decoder(chain_spec)
    dec.decode_for_puny_humans(tx_raw, chain_spec, sys.stdout, 'transfer', rpc=resolve_rpc)

if __name__ == '__main__':
    main()
