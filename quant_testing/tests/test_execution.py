"""Test the execution module
"""
import queue

from quant_testing.core.execution import NaiveSimulationExecutor as Naive
from quant_testing.core.portfolio import SingleSharePortfolio as Portfolio
from quant_testing.tests.test_portfolio import MockTickdata
from quant_testing.core.events import FillEvent, OrderEvent, ExecutionType


def mock_comission(num_shares):
    return 10


def test_naive_fill():
    """ Test that the naive fill order method works, adding the correct fill event
    to the events object
    """
    events = queue.Queue()
    portfolio = Portfolio(events, 100, 0, MockTickdata(), commission_calc=mock_comission)
    naive_handler = Naive(portfolio, events, MockTickdata())

    mock_order = OrderEvent('MOCK', 'MKT', 10, ExecutionType.buy)
    naive_handler.fill_order(mock_order)
    assert events.qsize() == 1
    mock_output = events.get()
    assert mock_output.__dict__ == FillEvent(None, None, None,
                                             10, ExecutionType.buy, 10, 10).__dict__
