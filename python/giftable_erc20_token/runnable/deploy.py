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

# third-party imports
import web3
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore import DictKeystore
from crypto_dev_signer.helper import TxExecutor

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')


argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-e', action='store_true', help='Treat all transactions as essential')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='Ethereum:1', help='Chain specification string')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('--name', dest='n', default='Giftable Token', type=str, help='Token name')
argparser.add_argument('--symbol', dest='s', default='GFT', type=str, help='Token symbol')
argparser.add_argument('--decimals', dest='d', default=18, type=int, help='Token decimals')
argparser.add_argument('--account', action='append', type=str, help='Account to fund')
argparser.add_argument('--minter', action='append', type=str, help='Minter to add')
argparser.add_argument('--abi-dir', dest='abi_dir', type=str, default=data_dir, help='Directory containing bytecode and abi (default: {})'.format(data_dir))
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('amount', type=int, help='Initial token supply (will be owned by contract creator)')
args = argparser.parse_args()

if args.v:
    logg.setLevel(logging.DEBUG)

block_last = args.w
block_all = args.ww

w3 = web3.Web3(web3.Web3.HTTPProvider(args.p))

signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_keystore_file(args.y)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)

chain_pair = args.i.split(':')
chain_id = int(chain_pair[1])


def gas_helper(signer_address, code, inputs):
    return 8000000

def gas_price_helper():
    return 20000000000

def translateTx(tx):
        return {
            'from': tx['from'],
            'chainId': tx['chainId'],
            'gas': tx['feeUnits'],
            'gasPrice': tx['feePrice'],
            'nonce': tx['nonce'],
            }

nonce = w3.eth.getTransactionCount(signer_address, 'pending')

helper = TxExecutor(
        signer_address,
        signer,
        w3.eth.sendRawTransaction,
        w3.eth.getTransactionReceipt,
        nonce,
        chain_id,
        fee_helper=gas_helper,
        fee_price_helper=gas_price_helper,
        block=args.ww,
        )

def main():

    f = open(os.path.join(args.abi_dir, 'GiftableToken.json'), 'r')
    abi = json.load(f)
    f.close()

    f = open(os.path.join(args.abi_dir, 'GiftableToken.bin'), 'r')
    bytecode = f.read()
    f.close()

    c = w3.eth.contract(abi=abi, bytecode=bytecode)
    (tx_hash, rcpt) = helper.sign_and_send(
            [
                translateTx,
                c.constructor(args.n, args.s, args.d).buildTransaction
                ],
            force_wait=True,
            )
    logg.debug('tx hash {} rcpt {}'.format(tx_hash, rcpt))

    address = rcpt.contractAddress
    logg.debug('token contract mined {} {} {} {}'.format(address, args.n, args.s, args.d))
    c = w3.eth.contract(abi=abi, address=address)

    balance = c.functions.balanceOf(signer_address).call()
    logg.info('balance {}: {} {}'.format(signer_address, balance, tx_hash))

    if args.minter != None:
        for a in args.minter:
            if a == signer_address:
                continue
            (tx_hash, rcpt) = helper.sign_and_send(
                [
                    translateTx,
                    c.functions.addMinter(a).buildTransaction,
                    ],
                    )

    if args.account != None:
        mint_total = len(args.account) * args.amount
        tx = c.functions.mint(mint_total)
        (tx_hash, rcpt) = helper.sign_and_send(
                [
                    translateTx,
                    c.functions.mint(mint_total).buildTransaction,
                    ],
                    force_wait=True,
                )

        for a in args.account:
            (tx_hash, rcpt) = helper.sign_and_send(
                    [
                        translateTx,
                        c.functions.transfer(a, args.amount).buildTransaction,
                        ],
                    )

    if block_last:
        helper.wait_for()

    print(address)

    sys.exit(0)


if __name__ == '__main__':
    main()
