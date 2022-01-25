# ETH-ERC20 Solidity Contract


### solidity 

To generate bytecode and tests install solc 8.x.x and run the solc bits below or execute the following: 

```
docker run -v `pwd`:/src registry.gitlab.com/grassrootseconomics/cic-base-images/ci-solc-python:latest solc --evm-version=byzantium solidity/GiftableToken.sol --abi
```

```
docker run -v `pwd`:/src registry.gitlab.com/grassrootseconomics/cic-base-images/ci-solc-python:latest solc GiftableToken.sol --bin | awk 'NR>3' > GiftableToken.bin 
```

### python unit tests

```
pip install --extra-index-url https://gitlab.com/api/v4/projects/27624814/packages/pypi/simple \
--extra-index-url https://pip.grassrootseconomics.net \
-r requirements.txt -r test_requirements.txt

bash python/run_tests.sh

```
