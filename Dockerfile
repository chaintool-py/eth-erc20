FROM ethereum/solc:0.6.12

FROM python:3.8.6

COPY --from=0 /usr/bin/solc /usr/bin/solc

#RUN apk update &&\
#	apk add gcc bash cargo
RUN apt update && \
    apt install -y gcc bash cargo

WORKDIR /usr/src

# Try to keep everything above here re-usable!

COPY . .

RUN chmod +x ./python/run_tests.sh

RUN cd ./solidity && \
	solc GiftableToken.sol --abi | awk 'NR>3' > GiftableToken.abi.json

RUN cd ./solidity && \
	solc GiftableToken.sol --bin | awk 'NR>3' > GiftableToken.bin && \
	truncate -s "$((`stat -t -c "%s" GiftableToken.bin`-1))" GiftableToken.bin

RUN cd ./python && \
	pip install --extra-index-url https://gitlab.com/api/v4/projects/27624814/packages/pypi/simple \
  --extra-index-url https://pip.grassrootseconomics.net:8433 \
  -r requirements.txt -r test_requirements.txt

#RUN pip install slither-analyzer

# To deploy:
# giftable-token-deploy --contracts-dir giftable_erc20_token/solidity/ <amount>
