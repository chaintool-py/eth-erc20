SOLC = /usr/bin/solc

all:
	$(SOLC) --bin GiftableToken.sol --evm-version byzantium | awk 'NR>3' > GiftableToken.bin
	$(SOLC) --abi GiftableToken.sol --evm-version byzantium | awk 'NR>3' > GiftableToken.json
	$(SOLC) --metadata GiftableToken.sol --evm-version byzantium | awk 'NR>3' > GiftableToken.metadata.json
	$(SOLC) --bin StaticToken.sol --evm-version byzantium | awk 'NR>3' > StaticToken.bin
	$(SOLC) --abi StaticToken.sol --evm-version byzantium | awk 'NR>3' > StaticToken.json
	$(SOLC) --metadata StaticToken.sol --evm-version byzantium | awk 'NR>3' > StaticToken.metadata.json
	truncate -s -1 StaticToken.bin
	truncate -s -1 GiftableToken.bin

install: all
	cp -v *.json ../python/giftable_erc20_token/data/
	cp -v *.bin ../python/giftable_erc20_token/data/

