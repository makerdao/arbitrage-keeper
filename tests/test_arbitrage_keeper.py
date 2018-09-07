# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2017 reverendus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import time

import pkg_resources
import pytest

from arbitrage_keeper.arbitrage_keeper import ArbitrageKeeper
from pymaker import Address
from pymaker.approval import directly
from pymaker.deployment import Deployment, deploy_contract
from pymaker.feed import DSValue
from pymaker.numeric import Wad, Ray
from pymaker.token import ERC20Token
from pymaker.transactional import TxManager
from pymaker.zrx import ZrxExchange
from tests.helper import args, captured_output, time_travel_by


class TestArbitrageKeeper:
    def test_should_not_start_without_eth_from_argument(self, deployment: Deployment):
        # when
        with captured_output() as (out, err):
            with pytest.raises(SystemExit):
                ArbitrageKeeper(args=args(f""),
                                web3=deployment.web3)

        # then
        assert "error: the following arguments are required: --eth-from" in err.getvalue()

    def test_should_not_start_without_tub_address_argument(self, deployment: Deployment):
        # when
        with captured_output() as (out, err):
            with pytest.raises(SystemExit):
                ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"),
                                web3=deployment.web3)

        # then
        assert "error: the following arguments are required: --tub-address" in err.getvalue()

    def test_should_not_start_without_tap_address_argument(self, deployment: Deployment):
        # when
        with captured_output() as (out, err):
            with pytest.raises(SystemExit):
                ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                       f" --tub-address {deployment.tub.address}"),
                                web3=deployment.web3)

        # then
        assert "error: the following arguments are required: --tap-address" in err.getvalue()

    def test_should_not_start_without_oasis_address_argument(self, deployment: Deployment):
        # when
        with captured_output() as (out, err):
            with pytest.raises(SystemExit):
                ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                       f" --tub-address {deployment.tub.address}"
                                       f" --tap-address {deployment.tap.address}"),
                                web3=deployment.web3)

        # then
        assert "error: the following arguments are required: --oasis-address" in err.getvalue()

    def test_should_not_start_without_base_token_argument(self, deployment: Deployment):
        # when
        with captured_output() as (out, err):
            with pytest.raises(SystemExit):
                ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                       f" --tub-address {deployment.tub.address}"
                                       f" --tap-address {deployment.tap.address}"
                                       f" --oasis-address {deployment.otc.address}"),
                                web3=deployment.web3)

        # then
        assert "error: the following arguments are required: --base-token" in err.getvalue()

    def test_should_not_start_without_min_profit_argument(self, deployment: Deployment):
        # when
        with captured_output() as (out, err):
            with pytest.raises(SystemExit):
                ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                       f" --tub-address {deployment.tub.address}"
                                       f" --tap-address {deployment.tap.address}"
                                       f" --oasis-address {deployment.otc.address}"
                                       f" --base-token {deployment.sai.address}"),
                                web3=deployment.web3)

        # then
        assert "error: the following arguments are required: --min-profit" in err.getvalue()

    def test_should_not_start_without_max_engagement_argument(self, deployment: Deployment):
        # when
        with captured_output() as (out, err):
            with pytest.raises(SystemExit):
                ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                       f" --tub-address {deployment.tub.address}"
                                       f" --tap-address {deployment.tap.address}"
                                       f" --oasis-address {deployment.otc.address}"
                                       f" --base-token {deployment.sai.address}"
                                       f" --min-profit 1.0"),
                                web3=deployment.web3)

        # then
        assert "error: the following arguments are required: --max-engagement" in err.getvalue()

    def test_should_not_start_if_base_token_is_invalid(self, deployment: Deployment):
        # expect
        with pytest.raises(Exception):
            ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                   f" --tub-address {deployment.tub.address}"
                                   f" --tap-address {deployment.tap.address}"
                                   f" --oasis-address {deployment.otc.address}"
                                   f" --base-token 0x1121211212112121121211212112121121211212"
                                   f" --min-profit 1.0 --max-engagement 1000.0"),
                            web3=deployment.web3)

    def test_should_not_do_anything_if_no_arbitrage_opportunities(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.sai.address}"
                                        f" --min-profit 1.0 --max-engagement 1000.0"),
                                 web3=deployment.web3)

        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tap.mold_gap(Wad.from_number(1.05)).transact()

        # when
        keeper.approve()
        keeper.process_block()

        # then
        # (nothing happens)

    def test_should_identify_multi_step_arbitrage_on_oasis(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.sai.address}"
                                        f" --min-profit 13.0 --max-engagement 100.0"),
                                 web3=deployment.web3)

        # and
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tub.mold_gap(Wad.from_number(1.05)).transact()
        deployment.tub.join(Wad.from_number(1000)).transact()
        deployment.tap.mold_gap(Wad.from_number(1.05)).transact()

        # and
        deployment.sai.mint(Wad.from_number(1000)).transact()

        # and
        deployment.otc.approve([deployment.gem, deployment.sai, deployment.skr], directly())
        deployment.otc.add_token_pair_whitelist(deployment.sai.address, deployment.skr.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.skr.address, deployment.gem.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.gem.address, deployment.sai.address).transact()
        deployment.otc.make(deployment.skr.address, Wad.from_number(105), deployment.sai.address, Wad.from_number(100)).transact()
        deployment.otc.make(deployment.gem.address, Wad.from_number(110), deployment.skr.address, Wad.from_number(105)).transact()
        deployment.otc.make(deployment.sai.address, Wad.from_number(115), deployment.gem.address, Wad.from_number(110)).transact()
        assert len(deployment.otc.get_orders()) == 3

        # when
        keeper.approve()
        block_number_before = deployment.web3.eth.blockNumber
        keeper.process_block()
        block_number_after = deployment.web3.eth.blockNumber

        # then
        assert len(deployment.otc.get_orders()) == 0

        # and
        # [keeper used three transactions, as TxManager is not configured]
        assert (block_number_after - block_number_before) == 3

    def test_should_execute_arbitrage_in_one_transaction_if_tx_manager_configured(self, deployment: Deployment):
        # given
        tx_manager = TxManager.deploy(deployment.web3)

        # and
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.sai.address}"
                                        f" --min-profit 13.0 --max-engagement 100.0"
                                        f" --tx-manager {tx_manager.address}"),
                                 web3=deployment.web3)

        # and
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tub.mold_gap(Wad.from_number(1.05)).transact()
        deployment.tub.join(Wad.from_number(1000)).transact()
        deployment.tap.mold_gap(Wad.from_number(1.05)).transact()

        # and
        deployment.sai.mint(Wad.from_number(1000)).transact()

        # and
        deployment.otc.approve([deployment.gem, deployment.sai, deployment.skr], directly())
        deployment.otc.add_token_pair_whitelist(deployment.sai.address, deployment.skr.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.skr.address, deployment.gem.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.gem.address, deployment.sai.address).transact()
        deployment.otc.make(deployment.skr.address, Wad.from_number(105), deployment.sai.address, Wad.from_number(100)).transact()
        deployment.otc.make(deployment.gem.address, Wad.from_number(110), deployment.skr.address, Wad.from_number(105)).transact()
        deployment.otc.make(deployment.sai.address, Wad.from_number(115), deployment.gem.address, Wad.from_number(110)).transact()
        assert len(deployment.otc.get_orders()) == 3

        # when
        keeper.approve()
        block_number_before = deployment.web3.eth.blockNumber
        keeper.process_block()
        block_number_after = deployment.web3.eth.blockNumber

        # then
        assert len(deployment.otc.get_orders()) == 0

        # and
        # [keeper used only one transaction, as TxManager is configured]
        assert (block_number_after - block_number_before) == 1

    def test_should_identify_arbitrage_against_oasis_and_join(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.gem.address}"
                                        f" --min-profit 5.0 --max-engagement 100.0"),
                                 web3=deployment.web3)

        # and
        # [a price is set, so the arbitrage keeper knows prices of `boom` and `bust`]
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()

        # and
        # [we have 100 WETH]
        deployment.gem.mint(Wad.from_number(100)).transact()

        # and
        # [somebody else placed an order on OASIS offering 110 WETH for 100 SKR]
        second_address = Address(deployment.web3.eth.accounts[1])

        deployment.gem.transfer(second_address, Wad.from_number(110)).transact()
        deployment.otc.add_token_pair_whitelist(deployment.skr.address, deployment.gem.address).transact()
        deployment.otc.approve([deployment.gem, deployment.skr], directly(from_address=second_address))
        deployment.otc.make(deployment.gem.address, Wad.from_number(110), deployment.skr.address, Wad.from_number(100)).transact(from_address=second_address)
        assert deployment.skr.total_supply() == Wad.from_number(0)
        assert len(deployment.otc.get_orders()) == 1

        # when
        keeper.approve()
        keeper.process_block()

        # then
        # [the order on Oasis has been taken by the keeper]
        assert len(deployment.otc.get_orders()) == 0

        # and
        # [the total supply of SKR has increased, so we know the keeper did call join('100.0')]
        assert deployment.skr.total_supply() == Wad.from_number(100)

    def test_should_identify_arbitrage_against_oasis_and_exit(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.gem.address}"
                                        f" --min-profit 5.0 --max-engagement 100.0"),
                                 web3=deployment.web3)

        # and
        # [a price is set, so the arbitrage keeper knows prices of `boom` and `bust`]
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()

        # and
        # [we have 100 WETH]
        deployment.gem.mint(Wad.from_number(100)).transact()

        # and
        # [somebody else placed an order on OASIS offering 110 SKR for 100 WETH]
        second_address = Address(deployment.web3.eth.accounts[1])

        deployment.gem.mint(Wad.from_number(110)).transact()
        deployment.tub.join(Wad.from_number(110)).transact()
        deployment.skr.transfer(second_address, Wad.from_number(110)).transact()
        deployment.otc.add_token_pair_whitelist(deployment.skr.address, deployment.gem.address).transact()
        deployment.otc.approve([deployment.gem, deployment.skr], directly(from_address=second_address))
        deployment.otc.make(deployment.skr.address, Wad.from_number(110), deployment.gem.address, Wad.from_number(100)).transact(from_address=second_address)
        assert deployment.skr.total_supply() == Wad.from_number(110)
        assert len(deployment.otc.get_orders()) == 1

        # when
        keeper.approve()
        keeper.process_block()

        # then
        # [the order on Oasis has been taken by the keeper]
        assert len(deployment.otc.get_orders()) == 0

        # and
        # [the total supply of SKR has decreased, so we know the keeper did call exit('110.0')]
        assert deployment.skr.total_supply() == Wad.from_number(0)

    def test_should_identify_arbitrage_against_oasis_and_boom(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                           f" --tub-address {deployment.tub.address}"
                                           f" --tap-address {deployment.tap.address}"
                                           f" --oasis-address {deployment.otc.address}"
                                           f" --base-token {deployment.sai.address}"
                                           f" --min-profit 100.0 --max-engagement 500000.0"),
                                 web3=deployment.web3)

        # and
        # [we generate some Dai surplus available for `boom`]
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tub.mold_cap(Wad.from_number(10000000000)).transact()
        deployment.tub.mold_mat(Ray.from_number(1.5)).transact()
        deployment.tub.mold_axe(Ray.from_number(1.2)).transact()
        deployment.tub.mold_tax(Ray.from_number(1.0000000001)).transact()
        deployment.gem.mint(Wad.from_number(1000000)).transact()
        deployment.tub.join(Wad.from_number(1000000)).transact()
        deployment.tub.open().transact()
        deployment.tub.lock(1, Wad.from_number(1000000)).transact()
        deployment.tub.draw(1, Wad.from_number(250000000)).transact()
        time_travel_by(deployment.web3, 60*60*24*180)
        deployment.tub.wipe(1, Wad.from_number(250000000)).transact()
        print(deployment.tap.joy())
        assert Wad.from_number(389102) < deployment.tap.joy() < Wad.from_number(389103)

        # and
        # [we add a boom/bust spread to make calculations a bit more difficult]
        deployment.tap.mold_gap(Wad.from_number(0.95)).transact()
        assert deployment.tap.ask(Wad.from_number(1)) == Wad.from_number(475.0)
        assert deployment.tap.bid(Wad.from_number(1)) == Wad.from_number(525.0)

        # and
        # [we have lots of SAI to invest]
        deployment.sai.mint(Wad.from_number(5000000.00)).transact()

        # [we have some SKR to cover rounding errors]
        deployment.skr.mint(Wad.from_number(0.000000000000000001)).transact()

        # and
        # [we should now have 389102.xx SAI available for 741.14 SKR on `boom`]
        # [now lets pretend somebody else placed an order on OASIS offering 1000 GEM for 500000 SAI]
        second_address = Address(deployment.web3.eth.accounts[1])

        deployment.gem.mint(Wad.from_number(1000)).transact()
        deployment.gem.transfer(second_address, Wad.from_number(1000)).transact()
        deployment.otc.approve([deployment.sai, deployment.gem], directly(from_address=second_address))
        deployment.otc.make(deployment.gem.address, Wad.from_number(1000), deployment.sai.address, Wad.from_number(500000)).transact(from_address=second_address)
        assert len(deployment.otc.get_orders()) == 1

        # when
        keeper.approve()
        keeper.process_block()

        # and
        # [the amount of surplus is almost zero, so we know the keeper did call boom()]
        # [the inequality below is to cater for rounding errors]
        assert deployment.tap.joy() < Wad.from_number(0.1)

    def test_should_identify_arbitrage_against_oasis_and_bust(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.sai.address}"
                                        f" --min-profit 950.0 --max-engagement 14250.0"),
                                 web3=deployment.web3)

        # and
        # [we generate some bad debt available for `bust`]
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tub.mold_cap(Wad.from_number(1000000)).transact()
        deployment.tub.mold_mat(Ray.from_number(2.0)).transact()
        deployment.tub.mold_axe(Ray.from_number(2.0)).transact()
        deployment.gem.mint(Wad.from_number(100)).transact()
        deployment.tub.join(Wad.from_number(100)).transact()
        deployment.tub.open().transact()
        deployment.tub.lock(1, Wad.from_number(100)).transact()
        deployment.tub.draw(1, Wad.from_number(25000)).transact()
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(400).value).transact()
        deployment.tub.bite(1).transact()
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        assert deployment.tap.woe() == Wad.from_number(25000)
        assert deployment.tap.fog() == Wad.from_number(100)

        # and
        # [we add a boom/bust spread to make calculations a bit more difficult]
        deployment.tap.mold_gap(Wad.from_number(0.95)).transact()
        assert deployment.tap.ask(Wad.from_number(1)) == Wad.from_number(475.0)
        assert deployment.tap.bid(Wad.from_number(1)) == Wad.from_number(525.0)

        # and
        # [we have some SKR to cover rounding errors]
        deployment.skr.mint(Wad.from_number(0.000000000000000001)).transact()

        # and
        # [we should now have 30 SKR available for 14250 SAI on `bust`]
        # [now lets pretend somebody else placed an order on OASIS offering 15250 SAI for 30 GEM]
        # [this will be an arbitrage opportunity which can make the bot earn 1000 SAI]
        second_address = Address(deployment.web3.eth.accounts[1])

        deployment.sai.mint(Wad.from_number(15250)).transact()
        deployment.sai.transfer(second_address, Wad.from_number(15250)).transact()
        deployment.otc.approve([deployment.sai, deployment.gem], directly(from_address=second_address))
        deployment.otc.make(deployment.sai.address, Wad.from_number(15250), deployment.gem.address, Wad.from_number(30)).transact(from_address=second_address)
        assert len(deployment.otc.get_orders()) == 1

        # when
        keeper.approve()
        keeper.process_block()

        # then
        # [the order on Oasis has been taken by the keeper]
        assert len(deployment.otc.get_orders()) == 0

        # and
        # [the amount of bad debt has decreased, so we know the keeper did call bust('14250.0')]
        # [the inequality below is to cater for rounding errors]
        assert deployment.tap.woe() < Wad.from_number(10800.0)

    def test_should_identify_arbitrage_against_0x_and_bust(self, deployment: Deployment):
        # given
        # [0x protocol is in place]
        zrx_token = ERC20Token(web3=deployment.web3, address=deploy_contract(deployment.web3, 'ZRXToken'))
        token_transfer_proxy_address = deploy_contract(deployment.web3, 'TokenTransferProxy')
        exchange = ZrxExchange.deploy(deployment.web3, zrx_token.address, token_transfer_proxy_address)
        deployment.web3.eth.contract(abi=json.loads(pkg_resources.resource_string('pymaker.deployment', f'abi/TokenTransferProxy.abi')))(address=token_transfer_proxy_address.address).transact().addAuthorizedAddress(exchange.address.address)

        # and
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                           f" --tub-address {deployment.tub.address}"
                                           f" --tap-address {deployment.tap.address}"
                                           f" --oasis-address {deployment.otc.address}"
                                           f" --exchange-address {exchange.address}"
                                           f" --relayer-api-server http://127.0.0.1:9999/sra/v0"
                                           f" --base-token {deployment.sai.address}"
                                           f" --min-profit 950.0 --max-engagement 14250.0"),
                                 web3=deployment.web3)

        # and
        # [we generate some bad debt available for `bust`]
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tub.mold_cap(Wad.from_number(1000000)).transact()
        deployment.tub.mold_mat(Ray.from_number(2.0)).transact()
        deployment.tub.mold_axe(Ray.from_number(2.0)).transact()
        deployment.gem.mint(Wad.from_number(100)).transact()
        deployment.tub.join(Wad.from_number(100)).transact()
        deployment.tub.open().transact()
        deployment.tub.lock(1, Wad.from_number(100)).transact()
        deployment.tub.draw(1, Wad.from_number(25000)).transact()
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(400).value).transact()
        deployment.tub.bite(1).transact()
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        assert deployment.tap.woe() == Wad.from_number(25000)
        assert deployment.tap.fog() == Wad.from_number(100)

        # and
        # [we add a boom/bust spread to make calculations a bit more difficult]
        deployment.tap.mold_gap(Wad.from_number(0.95)).transact()
        assert deployment.tap.ask(Wad.from_number(1)) == Wad.from_number(475.0)
        assert deployment.tap.bid(Wad.from_number(1)) == Wad.from_number(525.0)

        # and
        # [we have some SKR to cover rounding errors]
        deployment.skr.mint(Wad.from_number(0.000000000000000001)).transact()

        # and
        # [we should now have 30 SKR available for 14250 SAI on `bust`]
        # [now lets pretend we placed an order on 0x offering 15250 SAI for 30 GEM]
        # [this will be an arbitrage opportunity which can make the bot earn 1000 SAI]
        deployment.sai.mint(Wad.from_number(15250)).transact()
        exchange.approve([deployment.sai, deployment.gem], directly())
        zrx_order = exchange.sign_order(exchange.create_order(pay_token=deployment.sai.address,
                                                              pay_amount=Wad.from_number(15250),
                                                              buy_token=deployment.gem.address,
                                                              buy_amount=Wad.from_number(30), expiration=int(time.time() + 3600)))
        keeper.zrx_orders = lambda tokens: [zrx_order]

        # when
        keeper.approve()
        keeper.process_block()

        # then
        # [the 0x order has been taken by the keeper]
        assert exchange.get_unavailable_buy_amount(zrx_order) == Wad.from_number(30)

        # and
        # [the amount of bad debt has decreased, so we know the keeper did call bust('14250.0')]
        # [the inequality below is to cater for rounding errors]
        assert deployment.tap.woe() < Wad.from_number(10800.0)

    def test_should_obey_max_engagement(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.sai.address}"
                                        f" --min-profit 1.0 --max-engagement 90.0"),
                                 web3=deployment.web3)

        # and
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tub.mold_gap(Wad.from_number(1.05)).transact()
        deployment.tub.join(Wad.from_number(1000)).transact()
        deployment.tap.mold_gap(Wad.from_number(1.05)).transact()

        # and
        deployment.sai.mint(Wad.from_number(1000)).transact()

        # and
        deployment.otc.approve([deployment.gem, deployment.sai, deployment.skr], directly())
        deployment.otc.add_token_pair_whitelist(deployment.sai.address, deployment.skr.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.skr.address, deployment.gem.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.gem.address, deployment.sai.address).transact()
        deployment.otc.make(deployment.skr.address, Wad.from_number(105), deployment.sai.address, Wad.from_number(100)).transact()
        deployment.otc.make(deployment.gem.address, Wad.from_number(110), deployment.skr.address, Wad.from_number(105)).transact()
        deployment.otc.make(deployment.sai.address, Wad.from_number(115), deployment.gem.address, Wad.from_number(110)).transact()
        assert len(deployment.otc.get_orders()) == 3

        # when
        keeper.approve()
        keeper.process_block()

        # then
        assert len(deployment.otc.get_orders()) == 3
        assert deployment.otc.get_orders()[0].buy_amount == Wad.from_number(10)

    def test_should_obey_min_profit(self, deployment: Deployment):
        # given
        keeper = ArbitrageKeeper(args=args(f"--eth-from {deployment.our_address.address}"
                                        f" --tub-address {deployment.tub.address}"
                                        f" --tap-address {deployment.tap.address}"
                                        f" --oasis-address {deployment.otc.address}"
                                        f" --base-token {deployment.sai.address}"
                                        f" --min-profit 16.0 --max-engagement 1000.0"),
                                 web3=deployment.web3)

        # and
        DSValue(web3=deployment.web3, address=deployment.tub.pip()).poke_with_int(Wad.from_number(500).value).transact()
        deployment.tub.mold_gap(Wad.from_number(1.05)).transact()
        deployment.tub.join(Wad.from_number(1000)).transact()
        deployment.tap.mold_gap(Wad.from_number(1.05)).transact()

        # and
        deployment.sai.mint(Wad.from_number(1000)).transact()

        # and
        deployment.otc.approve([deployment.gem, deployment.sai, deployment.skr], directly())
        deployment.otc.add_token_pair_whitelist(deployment.sai.address, deployment.skr.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.skr.address, deployment.gem.address).transact()
        deployment.otc.add_token_pair_whitelist(deployment.gem.address, deployment.sai.address).transact()
        deployment.otc.make(deployment.skr.address, Wad.from_number(105), deployment.sai.address, Wad.from_number(100)).transact()
        deployment.otc.make(deployment.gem.address, Wad.from_number(110), deployment.skr.address, Wad.from_number(105)).transact()
        deployment.otc.make(deployment.sai.address, Wad.from_number(115), deployment.gem.address, Wad.from_number(110)).transact()
        assert len(deployment.otc.get_orders()) == 3

        # when
        keeper.approve()
        keeper.process_block()

        # then
        assert len(deployment.otc.get_orders()) == 3
        assert deployment.otc.get_orders()[0].buy_amount == Wad.from_number(100)
        assert deployment.otc.get_orders()[1].buy_amount == Wad.from_number(105)
        assert deployment.otc.get_orders()[2].buy_amount == Wad.from_number(110)
