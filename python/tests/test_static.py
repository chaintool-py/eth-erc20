# standard imports
import os
import unittest
import json
import logging
import datetime

# external imports
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.tx import receipt
from chainlib.eth.block import (
        block_latest,
        block_by_number,
    )

# local imports
from static_token import StaticToken
from static_token.unittest import TestStaticToken

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

testdir = os.path.dirname(__file__)


class TestExpire(TestStaticToken):

    def setUp(self):
        super(TestExpire, self).setUp()


    def test_static_interface(self):
        pass


if __name__ == '__main__':
    unittest.main()
