from setuptools import setup

setup(
        package_data={
            '': [
                'data/GiftableToken.abi.json',
                'data/GiftableToken.bin',
                ],
            },
        include_package_data=True,
        )
