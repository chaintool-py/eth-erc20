all:
	solc --bin GiftableToken.sol | awk 'NR>3' > GiftableToken.bin
	truncate -s -1 GiftableToken.bin
	solc --abi GiftableToken.sol | awk 'NR>3' > GiftableToken.abi.json

install: all
	cp -v *{json,bin} ../python/giftable_erc20_token/data/

