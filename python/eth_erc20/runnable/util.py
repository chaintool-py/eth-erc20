# external imports
from chainlib.eth.tx import (
        unpack,
        Tx,
        )
from hexathon import (
        strip_0x,
        add_0x,
        )
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.runnable.util import decode_out

# local imports
from eth_erc20.erc20 import ERC20

sender_address = ZERO_ADDRESS


class Decoder:

    def __init__(self, chain_spec):
        self.chain_spec = chain_spec


    def decode_transfer(self, tx, writer, rpc=None):
        r = ERC20.parse_transfer_request(tx['data'])    
        token_value = r[1]
        token_str = tx['to']
        token_recipient = r[0]
        if rpc != None:
            c = ERC20(self.chain_spec)
            o = c.symbol(tx['to'], sender_address=sender_address)
            r = rpc.do(o)
            symbol = c.parse_symbol(r)

            o = c.name(tx['to'], sender_address=sender_address)
            r = rpc.do(o)
            name = c.parse_symbol(r)

            o = c.decimals(tx['to'], sender_address=sender_address)
            r = rpc.do(o)
            decimals = c.parse_decimals(r)

            token_str = '{} ({})'.format(name, symbol)
            token_value = token_value / (10 ** decimals)
            token_value_str = '{:.6f} ({} decimals)'.format(token_value, decimals)

        writer.write("""to: {}
token: {}
value: {}
""".format(
    token_recipient,
    token_str,
    token_value_str,
    )
)

        #writer.write('{}\n'.format(r))k


    def decode_for_puny_humans(self, tx_raw, chain_spec, writer, method, rpc=None):
        tx_raw = strip_0x(tx_raw)
        tx_raw_bytes = bytes.fromhex(tx_raw)
        tx_src = unpack(tx_raw_bytes, chain_spec)
        tx = Tx.src_normalize(tx_src)
      
        self.decode_transfer(tx, writer, rpc=rpc)

        decode_out(tx_src, writer, skip_keys=['to'])
        
        writer.write('src: {}\n'.format(add_0x(tx_raw)))
