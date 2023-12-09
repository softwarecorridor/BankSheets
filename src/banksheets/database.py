from sqlite3 import Connection, Cursor, connect
from banksheets.entry import DataEntry
from pathlib import Path


# TODO: make sure that we are using the correct key
# TODO: use import resources instead of path
def create_sql_connection(path: Path):
    connection = None
    with open("data\schema.sql") as fp:
        connection = connect(path)
        connection.executescript(fp.read())
    return connection


def insert_descriptions(data_entries: list[DataEntry], sql_connection: Connection):
    to_insert = []
    for datum in data_entries:
        to_insert.append((datum.description,))

    sql_connection.executemany(
        "INSERT OR IGNORE INTO description(name) VALUES (?);", to_insert
    )
    sql_connection.commit()


def insert_potential_transactions(data_entries, sql_connection: Connection):
    to_insert = []
    for datum in data_entries:
        desc_id_query = sql_connection.execute(
            "SELECT description_id FROM description WHERE name=?", (datum.description,)
        )
        query_result = desc_id_query.fetchone()
        if query_result:
            to_insert.append(
                (datum.date.strftime("%m/%d/%Y"), datum.amount, query_result[0])
            )
    sql_connection.executemany(
        "INSERT OR IGNORE INTO potential_transaction(date, amount, description, preserve ) VALUES (?, ?, ?, 0);",
        to_insert,
    )
    sql_connection.commit()

    # TODO: do this as one query?
    _preserve_non_duplicate_transactions(sql_connection)


def _preserve_non_duplicate_transactions(sql_connection: Connection) -> None:
    statement = "UPDATE potential_transaction SET preserve = 1 WHERE NOT EXISTS (SELECT 1 FROM duplicate_transaction WHERE duplicate_transaction.potential_date = potential_transaction.date AND duplicate_transaction.potential_amount = potential_transaction.amount AND duplicate_transaction.potential_description = potential_transaction.description);"
    sql_connection.execute(statement)
    sql_connection.commit()


def save_potential_records(sql_connection: Connection) -> None:
    statement = "INSERT INTO bank_transaction (date, amount, description) SELECT date, amount, description FROM potential_transaction WHERE preserve=1;"
    sql_connection.execute(statement)
    sql_connection.commit()


def clear_potential_records(sql_connection: Connection) -> None:
    statement = "DELETE FROM potential_transaction"
    sql_connection.execute(statement)
    sql_connection.commit()


def get_duplicate_records(sql_connection: Connection) -> list[tuple]:
    # TODO: return < 100k at once or some big number to prevent issues later
    # TODO: yield instead?
    statement = "SELECT potential_date, potential_description, potential_amount FROM duplicate_transaction;"
    cursor = sql_connection.cursor()
    c = cursor.execute(statement)
    return c.fetchall()


def mark_duplicates_to_keep(
    entries: list[DataEntry], sql_connection: Connection
) -> None:
    """Mark the ones the user selected as to be passed"""

    def get_record(item: DataEntry):
        return (item.date.strftime("%m/%d/%Y"), item.description, item.amount)

    # TODO: might want to only preserve 1x duplicate when nx are present?
    mark_statement = "UPDATE potential_transaction SET preserve = 1 WHERE date = ? AND description = ? AND amount = ?;"
    records = list(map(get_record, entries))
    sql_connection.executemany(mark_statement, records)
    sql_connection.commit()
