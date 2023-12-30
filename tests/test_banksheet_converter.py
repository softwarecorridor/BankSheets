from pytest import raises

from banksheets.banksheet_converter import MissingBankHeaderException, convert


def test_convert_bofa_bank():
    under_test = {
        "Date": "01/01/01",
        "Description": "Test",
        "Amount": "12",
        "Running Bal.": "23123.123",
    }

    result = convert(under_test)
    expected = {
        "date": "01/01/01",
        "amount": "12",
        "description": "Test",
    }

    assert result == expected


def test_convert_bofa_cc():
    under_test = {
        "Posted Date": "01/01/01",
        "Reference Number": "123",
        "Payee": "Test",
        "Address": None,
        "Amount": "12",
    }

    result = convert(under_test)
    expected = {
        "date": "01/01/01",
        "amount": "12",
        "description": "Test",
        "transaction_id": "123",
    }

    assert result == expected


def test_non_existent_mapping():
    under_test = {
        "P Date": "01/01/01",
        "Ref Number": "123",
        "Payee": "Test",
        "Address": None,
        "Amount": "12",
    }

    with raises(MissingBankHeaderException):
        convert(under_test)
