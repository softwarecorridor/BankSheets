from importlib.resources import files
from pathlib import Path
from sqlite3 import Connection, connect
from typing import Optional

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
        "INSERT OR IGNORE INTO potential_transaction(date, amount, description_id)"
        " VALUES (?, ?, (SELECT id FROM description WHERE name=?));",
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


def get_potential_duplicates(sql_connection: Connection) -> list[tuple]:
    statement = """

SELECT pt.id, date, amount, name, description_id,
    (SELECT COUNT(*)
     FROM bank_transaction bt
     WHERE bt.date = pt.date
       AND bt.amount = pt.amount
       AND bt.description_id = pt.description_id) AS bank_count
FROM potential_transaction pt
join description d on d.id=pt.description_id
WHERE (
    (date, amount, description_id) IN (
    SELECT date, amount, description_id
    FROM potential_transaction
    GROUP BY date, amount, description_id
    HAVING COUNT(*) > 1)
    OR EXISTS (
        SELECT 1
        FROM bank_transaction bt
        WHERE bt.date = pt.date
          AND bt.amount = pt.amount
          AND bt.description_id = pt.description_id
    )
)
ORDER BY date, amount
"""
    cursor = sql_connection.cursor()
    c = cursor.execute(statement)
    return c.fetchall()


def preserve_potential(sql_connection: Connection) -> None:
    statement = (
        "INSERT INTO bank_transaction (date, amount, description_id) SELECT date,"
        " amount, description_id FROM potential_transaction;"
    )
    sql_connection.execute(statement)
    sql_connection.commit()


def clear_potential(sql_connection: Connection) -> None:
    statement = "DELETE FROM potential_transaction;"
    sql_connection.execute(statement)


def remove_potential(sql_connection: Connection, entries: list[int]) -> None:
    cursor = sql_connection.cursor()
    placeholders = ",".join("?" * len(entries))  # Create a placeholder for each ID
    del_statement = f"DELETE FROM potential_transaction WHERE id IN ({placeholders})"
    cursor.execute(del_statement, tuple(entries))
    sql_connection.commit()


def get_descriptions_missing_alias(sql_connection: Connection) -> list[tuple[str]]:
    cursor = sql_connection.cursor()
    statement = (
        "SELECT name FROM description WHERE id NOT IN (SELECT description_id"
        " FROM description_alias);"
    )

    cursor.execute(statement)
    return cursor.fetchall()


def get_description_id_by_name(sql_connection: Connection, name: str) -> int:
    cursor = sql_connection.cursor()
    statement = "SELECT id from description WHERE name=?"

    cursor.execute(statement, (name,))
    return cursor.fetchone()


def get_description_id_by_name_like(
    sql_connection: Connection, pattern: str
) -> list[int]:
    cursor = sql_connection.cursor()
    statement = "SELECT id from description WHERE name LIKE ?"

    cursor.execute(statement, (pattern,))
    return cursor.fetchall()


def insert_alias(sql_connection: Connection, id_list: list[int], alias_name: str):
    statement = (
        "INSERT OR IGNORE INTO description_alias(description_id, name) VALUES (?, ?);"
    )
    data = [(id, alias_name) for id in id_list]

    sql_connection.executemany(statement, data)
    sql_connection.commit()


def replace_alias(sql_connection: Connection, id_list: list[int], alias_name: str):
    statement = (
        "INSERT OR REPLACE INTO description_alias(description_id, name) VALUES (?, ?);"
    )
    data = [(id, alias_name) for id in id_list]

    sql_connection.executemany(statement, data)
    sql_connection.commit()


def search(
    sql_connection: Connection,
    start_date: Optional[str],
    end_date: Optional[str],
    filter: Optional[str],
):
    cursor = sql_connection.cursor()
    statement = """
SELECT
    bt.date AS transaction_date,
    bt.amount AS transaction_amount,
    COALESCE(da.name, d.name) AS transaction_description
FROM
    bank_transaction bt
LEFT JOIN
    description d ON bt.description_id = d.id
LEFT JOIN
    description_alias da ON bt.description_id = da.description_id
"""
    conditions = []
    parameters = []

    if start_date:
        conditions.append("bt.date >= ?")
        parameters.append(start_date)

    if end_date:
        conditions.append("bt.date <= ?")
        parameters.append(end_date)

    if filter:
        conditions.append("(d.name = ? OR da.name = ?)")
        parameters.extend([filter, filter])

    if conditions:
        statement += "WHERE " + " AND ".join(conditions)

    # Add the ORDER BY clause
    statement += " ORDER BY bt.date ASC;"
    cursor.execute(statement, parameters)
    return cursor.fetchall()
