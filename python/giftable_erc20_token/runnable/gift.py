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
import web3
from eth_keys import keys
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore import DictKeystore
from crypto_dev_signer.eth.helper import EthTxExecutor

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-e', action='store_true', help='Treat all transactions as essential')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='Ethereum:1', help='Chain specification string')
argparser.add_argument('-a', '--token-address', required='True', dest='a', type=str, help='Giftable token address')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('--abi-dir', dest='abi_dir', type=str, default=data_dir, help='Directory containing bytecode and abi (default: {})'.format(data_dir))
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('--recipient', type=str, help='Recipient account address. If not set, tokens will be gifted to the keystore account')
argparser.add_argument('amount', type=int, help='Amount of tokens to mint and gift')
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

helper = EthTxExecutor(
        w3,
        signer_address,
        signer,
        chain_id,
        block=args.ww,
        )


def main():

    f = open(os.path.join(args.abi_dir, 'GiftableToken.json'), 'r')
    abi = json.load(f)
    f.close()

    gas_price = w3.eth.gasPrice

    last_tx = None

    nonce = w3.eth.getTransactionCount(signer_address, 'pending')

    c = w3.eth.contract(abi=abi, address=args.a)

    recipient = signer_address
    if args.recipient != None:
        recipient = args.recipient

    (tx_hash, rcpt) = helper.sign_and_send(
            [
                c.functions.mint(args.amount).buildTransaction,
                ],
                force_wait=True,
            )

    logg.info('mint to {} tx {}'.format(signer_address, tx_hash)) #.hex()))

    (tx_hash, rcpt) = helper.sign_and_send(
            [
                c.functions.transfer(recipient, args.amount).buildTransaction,
                ],
            )

    logg.info('transfer to {} tx {}'.format(recipient, tx_hash))


    if block_last:
        helper.wait_for()

    print(tx_hash)

    sys.exit(0)


if __name__ == '__main__':
    main()
