# standard imports
import logging

# external imports
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.contract import (
    ABIContractEncoder,
    ABIContractDecoder,
    ABIContractType,
    abi_decode_single,
)
from chainlib.eth.jsonrpc import to_blockheight_param
from chainlib.eth.error import RequestMismatchException
from chainlib.eth.tx import (
    TxFactory,
    TxFormat,
)
from chainlib.jsonrpc import JSONRPCRequest
from chainlib.block import BlockSpec
from hexathon import (
    add_0x,
    strip_0x,
)

logg = logging.getLogger()


class ERC20(TxFactory):
    

    def balance_of(self, contract_address, address, sender_address=ZERO_ADDRESS, id_generator=None, height=BlockSpec.LATEST):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('balanceOf')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        height = to_blockheight_param(height)
        o['params'].append(height)
        o = j.finalize(o)
        return o


    def balance(self, contract_address, address, sender_address=ZERO_ADDRESS, id_generator=None):
        return self.balance_of(contract_address, address, sender_address=sender_address, id_generator=id_generator)


    def symbol(self, contract_address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('symbol')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def name(self, contract_address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('name')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o

    
    def decimals(self, contract_address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('decimals')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def total_supply(self, contract_address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('totalSupply')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def allowance(self, contract_address, holder_address, spender_address, sender_address=ZERO_ADDRESS, id_generator=None):
        j = JSONRPCRequest(id_generator)
        o = j.template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('allowance')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.ADDRESS)
        enc.address(holder_address)
        enc.address(spender_address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        o['params'].append('latest')
        o = j.finalize(o)
        return o


    def transfer(self, contract_address, sender_address, recipient_address, value, tx_format=TxFormat.JSONRPC, id_generator=None):
        enc = ABIContractEncoder()
        enc.method('transfer')
        enc.typ(ABIContractType.ADDRESS)
        enc.typ(ABIContractType.UINT256)
        enc.address(recipient_address)
        enc.uint256(value)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format, id_generator=id_generator)
        return tx


    def transfer_from(self, contract_address, sender_address, holder_address, recipient_address, value, tx_format=TxFormat.JSONRPC, id_generator=None):
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


    def approve(self, contract_address, sender_address, spender_address, value, tx_format=TxFormat.JSONRPC, id_generator=None):
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
    def parse_balance_of(self, v):
        return self.parse_balance(v)


    @classmethod
    def parse_total_supply(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)


    @classmethod
    def parse_allowance(self, v):
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
