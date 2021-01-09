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
from eth_keys import keys
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.eth.transaction import EIP155Transaction

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


class DictKeystore:

    def __init__(self):
        self.keys = {}
        self.nonces = {}
        

    def get(self, address, password=None):
        return self.keys[signer_address]


    def import_file(self, keystore_file):
        f = open(keystore_file, 'r')
        encrypted_key = f.read()
        f.close()
        private_key = w3.eth.account.decrypt(encrypted_key, '')
        private_key_object = keys.PrivateKey(private_key)
        signer_address = private_key_object.public_key.to_checksum_address()
        self.keys[signer_address] = private_key
        return signer_address


class TransactionRevertError(Exception):
    pass


class EthCliHelper:

    def __init__(self, w3, signer, chain_id, block=False, gas_price_helper=None):
        self.w3 = w3
        self.nonce = {}
        self.signer = signer
        self.block = bool(block)
        self.chain_id = chain_id
        self.tx_hashes = []
        self.gas_helper = self.default_gas_helper
        if gas_price_helper == None:
            gas_price_helper = self.default_gas_price_helper
        self.gas_price_helper = gas_price_helper


    def default_gas_price_helper(self):
        return w3.eth.gasPrice


    def default_gas_helper(self, address, tx_data, args):
        return 8000000


    def sign_and_send(self, signer_address, tx_buildable, force_wait=False):
        if self.nonce.get(signer_address) == None:
            self.nonce[signer_address] = w3.eth.getTransactionCount(signer_address, 'pending')
        tx = tx_buildable.buildTransaction({
                'from': signer_address,
                'chainId': self.chain_id,
                'gasPrice': self.gas_price_helper(),
                'nonce': self.nonce[signer_address],
                })

        tx['gas'] = self.gas_helper(signer_address, None, None) 
        logg.debug('from {} nonce {} tx {}'.format(signer_address, self.nonce[signer_address], tx))

        chain_tx = EIP155Transaction(tx, self.nonce[signer_address], self.chain_id)
        signature = self.signer.signTransaction(chain_tx)
        chain_tx_serialized = chain_tx.rlp_serialize()
        tx_hash = self.w3.eth.sendRawTransaction('0x' + chain_tx_serialized.hex())
        self.tx_hashes.append(tx_hash)
        self.nonce[signer_address] += 1
        rcpt = None
        if self.block or force_wait:
            rcpt = self.wait_for(tx_hash)
            logg.info('tx {} gas used: {}'.format(tx_hash.hex(), rcpt['gasUsed']))
        return (tx_hash.hex(), rcpt)


    def wait_for(self, tx_hash=None):
        if tx_hash == None:
            tx_hash = self.tx_hashes[len(self.tx_hashes)-1]
        i = 1
        while True:
            try:
                return w3.eth.getTransactionReceipt(tx_hash)
            except web3.exceptions.TransactionNotFound:
                logg.debug('poll #{} for {}'.format(i, tx_hash.hex()))   
                i += 1
                time.sleep(1)
        if rcpt['status'] == 0:
            raise TransactionRevertError(tx_hash)
        return rcpt



w3 = web3.Web3(web3.Web3.HTTPProvider(args.p))

signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_file(args.y)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)

chain_pair = args.i.split(':')
chain_id = int(chain_pair[1])

helper = EthCliHelper(w3, signer, chain_id, args.ww)

def main():

    f = open(os.path.join(args.abi_dir, 'GiftableToken.json'), 'r')
    abi = json.load(f)
    f.close()

    f = open(os.path.join(args.abi_dir, 'GiftableToken.bin'), 'r')
    bytecode = f.read()
    f.close()

    c = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = c.constructor(args.n, args.s, args.d)

    (tx_hash, rcpt) = helper.sign_and_send(signer_address, tx, force_wait=True)
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
            tx = c.functions.addMinter(a)
            (tx_hash, rcpt) = helper.sign_and_send(signer_address, tx)

    if args.account != None:
        mint_total = len(args.account) * args.amount
        tx = c.functions.mint(mint_total)
        (tx_hash, rcpt) = helper.sign_and_send(signer_address, tx, True)
        for a in args.account:
            tx = c.functions.transfer(a, args.amount)
            (tx_hash, rcpt) = helper.sign_and_send(signer_address, tx)

    if block_last:
        helper.wait_for()

    print(address)

    sys.exit(0)

if __name__ == '__main__':
    main()
