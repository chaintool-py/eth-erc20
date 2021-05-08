# standard imports
import os

# external imports
import pytest
from crypto_dev_signer.keystore.dict import DictKeystore
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer


@pytest.fixture(scope='session')
def keystore():
    ks = DictKeystore()
    
    pk = os.urandom(32)
    ks.import_raw_key(pk)
    return ks


@pytest.fixture(scope='session')
def signer(
    keystore,
        ):

    s = EIP155Signer(keystore)
    return s
