from pytest import raises

from banksheets.transaction_reader import NoHeaderException, SkipAheadDictReader


def test_skip_none():
    with raises(TypeError):
        with SkipAheadDictReader(None) as reader:
            rows = list(reader)
            assert len(rows) == 0


def test_skip_fake_file():
    with raises(FileNotFoundError):
        with SkipAheadDictReader("test") as reader:
            rows = list(reader)
            assert len(rows) == 0


def test_bofa_bank(bofa_bank_test_file):
    with SkipAheadDictReader(bofa_bank_test_file) as reader:
        rows = list(reader)
        assert len(rows) == 5


def test_bofa_cc(bofa_cc_test_file):
    with SkipAheadDictReader(bofa_cc_test_file) as reader:
        rows = list(reader)
        assert len(rows) == 5


def test_wells_bank(wells_bank_test_file):
    with raises(NoHeaderException):
        with SkipAheadDictReader(wells_bank_test_file) as reader:
            rows = list(reader)
            assert len(rows) == 0
