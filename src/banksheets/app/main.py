import itertools
from pathlib import Path

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


def _ask_user_for_source() -> Path:
    path = None
    while path is None:
        text = input(
            "Input the path to a file or directory containing bank transactions:"
        )
        temp_path = None
        try:
            temp_path = Path(text)
        except Exception:
            pass
        if temp_path is not None:
            if temp_path.exists():
                path = temp_path
        if path is None:
            print(f'"{text}" is not a file or directory')
    return path


def _get_data(path: Path) -> list[DataEntry]:
    transaction_data = None
    if path.is_dir():
        transaction_data = get_data_from_folder(path)
    else:
        transaction_data = read_file(path)
    return convert_csv_data_to_dataentry(transaction_data)


def _ask_user_for_output() -> Path:
    path = None
    while path is None:
        text = input("Input the path to a file or directory to store the database:")
        temp_path: Path = None
        try:
            temp_path = Path(text)
        except Exception:
            pass
        if temp_path is not None:
            if temp_path.exists():
                if temp_path.is_dir():
                    path = temp_path / "output.db"
                elif temp_path.suffix == ".db":
                    path = temp_path
        if path is None:
            print(f'"{text}" is not a ".db" file or directory')
    return path


def main():
    in_put_data = _ask_user_for_source()
    output_db = _ask_user_for_output()
    transaction_data = _get_data(in_put_data)
    with create_sql_connection(output_db) as db:
        insert_descriptions(transaction_data, db)
        insert_potential_transactions(transaction_data, db)
        query_user(db)
        preserve_potential(db)
        clear_potential(db)


if __name__ == "__main__":
    main()
