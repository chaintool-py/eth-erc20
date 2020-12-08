"""Deploys giftable token, and optionally gifts a set amount to all accounts in wallet

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

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-n', '--name', dest='n', default='Giftable Token', type=str, help='Token name')
argparser.add_argument('-s', '--symbol', dest='s', default='GFT', type=str, help='Token symbol')
argparser.add_argument('-d', '--decimals', dest='d', default=18, type=int, help='Token decimals')
argparser.add_argument('-o', '--owner', dest='o', type=str, help='Reserve owner account')
argparser.add_argument('-a', '--account', dest='a', action='append', type=str, help='Account to fund')
argparser.add_argument('-m', '--minter', dest='m', action='append', type=str, help='Minter to add')
argparser.add_argument('--contracts-dir', dest='contracts_dir', type=str, default='.', help='Directory containing bytecode and abi')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('amount', type=int, help='Initial token supply (will be owned by contract creator)')
args = argparser.parse_args()

if args.v:
    logg.setLevel(logging.DEBUG)

def main():
    w3 = web3.Web3(web3.Web3.HTTPProvider(args.p))

    f = open(os.path.join(args.contracts_dir, 'GiftableToken.abi.json'), 'r')
    abi = json.load(f)
    f.close()

    f = open(os.path.join(args.contracts_dir, 'GiftableToken.bin'), 'r')
    bytecode = f.read()
    f.close()

    w3.eth.defaultAccount = w3.eth.accounts[0]
    if args.o != None:
        w3.eth.defaultAccount = args.o

    c = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = c.constructor(args.n, args.s, args.d).transact()
    rcpt = w3.eth.getTransactionReceipt(tx_hash)
    address = rcpt.contractAddress
    c = w3.eth.contract(abi=abi, address=address)

    logg.debug('construct tx {} address {}'.format(tx_hash.hex(), address))

    balance = c.functions.balanceOf(w3.eth.defaultAccount).call()
    logg.info('balance {}: {} {}'.format(w3.eth.defaultAccount, balance, tx_hash))


    if args.a != None:
        for a in args.a:
            if a == w3.eth.defaultAccount:
                continue
            tx_hash_mint = c.functions.mint(args.amount).transact()
            tx_hash_transfer = c.functions.transfer(a, args.amount).transact()
            rcpt = w3.eth.getTransactionReceipt(tx_hash)
            balance = c.functions.balanceOf(a).call()
            logg.info('balance {}: {}'.format(a, balance))

    if args.m != None:
        for a in args.m:
            if a == w3.eth.defaultAccount:
                continue
            tx_hash_minter = c.functions.addMinter(a).transact()
            logg.info('minter {}'.format(a))

    print(address)


if __name__ == '__main__':
    main()
