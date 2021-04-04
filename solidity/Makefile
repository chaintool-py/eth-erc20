SOLC = /usr/bin/solc

all:
	$(SOLC) --bin GiftableToken.sol --evm-version byzantium | awk 'NR>3' > GiftableToken.bin
	truncate -s -1 GiftableToken.bin
	$(SOLC) --abi GiftableToken.sol --evm-version byzantium | awk 'NR>3' > GiftableToken.json

install: all
	cp -v *{json,bin} ../python/giftable_erc20_token/data/

