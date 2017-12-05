# arbitrage-keeper

[![Build Status](https://travis-ci.org/makerdao/arbitrage-keeper.svg?branch=master)](https://travis-ci.org/makerdao/arbitrage-keeper)
[![codecov](https://codecov.io/gh/makerdao/arbitrage-keeper/branch/master/graph/badge.svg)](https://codecov.io/gh/makerdao/arbitrage-keeper)
[![Maintainability](https://api.codeclimate.com/v1/badges/4cc951530d1aa48ef71f/maintainability)](https://codeclimate.com/github/makerdao/arbitrage-keeper/maintainability)

The _DAI Stablecoin System_ incentivizes external agents, called _keepers_,
to automate certain operations around the Ethereum blockchain.

`arbitrage-keeper` performs arbitrage on OasisDEX, `join`, `exit`, `boom` and `bust`.

Keeper constantly looks for profitable enough arbitrage opportunities
and executes them the moment they become available. It can make profit on:
- taking orders on OasisDEX (on SAI/SKR, SAI/W-ETH and SKR/W-ETH pairs),
- calling `join` and `exit` to exchange between W-ETH and SKR,
- calling `boom` and `bust` to exchange between SAI and SKR.

Opportunities discovered by the keeper are sequences of token exchanges
executed using methods listed above. An opportunity can consist of two
or three steps, technically it could be more but practically it will never
be more than three.

Steps can be executed sequentially (each one as a separate Etheruem
transaction, checking if one has been successful before executing the next
one) or in one ago. The latter method requires a `TxManager` contract deployed,
its address has to be passed as the `--tx-manager` argument. Also the `TxManager`
contract has to be owned by the account the keeper operates from.

You can find the source code of the `TxManager` here:
<https://github.com/reverendus/tx-manager>.

The base token is the token all arbitrage opportunities will start with.
Some amount of this token will be exchanged to some other token(s) and then exchanged
back to the base token, aiming to end up with more of it than we started with.
The keeper is aware of gas costs and takes a rough estimate of these costs while
calculating arbitrage profitability.

<https://chat.makerdao.com/channel/keeper>

## Installation

This project uses *Python 3.6.2*.

In order to clone the project and install required third-party packages please execute:
```
git clone https://github.com/makerdao/arbitrage-keeper.git
git submodule update --init --recursive
pip3 install -r requirements.txt
```

### Known macOS issues

In order for the Python requirements to install correctly on _macOS_, please install
`openssl`, `libtool` and `pkg-config` using [Homebrew](https://brew.sh/):
```
brew install openssl libtool pkg-config
```

and set the `LDFLAGS` environment variable before you run `pip3 install -r requirements.txt`:
```
export LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" 
```

## Usage

```
usage: arbitrage-keeper [-h] [--rpc-host RPC_HOST] [--rpc-port RPC_PORT]
                        --eth-from ETH_FROM --tub-address TUB_ADDRESS
                        --tap-address TAP_ADDRESS --oasis-address
                        OASIS_ADDRESS [--tx-manager TX_MANAGER]
                        [--gas-price GAS_PRICE] --base-token BASE_TOKEN
                        --min-profit MIN_PROFIT --max-engagement
                        MAX_ENGAGEMENT [--max-errors MAX_ERRORS] [--debug]
                        [--trace]

optional arguments:
  -h, --help            show this help message and exit
  --rpc-host RPC_HOST   JSON-RPC host (default: `localhost')
  --rpc-port RPC_PORT   JSON-RPC port (default: `8545')
  --eth-from ETH_FROM   Ethereum account from which to send transactions
  --tub-address TUB_ADDRESS
                        Ethereum address of the Tub contract
  --tap-address TAP_ADDRESS
                        Ethereum address of the Tap contract
  --oasis-address OASIS_ADDRESS
                        Ethereum address of the OasisDEX contract
  --tx-manager TX_MANAGER
                        Ethereum address of the TxManager contract to use for
                        multi-step arbitrage
  --gas-price GAS_PRICE
                        Gas price in Wei (default: node default)
  --base-token BASE_TOKEN
                        The token all arbitrage sequences will start and end
                        with
  --min-profit MIN_PROFIT
                        Minimum profit (in base token) from one arbitrage
                        operation
  --max-engagement MAX_ENGAGEMENT
                        Maximum engagement (in base token) in one arbitrage
                        operation
  --max-errors MAX_ERRORS
                        Maximum number of allowed errors before the keeper
                        terminates (default: 100)
  --debug               Enable debug output
  --trace               Enable trace output
```

## License

See [COPYING](https://github.com/makerdao/arbitrage-keeper/blob/master/COPYING) file.
