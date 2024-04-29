from banksheets.entry import DataEntry
from banksheets.ui.common import convert_csv_data_to_dataentry


def test_convert_csv_data_to_dataentry_none():
    result = convert_csv_data_to_dataentry(None)
    assert [] == result


def test_convert_csv_data_to_dataentry_empty():
    result = convert_csv_data_to_dataentry([])
    assert [] == result


def test_convert_csv_data_to_dataentry_single(transaction_a_negative):
    expected = DataEntry(**transaction_a_negative)
    result = convert_csv_data_to_dataentry([transaction_a_negative])
    assert expected == result[0]


def test_convert_csv_data_to_dataentry_multiple(
    transaction_a, transaction_a_negative, transaction_b, transaction_c
):
    input_arr = [transaction_a, transaction_a_negative, transaction_b, transaction_c]
    result = convert_csv_data_to_dataentry(input_arr)

    assert len(input_arr) == len(result)
    for expected, result in zip(input_arr, result):
        assert DataEntry(**expected) == result
