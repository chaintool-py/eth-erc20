"""Mints and gifts tokens to a given address
.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# SPDX-License-Identifier: GPL-3.0-or-later

# standard imports
import os
import json
import argparse
import logging

# third-party imports
import web3

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-t', '--token-address', required='True', dest='t', type=str, help='Giftable token address')
argparser.add_argument('-m', '--minter-address', dest='m', type=str, help='Minter account address')
argparser.add_argument('--abi-dir', dest='abi_dir', type=str, default=data_dir, help='Directory containing bytecode and abi (default: {})'.format(data_dir))
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-r', '--recipient-address', dest='r', type=str, help='Recipient account address')
argparser.add_argument('amount', type=int, help='Amount of tokens to mint and gift')
args = argparser.parse_args()

if args.v:
    logg.setLevel(logging.DEBUG)

def main():
    w3 = web3.Web3(web3.Web3.HTTPProvider(args.p))

    f = open(os.path.join(args.abi_dir, 'GiftableToken.json'), 'r')
    abi = json.load(f)
    f.close()

    c = w3.eth.contract(abi=abi, address=args.t)
    if args.m != None:
        w3.eth.defaultAccount = web3.Web3.toChecksumAddress(args.m)
    else:
        w3.eth.defaultAccount = w3.eth.accounts[0]

    recipient = w3.eth.defaultAccount
    if args.r != None:
        recipient = web3.Web3.toChecksumAddress(args.r)

    c.functions.mint(args.amount).transact()
    tx = c.functions.transfer(recipient, args.amount).transact()

    print(tx.hex())

