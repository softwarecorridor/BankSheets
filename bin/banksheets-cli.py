import itertools
from pathlib import Path

import click

from banksheets.entry import DataEntry
from banksheets.sql_commands import (
    clear_potential,
    create_sql_connection,
    get_potential_duplicates,
    insert_descriptions,
    insert_potential_transactions,
    preserve_potential,
    remove_potential,
)
from banksheets.transaction_reader import (
    MissingHeadingMapping,
    NoHeaderException,
    SkipAheadDictReader,
)


def get_data_from_folder(folder: Path) -> list[dict[str, str]]:
    transactions = []
    for file in folder.glob("*.csv"):
        transactions.extend(read_file(file))
    return transactions


def read_file(path: Path) -> list[dict[str, str]]:
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
    def create(item: dict[str, str]):
        try:
            return DataEntry(**item)
        except ValueError:
            print("weird data")

    converted = map(create, items)
    return list(converted)


def get_duplicate_groups(db):
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


def query_user(db):
    to_delete_list = []
    for group in get_duplicate_groups(db):
        entry_count = len(group[0])
        is_done = False
        while not is_done:
            val = input(
                f"Duplicated input:\n{group[2]}."
                f"\nAlready present in db: {group[1]}"
                f"\nInput number of new copies to keep (max: {entry_count}):"
            )
            num_to_keep = -1
            try:
                num_to_keep = int(val)
            except ValueError:
                print(f"{val} is not a number")
            if 0 <= num_to_keep <= entry_count:
                num_to_keep = entry_count - num_to_keep
                to_delete_list.extend(group[0][:num_to_keep])
                is_done = True
            else:
                print(f"{num_to_keep} is not in range")

    remove_potential(db, to_delete_list)


def _get_data(path: Path) -> list[DataEntry]:
    transaction_data = None
    if path.is_dir():
        transaction_data = get_data_from_folder(path)
    else:
        transaction_data = read_file(path)
    return convert_csv_data_to_dataentry(transaction_data)


def _check_and_convert_source(path: str) -> None:
    source_path = Path(path)
    if source_path.is_dir():
        csv_files = list(source_path.glob("*.csv"))
        if len(csv_files) == 0:
            raise click.BadParameter("Source directory does not contain any CSV files.")
    elif source_path.suffix != ".csv":
        raise click.BadParameter("File is not a CSV file.")
    else:
        return source_path


def _convert_output(path: str):
    output_path = Path(path)
    if output_path.suffix == ".db":
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
    else:
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / "output.db"


@click.command()
@click.option(
    "--source",
    prompt="Input data source",
    help="Specify the input data source (directory or CSV file)",
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
)
@click.option(
    "--output",
    prompt="Output database",
    help="Specify the output database location (directory or file)",
)
def banksheets(source, output):
    input_src = _check_and_convert_source(source)
    output_src = _convert_output(output)
    transaction_data = _get_data(input_src)
    with create_sql_connection(output_src) as db:
        insert_descriptions(transaction_data, db)
        insert_potential_transactions(transaction_data, db)
        query_user(db)
        preserve_potential(db)
        clear_potential(db)


if __name__ == "__main__":
    banksheets()
