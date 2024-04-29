from pathlib import Path

import pytest


def base_csv_test_file(request, filename: str) -> Path:
    module_path: Path = Path(request.module.__file__)
    test_files_dir: Path = module_path.parent / "sample_data"
    return test_files_dir / filename


@pytest.fixture
def bofa_bank_test_file(request) -> Path:
    return base_csv_test_file(request, "sample_bofa_bank.csv")


@pytest.fixture
def bofa_cc_test_file(request) -> Path:
    return base_csv_test_file(request, "sample_bofa_cc.csv")


@pytest.fixture
def wells_bank_test_file(request) -> Path:
    return base_csv_test_file(request, "sample_wells_bank.csv")


@pytest.fixture
def transaction_a():
    return {
        "date": "01/01/2023",
        "description": "Company A",
        "extra_desc": "City1, Street A",
        "amount": "100.25",
    }


@pytest.fixture
def transaction_a_negative():
    return {
        "date": "01/01/2023",
        "description": "Company A",
        "extra_desc": "City1, Street A",
        "amount": "-100.25",
    }


@pytest.fixture
def transaction_b():
    return {
        "date": "02/15/2023",
        "description": "Company B",
        "amount": "-150.75",
    }


@pytest.fixture
def transaction_c():
    return {
        "date": "03/10/2023",
        "description": "Company C",
        "extra_desc": "City3, Street C",
        "amount": "200",
    }
