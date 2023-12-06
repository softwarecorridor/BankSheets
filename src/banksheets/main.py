import os
from banksheets.institution_parser import decide
from sqlite3 import Connection, Cursor, connect
from banksheets.entry import DataEntry
from banksheets.database import (
    create_sql_connection,
    insert_descriptions,
    insert_potential_transactions,
    save_potential_records,
    clear_potential_records,
    get_duplicate_records,
    mark_duplicates_to_keep,
)
from pathlib import Path


# TODO: rename pass key
# TODO: deal with row_id????????


def parse(file_path: str, file_contents):
    institution = decide(file_path, file_contents)
    if institution:
        return institution.report()


def get_data_from_folder(path) -> list[DataEntry]:
    transactions = []
    for entry in os.scandir(path):
        with open(entry.path) as f:
            data = parse(entry.path, f)
            if data:
                transactions.extend(data)

    return transactions


def write_to_output(transactions, filename):
    arr = transactions.copy()
    arr.sort()

    with open(os.path.join(os.getcwd(), "output", filename), "w") as f:
        for item in arr:
            f.write(f"{str(item)}\n")


def get_dummy_transactions() -> list[DataEntry]:
    return [
        DataEntry("11/11/2022", None, "ONE", "Groceries", 11.11),
        DataEntry("11/12/2022", None, "TWO", "Fun", 11.11),
        DataEntry("11/13/2022", None, "THREE", "Electricity", 11.11),
        DataEntry("11/11/2022", None, "ONE", "Groceries", 11.11),
    ]


def _convert_duplicate_records_to_entries(duplicate: list[tuple]) -> list[DataEntry]:
    return list(map(_convert_duplicate_to_entry, duplicate))


def _convert_duplicate_to_entry(record: tuple):
    return DataEntry(record[0], None, record[1], None, record[2])


def get_duplicate_entries(entries: list[DataEntry]) -> list[DataEntry]:
    uniques = []
    duplicates = set()
    for entry in entries:
        if entry not in uniques:
            uniques.append(entry)
        else:
            duplicates.add(entry)
    return list(duplicates)


def query_user_to_filter_duplicates(entries: DataEntry) -> list[DataEntry]:
    filtered_list = []
    seen_entries = set()
    for item in entries:
        if item in seen_entries:
            if query_user_to_duplicate(item):
                filtered_list.append(item)
        else:
            filtered_list.append(item)
        seen_entries.add(item)
    return filtered_list


def query_user_to_duplicate(entry: DataEntry) -> bool:
    user_input = input(f"Duplicate detects\n\t{entry}\nHit y to keep")
    return user_input == "y"


def main(path: Path):
    sql_conn = create_sql_connection(path)
    # transaction_data = get_data_from_folder("input")

    if sql_conn:
        transaction_data = get_dummy_transactions()
        filtered_transaction_data = query_user_to_filter_duplicates(transaction_data)
        insert_descriptions(filtered_transaction_data, sql_conn)
        insert_potential_transactions(filtered_transaction_data, sql_conn)
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
    path_to_db = Path("output\output.db")
    main(path_to_db)
