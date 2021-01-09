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

block_mode = 0
if args.ww:
    logg.debug('set block after each tx')
    block_mode = 2
elif args.w:
    logg.debug('set block until last tx')
    block_mode = 1

w3 = web3.Web3(web3.Web3.HTTPProvider(args.p))

private_key = None
signer_address = None
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    f = open(args.y, 'r')
    encrypted_key = f.read()
    f.close()
    private_key = w3.eth.account.decrypt(encrypted_key, '')
    private_key_object = keys.PrivateKey(private_key)
    signer_address = private_key_object.public_key.to_checksum_address()
    logg.debug('now have key for signer address {}'.format(signer_address))

network_pair = args.i.split(':')
network_id = int(network_pair[1])


def waitFor(tx_hash):
    i = 1
    while True:
        try:
            return w3.eth.getTransactionReceipt(tx_hash)
        except web3.exceptions.TransactionNotFound:
            logg.debug('poll #{} for {}'.format(i, tx_hash.hex()))   
            i += 1
            time.sleep(1)


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

    tx = c.functions.mint(args.amount).buildTransaction({
        'chainId': network_id,
        'gas': 60000,
        'gasPrice': gas_price,
        'nonce': nonce,
        })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash_mint = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    last_tx = tx_hash_mint
    logg.info('mint to {} tx {}'.format(signer_address, tx_hash_mint.hex()))

    if block_mode == 2:
        rcpt = waitFor(tx_hash_mint)
        if rcpt['status'] == 0:
            logg.critical('mint failed: {}'.format(tx_hash_mint.hex()))
            sys.exit(1)
        else:
            logg.info('mint succeeded. gas used: {}'.format(rcpt['gasUsed']))

    nonce += 1

    tx = c.functions.transfer(recipient, args.amount).buildTransaction({
        'chainId': network_id,
        'gas': 60000,
        'gasPrice': gas_price,
        'nonce': nonce,
        })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash_mint = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    last_tx = tx_hash_mint
    logg.info('transfer to {} tx {}'.format(recipient, tx_hash_mint.hex()))

    if block_mode > 0:
        rcpt = waitFor(tx_hash_mint)
        if rcpt['status'] == 0:
            logg.error('trasnfer failed: {}'.format(tx_hash_mint.hex()))
            sys.exit(1)
        else:
            logg.info('transfer succeeded. gas used: {}'.format(rcpt['gasUsed']))

    print(last_tx.hex())
    sys.exit(0)


if __name__ == '__main__':
    main()
