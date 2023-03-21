# import logging
import unittest

# local imports
from giftable_erc20_token.unittest import TestGiftableToken
from eth_erc20.unittest import TestInterface


class TestBasic(TestGiftableToken, TestInterface):
    pass


if __name__ == '__main__':
    unittest.main()
