FROM ethereum/solc:0.6.12

FROM python:3.8.6-alpine

COPY --from=0 /usr/bin/solc /usr/bin/solc

RUN apk update &&\
	apk add gcc bash musl-dev

WORKDIR /usr/src

# Try to keep everything above here re-usable!

COPY ./solidity/ /usr/src/giftable_erc20_token/solidity/
COPY ./python/ /usr/src/giftable_erc20_token/python/

RUN cd giftable_erc20_token/solidity && \
	solc GiftableToken.sol --abi | awk 'NR>3' > GiftableToken.abi.json

RUN cd giftable_erc20_token/solidity && \
	solc GiftableToken.sol --bin | awk 'NR>3' > GiftableToken.bin && \
	truncate -s "$((`stat -t -c "%s" GiftableToken.bin`-1))" GiftableToken.bin

RUN cd giftable_erc20_token/python && \
	pip install --extra-index-url https://pip.grassrootseconomics.net:8433 .

# To deploy:
# giftable-token-deploy --contracts-dir giftable_erc20_token/solidity/ <amount>
