SOLC = /usr/bin/solc

all:
	$(SOLC) --bin GiftableToken.sol --evm-version byzantium | awk 'NR>3' > GiftableToken.bin
	truncate -s -1 GiftableToken.bin
	$(SOLC) --abi GiftableToken.sol --evm-version byzantium | awk 'NR>3' > GiftableToken.json
	$(SOLC) --bin StaticToken.sol --evm-version byzantium | awk 'NR>3' > StaticToken.bin
	truncate -s -1 StaticToken.bin
	$(SOLC) --abi StaticToken.sol --evm-version byzantium | awk 'NR>3' > StaticToken.json

install: all
	cp -v Giftable*{json,bin} ../python/giftable_erc20_token/data/
	cp -v Static*{json,bin} ../python/static_token/data/

