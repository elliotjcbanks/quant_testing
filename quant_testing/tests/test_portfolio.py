"""Test the portfolio classes
"""
import queue
from unittest import mock

from quant_testing.core.portfolio import SingleSharePortfolio as Portfolio
from quant_testing.core.events import SignalEvent, FillEvent, OrderEvent, ExecutionType

# ############ Single share portfolio ###################################
# TODO: add more tests in a pytest.parametrize, rather than hard coded in
class MockTickdata:
    def get_latest_bars(*args):
        return {'share_price': 50}


def test_determine_move():
    import ipdb; ipdb.set_trace()
    events = queue.Queue()
    portfolio = Portfolio(events, 100, 0, MockTickdata())

    signal_event = SignalEvent(None, None, ExecutionType.buy)
    order_event = portfolio.determine_move(signal_event)
    assert isinstance(order_event, OrderEvent)
    assert order_event.order_type == 'MKT_ORDER'
    assert order_event.direction == ExecutionType.buy

    signal_event = SignalEvent(None, None, ExecutionType.sell)
    order_event = portfolio.generate_order(signal_event)
    assert isinstance(order_event, OrderEvent)
    assert order_event.order_type == 'MKT_ORDER'
    assert order_event.direction == ExecutionType.sell


def determine_move():
    pass


def test_buy_and_sell():
    portfolio = Portfolio(None, 100, 100, None)

    # buy a share
    portfolio.buy_instrument(10, 5, 10)
    assert portfolio.shares == 110
    assert portfolio.cash == 40

    # buy a share you can't buy
    portfolio.buy_instrument(10, 5, 100)
    assert portfolio.shares == 110
    assert portfolio.cash == 40

    # buy a share so there is zero cash
    portfolio.buy_instrument(3, 10, 10)
    assert portfolio.shares == 113
    assert portfolio.cash == 0

    # sell the instrument
    portfolio.sell_instrument(3, 100, 10)
    assert portfolio.shares == 110
    assert portfolio.cash == 290

    # Sell more shares than owned
    portfolio.sell_instrument(120, 1000, 10)
    assert portfolio.shares == 110
    assert portfolio.cash == 290


def test_update_portfolio():
    pass
