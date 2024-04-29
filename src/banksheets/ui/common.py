import itertools
from pathlib import Path
from sqlite3 import Connection

from banksheets.entry import DataEntry
from banksheets.sql_commands import get_potential_duplicates
from banksheets.transaction_reader import (
    MissingHeadingMapping,
    NoHeaderException,
    SkipAheadDictReader,
)


def _get_data_from_folder(folder: Path) -> list[dict[str, str]]:
    """Search a directory for csv files and return the rows of data.

    Args:
        folder - the source folder
    Returns:
        The transaction data
    """
    transactions = []
    for file in folder.glob("*.csv"):
        transactions.extend(_read_file(file))
    return transactions


def _read_file(path: Path) -> list[dict[str, str]]:
    """Try to read a csv file and return the data inside. Attempts to ignore none
    transaction data.

    Args:
        path - the source file
    Returns:
        The transaction data.
    """
    with open(path) as f:
        try:
            reader = SkipAheadDictReader(f)
            return list(reader)
        except NoHeaderException:
            pass
        except MissingHeadingMapping:
            pass
    return []


def convert_csv_data_to_dataentry(items: list[dict[str, str]]) -> list[DataEntry]:
    """Convert transaction data into dataentry

    Args:
        items - the list of transaction rows from csv
    Returns:
        The list of dataentries
    """
    if items is not None:

        def create(item: dict[str, str]) -> DataEntry:
            try:
                return DataEntry(**item)
            except ValueError:
                print("weird data")

        converted = map(create, items)
        return list(converted)
    else:
        return []


def get_duplicate_groups(db: Connection) -> list[list[int], int, tuple]:
    """Get information about all the duplicates currently in the potential table.

    Args:
        db - an active sql connection
    Returns:
        A list with items that are present more than once. Each item:
            0 - the list of ids with duplicate info in potential.\n
            1 - the number of items already saved to disk.\n
            2 - a tuple with the transaction details.
    """
    data = get_potential_duplicates(db)
    grouped_data = []
    for key, group in itertools.groupby(data, key=lambda x: (x[1], x[2], x[3], x[4])):
        potential_ids = []
        saved_count = 0
        for section in group:
            potential_ids.append(section[0])
            saved_count = section[5]

        grouped_data.append([potential_ids, saved_count, key])

    return grouped_data


def get_data(path: Path) -> list[DataEntry]:
    """Open the path and return the transaction data

    Args:
        path - the source location
    Returns:
        The transaction data
    """
    transaction_data = None
    if path.is_dir():
        transaction_data = _get_data_from_folder(path)
    else:
        transaction_data = _read_file(path)
    return convert_csv_data_to_dataentry(transaction_data)


def check_and_convert_source(path: str) -> Path:
    """Look for potential source data while converting the string to a Path

    Args:
        path - the source location string
    Returns:
        Path object of the string
    Raises:
        FileNotFoundError - No csv files in the passed in directory\n
        TypeError - The given file was not a csv
    """
    source_path = Path(path)
    if source_path.is_dir():
        csv_files = list(source_path.glob("*.csv"))
        if len(csv_files) == 0:
            raise FileNotFoundError(
                f"{source_path.stem} does not contain any CSV files."
            )
    elif source_path.suffix != ".csv":
        raise TypeError(f"{source_path.stem} is not a CSV file.")
    else:
        return source_path


def convert_output(path: str):
    """Convert string to a Path while creating any necessary directories.
    Args:
        path - the source location string
    Returns:
        Path object of the string
    """
    output_path = Path(path)
    if not output_path.exists():
        if output_path.suffix == ".db":
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path.mkdir(parents=True, exist_ok=True)
            output_path = output_path / "output.db"
    return output_path
