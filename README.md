# arbitrage-keeper

[![Build Status](https://travis-ci.org/makerdao/arbitrage-keeper.svg?branch=master)](https://travis-ci.org/makerdao/arbitrage-keeper)
[![codecov](https://codecov.io/gh/makerdao/arbitrage-keeper/branch/master/graph/badge.svg)](https://codecov.io/gh/makerdao/arbitrage-keeper)

The _DAI Stablecoin System_ incentivizes external agents, called _keepers_,
to automate certain operations around the Ethereum blockchain.

TODO

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

TODO

## License

See [COPYING](https://github.com/makerdao/arbitrage-keeper/blob/master/COPYING) file.
