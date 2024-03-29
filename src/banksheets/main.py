from pathlib import Path

from banksheets.database import (
    clear_potential_records,
    create_sql_connection,
    get_duplicate_records,
    insert_descriptions,
    insert_potential_transactions,
    mark_duplicates_to_keep,
    save_potential_records,
)
from banksheets.entry import DataEntry
from banksheets.transaction_reader import (
    MissingHeadingMapping,
    NoHeaderException,
    SkipAheadDictReader,
)


def get_data_from_folder(folder: Path) -> list[dict[str, str]]:
    transactions = []
    for file in folder.glob("*.csv"):
        with open(file) as f:
            try:
                reader = SkipAheadDictReader(f)
                transactions.extend(list(reader))
            except NoHeaderException:
                pass
            except MissingHeadingMapping:
                pass

    return transactions


def convert_csv_data_to_dataentry(items: list[dict[str, str]]) -> list[DataEntry]:
    def create(item: dict[str, str]):
        try:
            return DataEntry(**item)
        except ValueError:
            print("weird data")

    converted = map(create, items)
    return list(converted)


def _convert_duplicate_records_to_entries(duplicate: list[tuple]) -> list[DataEntry]:
    return list(map(_convert_duplicate_to_entry, duplicate))


def _convert_duplicate_to_entry(record: tuple):
    return DataEntry(record[0], record[2], record[1], None)


def query_user_to_duplicate(entry: DataEntry) -> bool:
    user_input = input(f"Duplicate detects\n\t{entry}\nHit y to remove")
    return user_input != "y"


def main(path: Path):
    sql_conn = create_sql_connection(path)
    transaction_data = get_data_from_folder(Path.cwd() / "input")
    transaction_data = convert_csv_data_to_dataentry(transaction_data)
    if sql_conn:
        insert_descriptions(transaction_data, sql_conn)
        insert_potential_transactions(transaction_data, sql_conn)
        duplicate_records = get_duplicate_records(sql_conn)
        save_records = []
        if len(duplicate_records) > 0:
            duplicate_entries = _convert_duplicate_records_to_entries(duplicate_records)
            for entry in duplicate_entries:
                should_keep = query_user_to_duplicate(entry)
                if should_keep:
                    save_records.append(entry)

            mark_duplicates_to_keep(save_records, sql_conn)

        save_potential_records(sql_conn)
        clear_potential_records(sql_conn)
    else:
        raise ValueError("No sql connection")


if __name__ == "__main__":
    path_to_db = Path.cwd() / "output" / "output.db"
    main(path_to_db)
