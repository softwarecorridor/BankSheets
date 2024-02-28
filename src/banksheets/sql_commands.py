from importlib.resources import files
from pathlib import Path
from sqlite3 import Connection, connect

from banksheets.entry import DataEntry


def create_sql_connection(path: Path):
    connection = None
    resources = files("banksheets.data")
    schema = "schema.sql"
    with open(resources / schema, "r") as fp:
        connection = connect(path)
        connection.executescript(fp.read())
    return connection


def insert_descriptions(
    data_entries: list[DataEntry], sql_connection: Connection
) -> None:
    if data_entries is None:
        raise TypeError()

    to_insert = []
    for datum in data_entries:
        if datum is not None:
            to_insert.append((datum.description,))

    sql_connection.executemany(
        "INSERT OR IGNORE INTO description(name) VALUES (?);", to_insert
    )
    sql_connection.commit()


def insert_potential_transactions(
    data_entries: list[DataEntry], sql_connection: Connection
):
    to_insert = []
    for entry in data_entries:
        if entry is not None:
            to_insert.append(
                (entry.date.strftime("%m/%d/%Y"), entry.amount, entry.description)
            )
    sql_connection.executemany(
        "INSERT OR IGNORE INTO potential_transaction(date, amount, description) VALUES"
        " (?, ?, (SELECT description_id FROM description WHERE name=?));",
        to_insert,
    )
    sql_connection.commit()


def get_duplicate_records(sql_connection: Connection) -> list[tuple]:
    # TODO: return < 100k at once or some big number to prevent issues later
    # TODO: yield instead?
    statement = "SELECT * FROM duplicate_view;"
    cursor = sql_connection.cursor()
    c = cursor.execute(statement)
    return c.fetchall()


def preserve_potential(sql_connection: Connection) -> None:
    statement = (
        "INSERT INTO bank_transaction (date, amount, description) SELECT date, amount,"
        " description FROM potential_transaction;"
    )
    sql_connection.execute(statement)

    statement = "DELETE FROM potential_transaction;"
    sql_connection.execute(statement)
    sql_connection.commit()


def remove_potential(sql_connection: Connection, entries: list[DataEntry]) -> None:
    statement = (
        "SELECT id FROM potential_transaction WHERE date=? AND amount=? AND"
        " description=(SELECT description_id FROM description WHERE name=?) LIMIT 1;"
    )
    cursor = sql_connection.cursor()

    def to_tuple(entry: DataEntry) -> tuple[str]:
        return entry.date.strftime("%m/%d/%Y"), entry.amount, entry.description

    for entry in map(to_tuple, entries):
        c = cursor.execute(statement, entry)
        res = c.fetchone()
        if res is not None and len(res) > 0:
            del_statement = "DELETE FROM potential_transaction WHERE id=?"
            sql_connection.execute(del_statement, res)

        sql_connection.commit()
