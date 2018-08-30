# arbitrage-keeper

[![Build Status](https://travis-ci.org/makerdao/arbitrage-keeper.svg?branch=master)](https://travis-ci.org/makerdao/arbitrage-keeper)
[![codecov](https://codecov.io/gh/makerdao/arbitrage-keeper/branch/master/graph/badge.svg)](https://codecov.io/gh/makerdao/arbitrage-keeper)

The _DAI Stablecoin System_ incentivizes external agents, called _keepers_,
to automate certain operations around the Ethereum blockchain.

`arbitrage-keeper` performs arbitrage on OasisDEX, `join`, `exit`, `boom` and `bust`.

Keeper constantly looks for profitable enough arbitrage opportunities
and executes them the moment they become available. It can make profit on:
- taking orders on OasisDEX (on DAI/PETH, DAI/W-ETH and PETH/W-ETH pairs),
- calling `join` and `exit` to exchange between W-ETH and PETH,
- calling `boom` and `bust` to exchange between DAI and PETH.

Opportunities discovered by the keeper are sequences of token exchanges
executed using methods listed above. An opportunity can consist of two
or three steps, technically it could be more but practically it will never
be more than three.

Steps can be executed sequentially (each one as a separate Ethereum
transaction, checking if one has been successful before executing the next
one) or in one ago. The latter method requires a `TxManager` contract deployed,
its address has to be passed as the `--tx-manager` argument. Also the `TxManager`
contract has to be owned by the account the keeper operates from.

You can find the source code of the `TxManager` here:
<https://github.com/makerdao/tx-manager>.

The base token is the token all arbitrage opportunities will start with.
Some amount of this token will be exchanged to some other token(s) and then exchanged
back to the base token, aiming to end up with more of it than we started with.
It implies that some amount of this token has to be provided to the keeper.
The higher the amount, the more profitable each arbitrage may be. Maximum
engagement in terms of base token can be set using the `--max-engagement` argument.

It is also beneficial to provide very small amounts of other tokens to the
keeper as well, mostly because of the rounding issues which may occur on
subsequent arbitrage steps. Currently the keeper operates on DAI, PETH and W-ETH.
It means that if we choose DAI as the base token, we should also give it some tiny
amounts of PETH and W-ETH. It may happen that due to rounding issues these amounts
will increase or decrease over time. Usually it is no more than 1 Wei increase
or decrease per one arbitrage opportunity.

In general, this keeper is already a bit dated. Especially OasisDEX order enumeration
can turn out to be really slow considering the current number of both open and historical
orders there. There is some caching mechanism in place, but it is a bit flawed as it
doesn't handle chain reorgs correctly. Having said that, `arbitrage-keeper` provides
valuable source of information where to look for arbitrage opportunities in the Dai system
and how to exploit them. It also demonstrates how to do atomic risk-free arbitrage
using the [tx-manager](https://github.com/makerdao/tx-manager) contract.

The `arbitrage-keeper` will not work with multicollateral Dai, mainly because
`boom` and `bust` actions will not be present in it anymore. Instead of that,
surplus and bad debt will be liquidated via auctions, supported by the new
[auction-keeper](https://github.com/makerdao/auction-keeper).

<https://chat.makerdao.com/channel/keeper>

## Installation

This project uses *Python 3.6.2*.

In order to clone the project and install required third-party packages please execute:
```
git clone https://github.com/makerdao/arbitrage-keeper.git
cd arbitrage-keeper
git submodule update --init --recursive
pip3 install -r requirements.txt
```

For some known Ubuntu and macOS issues see the [pymaker](https://github.com/makerdao/pymaker) README.

## Usage

```
usage: arbitrage-keeper [-h] [--rpc-host RPC_HOST] [--rpc-port RPC_PORT]
                        [--rpc-timeout RPC_TIMEOUT] --eth-from ETH_FROM
                        --tub-address TUB_ADDRESS --tap-address TAP_ADDRESS
                        --oasis-address OASIS_ADDRESS
                        [--oasis-support-address OASIS_SUPPORT_ADDRESS]
                        [--tx-manager TX_MANAGER] [--gas-price GAS_PRICE]
                        --base-token BASE_TOKEN --min-profit MIN_PROFIT
                        --max-engagement MAX_ENGAGEMENT
                        [--max-errors MAX_ERRORS] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --rpc-host RPC_HOST   JSON-RPC host (default: `localhost')
  --rpc-port RPC_PORT   JSON-RPC port (default: `8545')
  --rpc-timeout RPC_TIMEOUT
                        JSON-RPC timeout (in seconds, default: 10)
  --eth-from ETH_FROM   Ethereum account from which to send transactions
  --tub-address TUB_ADDRESS
                        Ethereum address of the Tub contract
  --tap-address TAP_ADDRESS
                        Ethereum address of the Tap contract
  --oasis-address OASIS_ADDRESS
                        Ethereum address of the OasisDEX contract
  --oasis-support-address OASIS_SUPPORT_ADDRESS
                        Ethereum address of the OasisDEX support contract
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
```

## License

See [COPYING](https://github.com/makerdao/arbitrage-keeper/blob/master/COPYING) file.

### Disclaimer

YOU (MEANING ANY INDIVIDUAL OR ENTITY ACCESSING, USING OR BOTH THE SOFTWARE INCLUDED IN THIS GITHUB REPOSITORY) EXPRESSLY UNDERSTAND AND AGREE THAT YOUR USE OF THE SOFTWARE IS AT YOUR SOLE RISK.
THE SOFTWARE IN THIS GITHUB REPOSITORY IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
YOU RELEASE AUTHORS OR COPYRIGHT HOLDERS FROM ALL LIABILITY FOR YOU HAVING ACQUIRED OR NOT ACQUIRED CONTENT IN THIS GITHUB REPOSITORY. THE AUTHORS OR COPYRIGHT HOLDERS MAKE NO REPRESENTATIONS CONCERNING ANY CONTENT CONTAINED IN OR ACCESSED THROUGH THE SERVICE, AND THE AUTHORS OR COPYRIGHT HOLDERS WILL NOT BE RESPONSIBLE OR LIABLE FOR THE ACCURACY, COPYRIGHT COMPLIANCE, LEGALITY OR DECENCY OF MATERIAL CONTAINED IN OR ACCESSED THROUGH THIS GITHUB REPOSITORY. 
