from unittest import mock
import pandas as pd
import numpy as np

import pytest
import queue

from quant_testing.core.datahandler import DailyHandler as csv_handler


@pytest.fixture
def mock_data():
    """ Example csv data to read
    """
    mock_data = np.array([[pd.Timestamp('2017-08-03 00:00:00'),
                           930.34, 932.24, 922.24, 923.65, '1202512'],
                          [pd.Timestamp('2017-08-04 00:00:00'),
                           926.75, 930.31, 923.03, 927.96, '1082267'],
                          [pd.Timestamp('2017-08-07 00:00:00'),
                           929.06, 931.7, 926.5, 929.36, '1032239'],
                          [pd.Timestamp('2017-08-08 00:00:00'),
                           927.09, 935.81, 925.61, 926.79, '1061579'],
                          [pd.Timestamp('2017-08-09 00:00:00'),
                           920.61, 925.98, 917.25, 922.9, '1192081'],
                          [pd.Timestamp('2017-08-10 00:00:00'),
                           917.55, 919.26, 906.13, 907.24, '1823967'],
                          [pd.Timestamp('2017-08-11 00:00:00'),
                           907.97, 917.78, 905.58, 914.39, '1206782'],
                          [pd.Timestamp('2017-08-14 00:00:00'),
                           922.53, 924.67, 918.19, 922.67, '1064530'],
                          [pd.Timestamp('2017-08-15 00:00:00'),
                           924.23, 926.55, 919.82, 922.22, '883369'],
                          [pd.Timestamp('2017-08-16 00:00:00'),
                           925.29, 932.7, 923.44, 926.96, '1006711'],
                          [pd.Timestamp('2017-08-17 00:00:00'),
                           925.78, 926.86, 910.98, 910.98, '1277238'],
                          [pd.Timestamp('2017-08-18 00:00:00'),
                           910.31, 915.28, 907.15, 910.67, '1342689'],
                          [pd.Timestamp('2017-08-21 00:00:00'),
                           910.0, 913.0, 903.4, 906.66, '943441'],
                          [pd.Timestamp('2017-08-22 00:00:00'),
                           912.72, 925.86, 911.48, 924.69, '1166737'],
                          [pd.Timestamp('2017-08-23 00:00:00'),
                           921.93, 929.93, 919.36, 927.0, '1090248'],
                          [pd.Timestamp('2017-08-24 00:00:00'),
                           928.66, 930.84, 915.5, 921.28, '1270306'],
                          [pd.Timestamp('2017-08-25 00:00:00'),
                           923.49, 925.56, 915.5, 915.89, '1053376'],
                          [pd.Timestamp('2017-08-28 00:00:00'),
                           916.0, 919.24, 911.87, 913.81, '1086484'],
                          [pd.Timestamp('2017-08-29 00:00:00'),
                           905.1, 923.33, 905.0, 921.29, '1185564'],
                          [pd.Timestamp('2017-08-30 00:00:00'),
                           920.05, 930.82, 919.65, 929.57, '1301225']], dtype=object)

    return mock_data


def mock_read_file(self, mock_data):
    """ Mock the datahandler read file, to mock the csv reading
    """
    self.data = generate_dataframe(mock_data)


def generate_dataframe(data):
    """Create a pandas dataframe from data for the csv testing
    """
    df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'share_price', 'Volume'])
    col_list = ['Open', 'High', 'Low', 'share_price', 'Volume']
    df[col_list] = df[col_list].astype('float64')
    df = df.set_index('timestamp')
    return df


@mock.patch.object(csv_handler, 'read_file', mock_read_file)
def test_datahandler_constructor(mock_data):
    """ Test that the datahandler ca correctly get datapoints from the csv file
    """
    events = queue.Queue()
    test_datahandler = csv_handler(mock_data, events)

    assert test_datahandler.events == events
    assert test_datahandler.current_timestamp == pd.to_datetime(mock_data[:, 0]).min()


@mock.patch.object(csv_handler, 'read_file', mock_read_file)
@pytest.mark.parametrize("position", [1, 6, 18])
@pytest.mark.parametrize("points", [0, 1, 2])
def test_get_data_points(mock_data, position, points):
    """ Test that the datahandler ca correctly get datapoints from the csv file
    """
    events = queue.Queue()
    test_datahandler = csv_handler(mock_data, events)

    time_to_check = pd.to_datetime(mock_data[position, 0])
    test_dataframe = test_datahandler.get_data_points(time_to_check, points)
    expected_dataframe = (generate_dataframe(mock_data[max(position - points, 0): position])
                          .reset_index(drop=True))

    assert test_dataframe.equals(expected_dataframe)


@mock.patch.object(csv_handler, 'read_file', mock_read_file)
@pytest.mark.parametrize("position", [1, 6, 18])
@pytest.mark.parametrize("points", [0, 1, 2])
def test_update_bars_get_latest_bars(mock_data, position, points):
    """ Test that the datahandler ca correctly get datapoints from the csv file
    """
    events = queue.Queue()
    max_timestamp = pd.to_datetime(mock_data[position, 0])
    test_datahandler = csv_handler(mock_data, events, max_timestamp=max_timestamp)

    # Check that a single update goes in the right position
    test_datahandler.update_bars()
    assert events.qsize() == 1
