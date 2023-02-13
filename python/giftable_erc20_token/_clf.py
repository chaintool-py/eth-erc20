# local imports
from .factory import GiftableToken


def code(v):
    version = None
    if v != None:
        version = v[0]
    return GiftableToken.bytecode(version=version)


def init(v):
    if v == None or len(v) < 3:
        raise ValueError('minimum 3 arguments required')
    version = None
    if len(v) == 4:
        version = v[4]
    return GiftableToken.cargs(v[0], v[1], v[2], version=version)


default = code
