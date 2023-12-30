from collections.abc import KeysView

_SQL_KEYS = ["date", "amount", "description", "transaction_id"]

_MAP_CONVERSION = {
    ("Posted Date", "Reference Number", "Payee", "Address", "Amount"): {
        "Posted Date": _SQL_KEYS[0],
        "Reference Number": _SQL_KEYS[3],
        "Payee": _SQL_KEYS[2],
        "Address": None,
        "Amount": _SQL_KEYS[1],
    },
    ("Date", "Description", "Amount", "Running Bal."): {
        "Date": _SQL_KEYS[0],
        "Description": _SQL_KEYS[2],
        "Amount": _SQL_KEYS[1],
    },
}


def convert(row: dict[str, str]) -> dict[str, str]:
    """
    Convert a row in a csv file to use the same keys as the SQL

    Args:
        row (dict[str, str]): the row in a csv file
    Returns:
        dict[str, str] - the converted row
    Raises:
        MissingBankHeaderException: if the mapping from keys to sql keys doesn't exist.
    """
    key = _to_key(row.keys())
    if key in _MAP_CONVERSION:
        return _change_headers(row, _MAP_CONVERSION[key])
    else:
        raise MissingBankHeaderException(key)


def _to_key(keys: KeysView) -> tuple[str]:
    return tuple(keys)


def _change_headers(row: dict[str, str], mapping: dict[str, str]) -> dict[str, str]:
    return {value: row.get(key) for key, value in mapping.items() if value is not None}


class MissingBankHeaderException(Exception):
    """The header information doesn't have an associated mapping."""

    def __init__(self, header: tuple[str]) -> None:
        super().__init__(f"{header} has no BankSheet mapping.")
