from pytest import fixture, raises

from banksheets.entry import DataEntry


@fixture
def transaction_a():
    return {
        "date": "01/01/2023",
        "description": "Company A",
        "extra_desc": "City1, Street A",
        "amount": "100.25",
    }


@fixture
def transaction_a_negative():
    return {
        "date": "01/01/2023",
        "description": "Company A",
        "extra_desc": "City1, Street A",
        "amount": "-100.25",
    }


@fixture
def transaction_b():
    return {
        "date": "02/15/2023",
        "description": "Company B",
        "amount": "-150.75",
    }


@fixture
def transaction_c():
    return {
        "date": "03/10/2023",
        "description": "Company C",
        "extra_desc": "City3, Street C",
        "amount": "200",
    }


def test_parse(transaction_a):
    under_test = DataEntry(**transaction_a)
    assert under_test.date.strftime("%m/%d/%Y") == transaction_a["date"]
    assert under_test.amount == float(transaction_a["amount"])
    assert under_test.description == transaction_a["description"]
    assert under_test.extra_desc == transaction_a["extra_desc"]


def test_fail_parse():
    data = ["2020-01-01", "company a", "exrta b", 1]
    with raises(ValueError):
        DataEntry(*data)


def test_order_simple(transaction_a, transaction_b, transaction_c):
    ut_1 = DataEntry(**transaction_a)
    ut_2 = DataEntry(**transaction_c)
    ut_3 = DataEntry(**transaction_b)
    under_test = [ut_1, ut_2, ut_3]
    under_test.sort()
    assert under_test == [ut_1, ut_3, ut_2]


def test_equality(transaction_a):
    ut_1 = DataEntry(**transaction_a)
    ut_2 = DataEntry(**transaction_a)
    assert ut_1 == ut_2


def test_inequality(transaction_a, transaction_a_negative):
    ut_1 = DataEntry(**transaction_a)
    ut_2 = DataEntry(**transaction_a_negative)
    assert ut_1 != ut_2


def test_lt(transaction_a, transaction_b):
    ut_1 = DataEntry(**transaction_a)
    ut_2 = DataEntry(**transaction_b)
    assert ut_1 < ut_2


def test_to_str(transaction_a):
    ut_1 = DataEntry(**transaction_a)
    date_str = transaction_a["date"]
    amount_str = transaction_a["amount"]
    description_str = transaction_a["description"]
    extra_desc_str = transaction_a["extra_desc"]
    expected = f"{date_str}\t{amount_str}\t{description_str}\t{extra_desc_str}"
    assert str(ut_1) == expected
