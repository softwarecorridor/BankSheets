from collections.abc import Iterator
from csv import DictReader
from pathlib import Path

from dateutil.parser import parse


class NoHeaderException(Exception):
    def __init__(self, file_name: Path) -> None:
        super().__init__(f"{file_name.stem} has no headers to key off of.")


class SkipAheadDictReader:
    """
    Skips over any summary information and return a DictReader with just the
    transaction data.

    Returns:
        csv.DictReader
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file = None

    def __enter__(self) -> Iterator[dict[str, str]]:
        header_line_index = self._get_header_line_index(Path(self.file_path))
        if header_line_index < 0:
            raise NoHeaderException(self.file_path)

        self.file = open(self.file_path, "r")

        for _ in range(header_line_index):
            next(self.file)

        return DictReader(self.file)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.file:
            self.file.close()

    def _get_header_line_index(self, file_path: Path) -> int:
        with open(file_path, "r") as f:
            found_header = False
            possible_line = -1
            current_line = 0
            line = f.readline()
            while line != "" and not found_header:
                split_line = line.split(",")
                if len(split_line) > 0:
                    contains_date = self._is_date(split_line[0])
                    if possible_line > -1:
                        if contains_date:
                            found_header = True
                        else:
                            possible_line = -1
                    if possible_line == -1 and not found_header:
                        if not contains_date:
                            possible_line = current_line
                current_line += 1
                line = f.readline()

            if not found_header:
                possible_line = -1
            return possible_line

    def _is_date(self, text: str) -> bool:
        try:
            parse(text)
            return True
        except ValueError:
            return False
