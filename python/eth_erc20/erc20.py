# standard imports
import logging

# external imports
import sha3
from hexathon import (
        add_0x,
        strip_0x,
        )
from crypto_dev_signer.eth.transaction import EIP155Transaction

# external imports
from chainlib.hash import (
        keccak256_hex_to_hex,
        keccak256_string_to_hex,
        )
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.tx import (
        TxFactory,
        TxFormat,
        )
from chainlib.eth.contract import (
        ABIContractEncoder,
        ABIContractDecoder,
        ABIContractType,
        abi_decode_single,
        )
from chainlib.jsonrpc import jsonrpc_template
from chainlib.eth.error import RequestMismatchException

logg = logging.getLogger()


class ERC20(TxFactory):
    

    def balance_of(self, contract_address, address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('balanceOf')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    def balance(self, contract_address, address, sender_address=ZERO_ADDRESS):
        return self.balance_of(contract_address, address, sender_address=ZERO_ADDRESS)


    def symbol(self, contract_address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('symbol')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    def name(self, contract_address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('name')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o

    
    def decimals(self, contract_address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('decimals')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    def total_supply(self, contract_address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('totalSupply')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        return o


    def transfer(self, contract_address, sender_address, recipient_address, value, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('transfer')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        enc.address(recipient_address)
        enc.uint256(value)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def transfer_from(self, contract_address, sender_address, holder_address, recipient_address, value, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('transferFrom')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        enc.address(holder_address)
        enc.address(recipient_address)
        enc.uint256(value)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def approve(self, contract_address, sender_address, spender_address, value, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('approve')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        enc.address(spender_address)
        enc.uint256(value)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    @classmethod
    def parse_symbol(self, v):
        return abi_decode_single(ABIContractType.STRING, v)


    @classmethod
    def parse_name(self, v):
        return abi_decode_single(ABIContractType.STRING, v)


    @classmethod
    def parse_decimals(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)


    @classmethod
    def parse_balance(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)


    @classmethod
    def parse_transfer_request(self, v):
        v = strip_0x(v)
        cursor = 0
        enc = ABIContractEncoder()
        enc.method('transfer')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        r = enc.get()
        l = len(r)
        m = v[:l]
        if m != r:
            logg.error('method mismatch, expected {}, got {}'.format(r, m))
            raise RequestMismatchException(v)
        cursor += l

        dec = ABIContractDecoder()
        dec.typ(ABIContractType.ADDRESS)
        dec.typ(ABIContractType.UINT256)
        dec.val(v[cursor:cursor+64])
        cursor += 64
        dec.val(v[cursor:cursor+64])
        r = dec.decode()
        return r 


    @classmethod
    def parse_transfer_from_request(self, v):
        v = strip_0x(v)
        cursor = 0
        enc = ABIContractEncoder()
        enc.method('transferFrom')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        r = enc.get()
        l = len(r)
        m = v[:l]
        if m != r:
            logg.error('method mismatch, expected {}, got {}'.format(r, m))
            raise RequestMismatchException(v)
        cursor += l

        dec = ABIContractDecoder()
        dec.typ(ABIContractType.ADDRESS)
        dec.typ(ABIContractType.ADDRESS)
        dec.typ(ABIContractType.UINT256)
        dec.val(v[cursor:cursor+64])
        cursor += 64
        dec.val(v[cursor:cursor+64])
        cursor += 64
        dec.val(v[cursor:cursor+64])
        r = dec.decode()
        return r 


    @classmethod
    def parse_approve_request(self, v):
        v = strip_0x(v)
        cursor = 0
        enc = ABIContractEncoder()
        enc.method('approve')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        r = enc.get()
        l = len(r)
        m = v[:l]
        if m != r:
            logg.error('method mismatch, expected {}, got {}'.format(r, m))
            raise RequestMismatchException(v)
        cursor += l

        dec = ABIContractDecoder()
        dec.typ(ABIContractType.ADDRESS)
        dec.typ(ABIContractType.UINT256)
        dec.val(v[cursor:cursor+64])
        cursor += 64
        dec.val(v[cursor:cursor+64])
        r = dec.decode()
        return r 
