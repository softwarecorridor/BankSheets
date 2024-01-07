from csv import DictReader
from io import TextIOWrapper
from typing import Any

from dateutil.parser import ParserError, parse

_SQL_KEYS = ["date", "amount", "description", "transaction_id"]

_MAP_CONVERSION = {
    ("Posted Date", "Reference Number", "Payee", "Address", "Amount"): [
        _SQL_KEYS[0],
        None,
        _SQL_KEYS[2],
        None,
        _SQL_KEYS[1],
    ],
    ("Date", "Description", "Amount", "Running Bal."): [
        _SQL_KEYS[0],
        _SQL_KEYS[2],
        _SQL_KEYS[1],
        None,
    ],
}


class NoHeaderException(Exception):
    def __init__(self) -> None:
        super().__init__("CSV file has no headers to key off of.")


class SkipAheadDictReader(DictReader):
    """
    Skips over any summary information and return a DictReader with just the
    transaction data.

    raises:
        NoHeaderException if there aren't anything we detect as a header.
    """

    def __init__(self, file: TextIOWrapper) -> None:
        if file is None:
            raise TypeError("SkipAheadDictReader doesn't accept None objects.")
        self.file = file
        headers = self._get_headers()
        new_headers = self._convert(headers)
        super().__init__(self.file, new_headers)

    def __next__(self) -> dict[Any, str | Any]:
        d = super().__next__()
        del d[None]
        return d

    def _get_headers(self) -> tuple[int, list[str]]:
        position = 0
        found = False
        line = self.file.readline()
        prev_row_segments = []
        while line != "" and not found:
            split_line = line.split(",")
            if len(split_line) > 0:
                first_segment_is_date = SkipAheadDictReader._contains_date(split_line)
                if first_segment_is_date:
                    if prev_row_segments == []:
                        raise NoHeaderException()
                    else:
                        found = True
                else:
                    position = self.file.tell()
                    prev_row_segments = split_line

                if not found:
                    line = self.file.readline()

        self.file.seek(position)
        return prev_row_segments

    @staticmethod
    def _contains_date(args: list[str]) -> bool:
        try:
            text = args[0].strip('"')
            parse(text)
            return True
        except ValueError:
            return False
        except ParserError as e:
            print(e)
            return False

    @staticmethod
    def _convert(header_row: list[str]) -> list[str]:
        key = SkipAheadDictReader._get_key(header_row)
        return _MAP_CONVERSION[key]

    @staticmethod
    def _get_key(header_row: list[str]) -> tuple[str]:
        new_headers = header_row
        new_headers[-1] = new_headers[-1].strip()
        return tuple(new_headers)
