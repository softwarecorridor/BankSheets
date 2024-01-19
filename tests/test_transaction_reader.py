from pytest import raises

from banksheets.transaction_reader import NoHeaderException, SkipAheadDictReader


def test_bofa_bank(bofa_bank_test_file):
    with open(bofa_bank_test_file) as csvfile:
        under_test = SkipAheadDictReader(csvfile)
        rows = list(under_test)
        assert len(rows) == 5
        assert all(item in rows[0] for item in ["date", "amount", "description"])


def test_bofa_cc(bofa_cc_test_file):
    with open(bofa_cc_test_file) as csvfile:
        under_test = SkipAheadDictReader(csvfile)
        rows = list(under_test)
        assert len(rows) == 5
        assert all(
            item in rows[0] for item in ["date", "amount", "description", "extra_desc"]
        )


def test_wells_bank(wells_bank_test_file):
    with raises(NoHeaderException):
        with open(wells_bank_test_file) as csvfile:
            SkipAheadDictReader(csvfile)
